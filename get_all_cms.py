import pandas as pd

# Create a list called files for the string paths to the raw data
files = ['raw_data/2016_Hospital_General_Information.csv', 'raw_data/2017_Hospital_General_Information.csv',
         'raw_data/2018_Hospital_General_Information.csv', 'raw_data/2019_Hospital_General_Information.csv',
         'raw_data/2020_Hospital_General_Information.csv', 'raw_data/2021_Hospital_General_Information.csv',
         'raw_data/2022_Hospital_General_Information.csv', 'raw_data/2023_Hospital_General_Information.csv']

# Create an empty list called dfs to hold the dataframes, then read the .csvs and append to dfs
dfs = []
for file in files:
    dfs.append(pd.read_csv(file, encoding = 'iso-8859-1'))

# Union all dataframes in dfs into one dataframe called all_cms
all_cms = pd.concat(dfs, ignore_index = True)

# Identify columns to be dropped
cols_to_drop = ['Address', 'County Name', 'Phone Number', 'Hospital overall rating footnote',
                'Mortality national comparison footnote', 'Safety of care national comparison footnote',
                'Readmission national comparison footnote', 'Patient experience national comparison footnote',
                'Effectiveness of care national comparison footnote', 'Timeliness of care national comparison footnote',
                'Efficient use of medical imaging national comparison footnote', 'MORT Group Footnote',
                'Safety Group Footnote', 'READM Group Footnote', 'Pt Exp Group Footnote', 'TE Group Footnote']

all_cms = all_cms.drop(columns = cols_to_drop)

# Replace 'Not Available' values with NaN
all_cms['Hospital overall rating'] = all_cms['Hospital overall rating'].replace('Not Available', pd.NA)

# Change the datatype to Int64 (use Int64 instead of int since there are NaNs)
all_cms['Hospital overall rating'] = all_cms['Hospital overall rating'].astype('Int64')

# Convert all values in Facility ID column to string datatype
all_cms['Facility ID'] = all_cms['Facility ID'].astype(str)

# cms.to_csv('cleaned_data/all_states_cms.csv', index = False)

