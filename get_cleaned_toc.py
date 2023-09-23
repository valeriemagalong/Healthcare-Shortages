import pandas as pd
import addfips as af
from uszipcode import SearchEngine
from get_cleaned_cms import cms
from get_ms_la_al import shpsa

# Create a list called files for the string paths to the raw data
files = ['raw_data/2016_Timely and Effective Care - Hospital.csv', 'raw_data/2017_Timely and Effective Care - Hospital.csv',
         'raw_data/2018_Timely and Effective Care - Hospital.csv', 'raw_data/2019_Timely and Effective Care - Hospital.csv',
         'raw_data/2020_Timely_and_Effective_Care-Hospital.csv', 'raw_data/2021_Timely_and_Effective_Care-Hospital.csv',
         'raw_data/2022_Timely_and_Effective_Care-Hospital.csv', 'raw_data/2023_Timely_and_Effective_Care-Hospital.csv']

# Create an empty list called dfs to hold the dataframes, then read the .csvs and append to dfs
dfs = []
for file in files:
    dfs.append(pd.read_csv(file, encoding = 'iso-8859-1'))

# Union all dataframes in dfs into one dataframe called toc
toc = pd.concat(dfs, ignore_index = True)

# Identify columns to be dropped
cols_to_drop = ['Address', 'Phone Number', 'Footnote', 'Start Date', 'End Date']

toc = toc.drop(columns = cols_to_drop)

# Replace state abbrevations in State column with actual state names for states of interest
state_mapping = {
    'AL': 'Alabama',
    'LA': 'Louisiana',
    'MS': 'Mississippi'
}

toc['State'] = toc['State'].replace(state_mapping)

# Get the unique ZIP codes in the toc dataframe
zips = toc['ZIP Code'].unique()

# Convert zips to a list of string ZIP codes (because uszipcode library searches based on a string)
zips = zips.astype(str).tolist()

# Create a search engine
search = SearchEngine()

# Create empty dictionary to store the state, county, latitude, & longitude for each ZIP code
zip_map = {}

# Look up each ZIP code, and if that ZIP is in the uszipcode database, add relevant info to zip_map
for zip_code in zips:
    info = search.by_zipcode(zip_code)
    if info:
        zip_map[zip_code] = {
            'State': info.state,
            'County': info.county,
            'Latitude': info.lat,
            'Longitude': info.lng
        }
        
# Initialize AddFIPS object called fips_tool
fips_tool = af.AddFIPS()

# For each ZIP code in zip_map, get the county FIPS code
for zip_code in zip_map:
    county = zip_map[zip_code]['County']
    state = zip_map[zip_code]['State']
    county_fips = fips_tool.get_county_fips(county, state)
    # Add the FIPS code to that ZIP code's dictionary in zip_map
    zip_map[zip_code]['Common State County FIPS Code'] = county_fips
    
# Define a function called lookup that retrieves a value associated with a specific key for each ZIP code in zip_map
def lookup(zip_code, key):
    return zip_map[zip_code][key]

# Define the keys that will be added as columns to cms
keys = ['County', 'Common State County FIPS Code', 'Latitude', 'Longitude']

# For each key, create a new column in cms, & use the apply method to store the evaluated result of lookup() as the column values
for key in keys:
    toc[key] = toc['ZIP Code'].apply(lambda x: lookup(str(x), key))

# Define measures of interest
measures_to_keep = ['OP_4', 'OP_18b', 'OP_20', 'OP_21', 'OP_22', 'ED_2b']

# Drop irrelevant rows
toc = toc[toc['Measure ID'].isin(measures_to_keep)]

# Replace measure strings in Measure Name column with more intuitive names
measure_mapping = {
    'OP 18': 'Median Time Spent in ED Before Leaving',
    'Door to diagnostic eval': 'Median Time Spent in ED Before Seen by Health Professional',
    'Median time to pain med': 'Median Time to Pain Medicine',
    'Left before being seen': '% of Patients Left Before Being Seen',
    'Aspirin at Arrival': 'Median Time to Pain Medicine',
    'Average (median) time patients spent in the emergency department before leaving from the visit A lower number of minutes is better': 'Median Time Spent in ED Before Leaving',
    'ED2': 'Median Admit Decision Time to ED Departure Time As Inpatient',
    'Average (median) time patients spent in the emergency department, after the doctor decided to admit them as an inpatient before leaving the emergency department for their inpatient room A lower number of minutes is better': 'Median Admit Decision Time to ED Departure Time As Inpatient'
}

