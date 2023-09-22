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

