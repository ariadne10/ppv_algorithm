import streamlit as st
import pandas as pd
import base64
import datetime

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    # Get current date
    current_date = datetime.datetime.now().strftime('%m-%d-%y')

    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="PPV_{current_date}.csv">Download csv file</a>'
    return href

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
    # Check if open_orders is empty
    if open_orders.empty:
        st.warning('Open Orders file is empty.')
    else:
        # Continue with processing
        open_orders['POCreateDate Hierarchy - POCreateDate'] = pd.to_datetime(open_orders['POCreateDate Hierarchy - POCreateDate'])
        open_orders = open_orders.sort_values('POCreateDate Hierarchy - POCreateDate', ascending=False).drop_duplicates(subset='FinalKey', keep='first')
        open_orders = open_orders.iloc[:-2, :]
        open_orders['FinalKey'] = open_orders['FinalKey'].str.upper()

    # Merging
    merged_data = ppv_offers.merge(sat_quotes, on='FinalKey', how='left')
    if not open_orders.empty:
        merged_data = merged_data.merge(open_orders, on='FinalKey', how='left')

    # Drop specified columns
    merged_data = merged_data.drop(columns=['FinalKey', 'STD Site', 'STD JPN', 'STD MPN'])

    # Write the DataFrame to the screen
    st.write(merged_data)

    # Export to CSV (as a Download Link)
    st.markdown(get_table_download_link(merged_data), unsafe_allow_html=True)
else:
    st.warning('Please upload the Excel files.')