toc['Measure Name'] = toc['Measure Name'].replace(measure_mapping)

# Drop rows where Score is Not Available
toc = toc[toc['Score'] != 'Not Available']

# Change the datatype to float
toc['Score'] = toc['Score'].astype('float')

# Convert all values in Facility ID column to string datatype
toc['Facility ID'] = toc['Facility ID'].astype(str)

# Define the hospital type of interest
acute_types = ['Acute Care Hospitals', 'Acute Care - Veterans Administration', 'Acute Care - Department of Defense']

# Subset the cms dataframe, keeping only rows from acute care hospitals
acms = cms[cms['Hospital Type'].isin(acute_types)]

acute_facilities = acms['Facility ID'].unique()

# Only keep the rows in toc from acute care facilities
toc = toc[toc['Facility ID'].isin(acute_facilities)]

# Add a column to toc dataframe for Hospital Ownership
for index, row in toc.iterrows():
    facility_id = row['Facility ID']
    matching_row = acms.loc[acms['Facility ID'] == facility_id]
    toc.at[index, 'Hospital Ownership'] = matching_row['Hospital Ownership'].values[0]

# Drop all states except Alabama, Mississippi, & Louisiana
states = ['Alabama', 'Mississippi', 'Louisiana']

toc = toc[toc['State'].isin(states)]

# Get HPSA-designated counties from shpsa dataframe
hpsa_counties = pd.Series(shpsa['Common State County FIPS Code'].unique())

# Create a column County HPSA Status in the toc dataframe with default values of Non-Shortage Area
toc['County HPSA Status'] = 'Non-Shortage Area'

# Update the County HPSA Status to Shortage Area for hospitals in shortage areas
toc.loc[toc['Common State County FIPS Code'].isin(hpsa_counties), 'County HPSA Status'] = 'Shortage Area'

# Identify columns of interest from shpsa, then left join cms with shpsa based on county FIPS code
join_cols = ['Common State County FIPS Code', 'Designation Type', 'HPSA Score', 'HPSA FTE',
             'HPSA Designation Population', '% of Population Below 100% Poverty', 'HPSA Formal Ratio',
             'Rural Status', 'HPSA Provider Ratio Goal', 'HPSA Shortage']

toc = toc.merge(shpsa[join_cols], on = 'Common State County FIPS Code', how = 'left')

# Import data from AHRQ into dataframe called ahrq
ahrq = pd.read_excel('raw_data/chsp-compendium-2021.xlsx')

# Only keep rows from MS, AL, & LA
ahrq = ahrq[ahrq['health_sys_state'].isin(['MS', 'AL', 'LA'])]

