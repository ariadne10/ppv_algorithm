import streamlit as st
import pandas as pd

# Display a file uploader widget in your app for each Excel file
ppv_offers_file = st.file_uploader("Upload PPV Offers Excel", type=['xlsx'])
sat_quotes_file = st.file_uploader("Upload SAT Quotes Excel", type=['xlsx'])
open_orders_file = st.file_uploader("Upload Open Orders Excel", type=['xlsx'])

if ppv_offers_file and sat_quotes_file and open_orders_file:
    # Use pandas to read the Excel data
    ppv_offers = pd.read_excel(ppv_offers_file)
    sat_quotes = pd.read_excel(sat_quotes_file)
    open_orders = pd.read_excel(open_orders_file)

    # Preprocessing and merging code here

    # PPV Offers
    ppv_offers = ppv_offers.iloc[:-2, :]
    ppv_offers = ppv_offers.apply(lambda x: x.str.upper() if x.dtype == 'object' else x)
    ppv_offers = ppv_offers[
        (ppv_offers['Offer JPN'] == ppv_offers['STD JPN']) &
        (ppv_offers['Offer MPN'] == ppv_offers['STD MPN']) &
        (ppv_offers['Offer Site'] == ppv_offers['STD Site'])
    ]

    # SAT Quotes
    sat_quotes = sat_quotes.iloc[:-2, :]
    sat_quotes['FinalKey'] = sat_quotes['FinalKey'].str.upper()

    # Open Orders
    open_orders['POCreateDate'] = pd.to_datetime(open_orders['POCreateDate'])
    open_orders = open_orders.sort_values('POCreateDate', ascending=False).drop_duplicates(subset='FinalKey', keep='first')
    open_orders = open_orders.iloc[:-2, :]
    open_orders['FinalKey'] = open_orders['FinalKey'].str.upper()

    # Merging
    merged_data = ppv_offers.merge(sat_quotes, on='FinalKey', how='left')
    merged_data = merged_data.merge(open_orders, on='FinalKey', how='left')

    # Drop specified columns
    merged_data = merged_data.drop(columns=['FinalKey', 'Offer Site', 'STD Site', 'Offer JPN', 'STD JPN', 'STD MPN'])

    # Write the DataFrame to the screen
    st.write(merged_data)
else:
    st.warning('Please upload the Excel files.')
