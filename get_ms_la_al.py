from get_cleaned_hpsa import hpsa

# Keep only the rows that are from Mississippi, Louisiana, or Alabama and store in shpsa dataframe (i.e. South HPSAs)
top_three = ['Mississippi', 'Louisiana', 'Alabama']
shpsa = hpsa[hpsa['Common State Name'].isin(top_three)]

# Get the sample size for HPSA-designated counties (by county FIPS code)
county_n = shpsa['Common State County FIPS Code'].value_counts()

# Get the FIPS codes of those counties with two rows in shpsa
multiple_fips = county_n[county_n > 1].index

# Iterate through each county in multiple_fips, dropping the Proposed For Withdrawal row from shpsa
for county in multiple_fips:
    county_rows = shpsa[shpsa['Common State County FIPS Code'] == county]
    proposed_withdrawal_row = county_rows[county_rows['HPSA Status'] == 'Proposed For Withdrawal']
    shpsa = shpsa.drop(index = proposed_withdrawal_row.index)
    
