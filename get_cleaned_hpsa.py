import pandas as pd

# Import data as hpsa
hpsa = pd.read_excel('raw_data/BCD_HPSA_FCT_DET_PC.xlsx')

# Keep only the rows that are of the Geographic Population type
hpsa = hpsa[hpsa['HPSA Population Type'] == 'Geographic Population']

# Keep only the rows that have a status of Designated or Proposed For Withdrawal
hpsa = hpsa[hpsa['HPSA Status'] != 'Withdrawn']

# Keep only the rows that have a component type of Single County
hpsa = hpsa[hpsa['HPSA Component Type Description'] == 'Single County']

# Exclude rows that are NOT the 50 US states (i.e. exclude US territories & insular areas)
excluded = ['Federated States of Micronesia', 'American Samoa', 'Northern Mariana Islands', 'U.S. Virgin Islands',
            'Marshall Islands', 'Republic of Palau']

hpsa = hpsa[~hpsa['Common State Name'].isin(excluded)]

# Drop unnecessary columns
cols_to_drop = ['HPSA ID', 'HPSA Discipline Class', 'PC MCTA Score', 'Primary State Abbreviation', 'Metropolitan Indicator',
                'HPSA Geography Identification Number', 'HPSA Degree of Shortage', 'Withdrawn Date', 'HPSA Population Type',
                'Longitude', 'Latitude', 'BHCMIS Organization Identification Number', 'Break in Designation', 'Common Postal Code',
                'Common State FIPS Code', 'County or County Equivalent Federal Information Processing Standard Code',
                'Discipline Class Number', 'HPSA Address', 'HPSA Component Name', 'HPSA Component Source Identification Number',
                'HPSA Component State Abbreviation', 'HPSA Component Type Code', 'HPSA Component Type Description',
                'HPSA Designation Population Type Description', 'HPSA Metropolitan Indicator Code', 'HPSA Population Type Code',
                'HPSA Postal Code', 'HPSA Resident Civilian Population', 'HPSA Status Code', 'HPSA Type Code', 'HPSA City',
                'HPSA Withdrawn Date String', 'Primary State FIPS Code', 'Primary State Name', 'Provider Type', 'Rural Status Code',
                'State Abbreviation', 'State and County Federal Information Processing Standard Code', 'State FIPS Code',
                'State Name', 'U.S. - Mexico Border 100 Kilometer Indicator', 'U.S. - Mexico Border County Indicator',
                'Data Warehouse Record Create Date', 'Data Warehouse Record Create Date Text']

hpsa = hpsa.drop(columns = cols_to_drop)

