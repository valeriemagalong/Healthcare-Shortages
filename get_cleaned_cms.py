import pandas as pd
import addfips as af
from uszipcode import SearchEngine
from get_ms_la_al import shpsa

# Create a list called files for the string paths to the raw data
files = ['raw_data/2016_Hospital_General_Information.csv', 'raw_data/2017_Hospital_General_Information.csv',
         'raw_data/2018_Hospital_General_Information.csv', 'raw_data/2019_Hospital_General_Information.csv',
         'raw_data/2020_Hospital_General_Information.csv', 'raw_data/2021_Hospital_General_Information.csv',
         'raw_data/2022_Hospital_General_Information.csv', 'raw_data/2023_Hospital_General_Information.csv']

# Create an empty list called dfs to hold the dataframes, then read the .csvs and append to dfs
dfs = []
for file in files:
    dfs.append(pd.read_csv(file, encoding = 'iso-8859-1'))

# Union all dataframes in dfs into one dataframe called cms
cms = pd.concat(dfs, ignore_index = True)

# Identify columns to be dropped
cols_to_drop = ['Address', 'County Name', 'Phone Number', 'Hospital overall rating footnote',
                'Mortality national comparison footnote', 'Safety of care national comparison footnote',
                'Readmission national comparison footnote', 'Patient experience national comparison footnote',
                'Effectiveness of care national comparison footnote', 'Timeliness of care national comparison footnote',
                'Efficient use of medical imaging national comparison footnote', 'MORT Group Footnote',
                'Safety Group Footnote', 'READM Group Footnote', 'Pt Exp Group Footnote', 'TE Group Footnote']

cms = cms.drop(columns = cols_to_drop)

# Drop all rows excepts those from MS, LA, & AL
states = ['MS', 'LA', 'AL']

cms = cms[cms['State'].isin(states)]

# Replace state abbrevations in State column with actual state names
state_mapping = {
    'AL': 'Alabama',
    'LA': 'Louisiana',
    'MS': 'Mississippi'
}

cms['State'] = cms['State'].replace(state_mapping)

# Get the unique ZIP codes in the cms dataframe
zips = cms['ZIP Code'].unique()

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
    cms[key] = cms['ZIP Code'].apply(lambda x: lookup(str(x), key))

# Replace 'Not Available' values with NaN
cms['Hospital overall rating'] = cms['Hospital overall rating'].replace('Not Available', pd.NA)

# Change the datatype to Int64 (use Int64 instead of int since there are NaNs)
cms['Hospital overall rating'] = cms['Hospital overall rating'].astype('Int64')

# Get HPSA-designated counties from shpsa dataframe
hpsa_counties = pd.Series(shpsa['Common State County FIPS Code'].unique())

# Create a column County HPSA Status in the cms dataframe with default values of Non-Shortage Area
cms['County HPSA Status'] = 'Non-Shortage Area'

# Update the County HPSA Status to Shortage Area for hospitals in shortage areas
cms.loc[cms['Common State County FIPS Code'].isin(hpsa_counties), 'County HPSA Status'] = 'Shortage Area'

# Identify columns of interest from shpsa, then left join cms with shpsa based on county FIPS code
join_cols = ['Common State County FIPS Code', 'Designation Type', 'HPSA Score', 'HPSA FTE',
             'HPSA Designation Population', '% of Population Below 100% Poverty', 'HPSA Formal Ratio',
             'Rural Status', 'HPSA Provider Ratio Goal', 'HPSA Shortage']

cms = cms.merge(shpsa[join_cols], on = 'Common State County FIPS Code', how = 'left')

