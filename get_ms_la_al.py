from get_cleaned_hpsa import hpsa

# Keep only the rows that are from Mississippi, Louisiana, or Alabama and store in shpsa dataframe (i.e. South HPSAs)
top_three = ['Mississippi', 'Louisiana', 'Alabama']
shpsa = hpsa[hpsa['Common State Name'].isin(top_three)]
