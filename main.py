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
    # Convert all string/object type columns to upper case
    string_columns = ppv_offers.select_dtypes(include='object')
    string_columns = string_columns.applymap(lambda x: str(x).upper() if pd.notnull(x) else x)
    ppv_offers[string_columns.columns] = string_columns

    ppv_offers = ppv_offers[
        ppv_offers.apply(lambda x: x['Offer JPN'] in x['STD JPN'] if pd.notna(x['Offer JPN']) and pd.notna(x['STD JPN']) else False, axis=1) &
        ppv_offers.apply(lambda x: x['Offer MPN'] in x['STD MPN'] if pd.notna(x['Offer MPN']) and pd.notna(x['STD MPN']) else False, axis=1) &
        ppv_offers.apply(lambda x: x['Offer Site'] in x['STD Site'] if pd.notna(x['Offer Site']) and pd.notna(x['STD Site']) else False, axis=1)
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
merged_data = merged_data.merge(open_orders, on='FinalKey', how='left')

merged_data.drop_duplicates(subset=['FinalKey', 'Company Name'], inplace=True)

# Drop specified columns
merged_data = merged_data.drop(columns=['FinalKey', 'Offer Site', 'Offer JPN', 'STD MPN', 'Jabil Media', 'MPQ_1', 'Date Release', 'Delivery Date', 'POCreateDate Hierarchy - POCreateDate', 'SupplierGlobalName Hierarchy - SupplierGlobalName', 'Open Order Cost', 'TP', 'Lead Time'])

# Rename columns
merged_data = merged_data.rename(columns={
    'STD Site': 'Site',
    'STD JPN': 'JPN',
    'Offer MPN': 'MPN',
    'Supplier Media': 'Media',
    'StandardCostUSD': 'BU STD',
})

# Rearrange columns to place 'SAT Active Price' after 'BU STD'
cols = merged_data.columns.tolist()
cols.insert(cols.index("BU STD")+1, cols.pop(cols.index('SAT Active Price')))
merged_data = merged_data[cols]

# Write the DataFrame to the screen
st.write(merged_data)

# Export to CSV (as a Download Link)
st.markdown(get_table_download_link(merged_data), unsafe_allow_html=True)
