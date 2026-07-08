import pandas as pd

sold = pd.read_csv(r"D:\Data&Documents\Berkeley\Internship\IDX Exchange\IDX_Codes\Sold_Concated.csv", low_memory=False, encoding = 'latin1')
listings = pd.read_csv(r"D:\Data&Documents\Berkeley\Internship\IDX Exchange\IDX_Codes\Listing_Concated.csv", low_memory=False, encoding = 'latin1')

print('Unfiltered row count of Sold is '+ str(sold.shape[0]))
print('Unfiltered row count of Listings is '+ str(listings.shape[0]))


fi_sold = sold[sold['PropertyType'] == 'Residential']
fi_listings = listings[listings['PropertyType'] == 'Residential']

print('Filtered row count of Sold is '+ str(fi_sold.shape[0]))
print('Filtered row count of Listings is '+ str(fi_listings.shape[0]))

# Result:
# Unfiltered row count of Sold is 639941
# Unfiltered row count of Listings is 929339
# Filtered row count of Sold is 430462
# Filtered row count of Listings is 591332