# Create hospital mapping, where key is the Facility Name from toc, and value is the corresponding health_sys_name from ahrq
# Mapping was validated by eye using Excel, checking that the was a match in health system city in AHRQ and CMS .csv files
hosp_mapping = {
    'DCH REGIONAL MEDICAL CENTER': 'DCH Health System',
    'EAST ALABAMA MEDICAL CENTER': 'East Alabama Medical Center',
    'HUNTSVILLE HOSPITAL': 'Huntsville Hospital Health System',
    'MOBILE INFIRMARY MEDICAL CENTER': 'Infirmary Health System',
    'SOUTHEAST HEALTH MEDICAL CENTER': 'Southeast Health',
    'UAB CALLAHAN EYE HOSPITAL AUTHORITY': 'UAB Health System',
    'UNIVERSITY OF SOUTH ALABAMA MEDICAL CENTER': 'University of South Alabama Hospitals',
    'BATON ROUGE GENERAL MEDICAL CENTER': 'Baton Rouge General Health System',
    'OUR LADY OF THE LAKE REGIONAL MEDICAL CENTER': 'Franciscan Missionaries of Our Lady Health System',
    'UNIVERSITY MEDICAL CENTER NEW ORLEANS': 'LCMC Health System',
    'TOURO INFIRMARY': 'LCMC Health System',
    'NEW ORLEANS EAST HOSPITAL': 'LCMC Health System',
    'LAKE CHARLES MEMORIAL HOSPITAL': 'Lake Charles Memorial Health System',
    'NORTH OAKS MEDICAL CENTER, L L C': 'North Oaks Health System',
    'OCHSNER CLINIC FOUNDATION': 'Ochsner Health System',
    'OCHSNER MEDICAL CENTER': 'Ochsner Health System',
    'OCHSNER MEDICAL CENTER - BATON ROUGE': 'Ochsner Health System',
    'OCHSNER MEDICAL CENTER - NORTHSHORE, L L C': 'Ochsner Health System',
    'OCHSNER MEDICAL CENTER KENNER': 'Ochsner Health System',
    'OCHSNER LSU HEALTH MONROE': 'Ochsner Health System',
    'OCHSNER LSU HEALTH SHREVEPORT': 'Ochsner Health System',
    'OCHSNER ST MARY': 'Ochsner Health System',
    'OCHSNER LAFAYETTE GENERAL MEDICAL CENTER': 'Ochsner Health System',
    'OCHSNER UNIVERSITY HOSPITAL AND CLINICS': 'Ochsner Health System',
    'OCHSNER AMERICAN LEGION HOSPITAL': 'Ochsner Health System',
    'SLIDELL MEMORIAL HOSPITAL': 'Slidell Memorial Hospital',
    'WILLIS KNIGHTON MEDICAL CENTER': 'Willis Knighton Health System',
    'WILLIS KNIGHTON MEDICAL CENTER, INC': 'Willis Knighton Health System',
    'ANDERSON REGIONAL MEDICAL CENTER': 'Anderson Regional Health System',
    'ANDERSON REGIONAL MEDICAL CTR': 'Anderson Regional Health System',
    'DELTA HEALTH-NORTHWEST REGIONAL': 'Delta Health System',
    'DELTA HEALTH- THE MEDICAL CENTER': 'Delta Health System',
    'DELTA HEALTH SYSTEM - THE MEDICAL CENTER': 'Delta Health System',
    'DELTA HEALTH - HIGHLAND  HILLS': 'Delta Health System',
    'FORREST GENERAL HOSPITAL': 'Forrest Health',
    'MARION GENERAL HOSPITAL': 'Forrest Health',
    'MEMORIAL HOSPITAL AT GULFPORT': 'Memorial Hospital at Gulfport',
    'NORTH MISSISSIPPI MEDICAL CENTER': 'North Mississippi Health Services',
    'NORTH MISSISSIPPI MEDICAL CENTER-WEST POINT': 'North Mississippi Health Services',
    'OCHSNER RUSH HOSPITAL': 'Rush Health Systems',
    'RUSH FOUNDATION HOSPITAL': 'Rush Health Systems',
    'SINGING RIVER HEALTH SYSTEM': 'Singing River Health System',
    'SINGING RIVER GULFPORT': 'Singing River Health System',
    'SINGING RIVER HOSPITAL': 'Singing River Health System',
    'UNIVERSITY OF MISSISSIPPI MEDICAL CENTER- GRENADA': 'The University of Mississippi Medical Center',
    'UNIVERSITY OF MISSISSIPPI MED CENTER': 'The University of Mississippi Medical Center',
    'SOUTH CENTRAL REG MED CTR': 'South Central Regional Medical Center Health System'
}

# Define columns in ahrq that I want to keep (keys), and map to final column name (values)
ahrq_cols = {
    'total_mds': 'Total MDs in System',
    'prim_care_mds': 'Total Primary Care MDs in System',
    'hosp_cnt': 'Total Hospitals in System',
    'acutehosp_cnt': 'Total Acute Care Hospitals in System',
    'sys_beds': 'Total Beds in System',
    'sys_res': 'Total Residents in System'
}

# Iterate through each Facility Name in toc dataframe, and append new columns from ahrq if there is a match in hosp_mapping
for col in ahrq_cols.keys():
    for i in toc.index:
        facility = toc.loc[i, 'Facility Name']  # Accessing 'Facility Name' column in 'toc'
        if facility in hosp_mapping:
            matching_health_sys = ahrq.loc[ahrq['health_sys_name'] == hosp_mapping[facility], col]
            toc.at[i, ahrq_cols[col]] = matching_health_sys.values[0] if not matching_health_sys.empty else None
            
