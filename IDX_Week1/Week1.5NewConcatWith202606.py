
import numpy as np
import pandas as pd
import math


monthList = ['202401','202402','202403','202404','202405','202406','202407','202408',
             '202409','202410','202411','202412','202501','202502','202503','202504',
             '202505','202506','202507','202508','202509','202510','202511','202512',
             '202601','202602','202603','202604']
soldName = 'CRMLSSold'
listingName = 'CRMLSListing'
location = r'D:\Data&Documents\Berkeley\Internship\IDX Exchange\IDX_raw_data\\'

print(location + soldName + monthList[0])

sold1 = pd.read_csv("D:/Data&Documents/Berkeley/Internship/IDX Exchange/Sold_concated.csv", encoding='latin-1', low_memory=False)
sold2 = pd.read_csv("D:\Data&Documents\Berkeley\Internship\IDX Exchange\IDX_Codes\IDX_NewDataPulling\CRMLSSold202606.csv", encoding='latin-1', low_memory=False)
sold = pd.concat([sold1, sold2])
list1 = pd.read_csv("D:/Data&Documents/Berkeley/Internship/IDX Exchange/Listing_concated.csv", encoding='latin-1', low_memory=False)
list2 = pd.read_csv("D:\Data&Documents\Berkeley\Internship\IDX Exchange\IDX_Codes\IDX_NewDataPulling\CRMLSListing202606.csv", encoding='latin-1', low_memory=False)
listing = pd.concat([list1, list2])

sold.to_csv('Sold_Concated.csv',index = False, encoding='latin-1')
listing.to_csv('Listing_Concated.csv', index = False, encoding='latin-1')