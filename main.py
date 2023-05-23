import pandas as pd

#### Upload PPV Offers ####
ppv_offers = pd.read_csv(r'C:\Users\3590080\OneDrive - Jabil\Desktop\Weekly Offers.csv')
# Determine the last two rows
last_two_rows = ppv_offers.iloc[-2:, :]
# Drop the last two rows
ppv_offers = ppv_offers.drop(ppv_offers.index[-2:])
# Make columns upper case
ppv_offers['Offer MPN'] = ppv_offers['Offer MPN'].str.upper()
ppv_offers['STD MPN'] = ppv_offers['STD MPN'].str.upper()
ppv_offers['Offer JPN'] = ppv_offers['Offer JPN'].str.upper()
ppv_offers['STD JPN'] = ppv_offers['STD JPN'].str.upper()
ppv_offers['JPN'] = ppv_offers['JPN'].str.upper()
ppv_offers['Site'] = ppv_offers['Site'].str.upper()
ppv_offers['Offer Site'] = ppv_offers['Offer Site'].str.upper()
ppv_offers['STD Site'] = ppv_offers['STD Site'].str.upper()
ppv_offers['FinalKey'] = ppv_offers['FinalKey'].str.upper()
# Delete PPV Offer rows where JPN != JPN
ppv_offers = ppv_offers[ppv_offers['Offer JPN'] == ppv_offers['STD JPN']]
# Delete PPV Offer rows where MPN != MPN
ppv_offers = ppv_offers[ppv_offers['Offer MPN'] == ppv_offers['STD MPN']]
# Delete PPV Offer rows where Site != Site
ppv_offers = ppv_offers[ppv_offers['Offer Site'] == ppv_offers['STD Site']]


#### Upload SAT Quotes ####
sat_quotes = pd.read_csv(r'C:\Users\3590080\OneDrive - Jabil\Desktop\SAT Quotes.csv')
# Determine the last two rows
last_two_rows = sat_quotes.iloc[-2:, :]
# Drop the last two rows
sat_quotes = sat_quotes.drop(sat_quotes.index[-2:])
# Make columns upper case
sat_quotes['FinalKey'] = sat_quotes['FinalKey'].str.upper()


#### Upload Open Orders ####
open_orders = pd.read_csv(r'C:\Users\3590080\OneDrive - Jabil\Desktop\Open Orders.csv')
# Make sure that 'POCreateDate' is a datetime object
open_orders['POCreateDate'] = pd.to_datetime(open_orders['POCreateDate'])
# Sort the DataFrame by 'POCreateDate' in descending order (most recent first)
open_orders = open_orders.sort_values('POCreateDate', ascending=False)
# Drop duplicates based on 'FinalKey', keeping the first occurrence (which is the most recent due to the sorting)
open_orders = open_orders.drop_duplicates(subset='FinalKey', keep='first')
# Drop the last two rows
last_two_rows = open_orders.iloc[-2:, :]
open_orders = open_orders.drop(open_orders.index[-2:])
# Make columns upper case
open_orders['FinalKey'] = open_orders['FinalKey'].str.upper()

# Merge ppv_offers with sat_quotes on 'FinalKey' using a left join
merged_data = ppv_offers.merge(sat_quotes, on='FinalKey', how='left')

# Merge the merged_data with open_orders on 'FinalKey' using a left join
merged_data = merged_data.merge(open_orders, on='FinalKey', how='left
