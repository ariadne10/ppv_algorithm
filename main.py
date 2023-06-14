import streamlit as st
import pandas as pd
import base64
import datetime

def get_table_download_link(df):
    current_date = datetime.datetime.now().strftime('%m-%d-%y')
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode() 
    href = f'<a href="data:file/csv;base64,{b64}" download="PPV_{current_date}.csv">Download csv file</a>'
    return href

ppv_offers_file = st.file_uploader("Upload PPV Offers Excel", type=['xlsx'])
sat_quotes_file = st.file_uploader("Upload SAT Quotes Excel", type=['xlsx'])
open_orders_file = st.file_uploader("Upload Open Orders Excel", type=['xlsx'])

# New file uploader widget for review file
review_file = st.file_uploader("Upload Review Excel", type=['xlsx'])

if ppv_offers_file and sat_quotes_file and open_orders_file:
    ppv_offers = pd.read_excel(ppv_offers_file)
    sat_quotes = pd.read_excel(sat_quotes_file)
    open_orders = pd.read_excel(open_orders_file)
    
    # Read review file if uploaded
    review_data = pd.read_excel(review_file) if review_file else None

    ppv_offers = ppv_offers.iloc[:-2, :]
    string_columns = ppv_offers.select_dtypes(include='object')
    string_columns = string_columns.applymap(lambda x: str(x).upper() if pd.notnull(x) else x)
    ppv_offers[string_columns.columns] = string_columns

    ppv_offers = ppv_offers[
        ppv_offers.apply(lambda x: x['Offer JPN'] in x['STD JPN'] if pd.notna(x['Offer JPN']) and pd.notna(x['STD JPN']) else False, axis=1) &
        ppv_offers.apply(lambda x: x['Offer MPN'] in x['STD MPN'] if pd.notna(x['Offer MPN']) and pd.notna(x['STD MPN']) else False, axis=1) &
        ppv_offers.apply(lambda x: x['Offer Site'] in x['STD Site'] if pd.notna(x['Offer Site']) and pd.notna(x['STD Site']) else False, axis=1)
    ]

    sat_quotes = sat_quotes.iloc[:-2, :]
    sat_quotes['FinalKey'] = sat_quotes['FinalKey'].str.upper()

    if open_orders.empty:
        st.warning('Open Orders file is empty.')
    else:
        open_orders['POCreateDate Hierarchy - POCreateDate'] = pd.to_datetime(open_orders['POCreateDate Hierarchy - POCreateDate'])
        open_orders = open_orders.sort_values('POCreateDate Hierarchy - POCreateDate', ascending=False).drop_duplicates(subset='FinalKey', keep='first')
        open_orders = open_orders.iloc[:-2, :]
        open_orders['FinalKey'] = open_orders['FinalKey'].str.upper()

    merged_data = ppv_offers.merge(sat_quotes, on='FinalKey', how='left')
    merged_data = merged_data.merge(open_orders, on='FinalKey', how='left')

    if review_data is not None:
        review_data['FinalKey'] = review_data['FinalKey'].str.upper()
        keys_not_in_merged = set(review_data['FinalKey']) - set(merged_data['FinalKey'])
        rows_to_append = review_data[review_data['FinalKey'].isin(keys_not_in_merged)]
        merged_data = merged_data.append(rows_to_append, ignore_index=True)

    merged_data.drop_duplicates(subset=['FinalKey', 'Company Name'], inplace=True)

    merged_data = merged_data.drop(columns=['Offer Site', 'Offer JPN', 'STD MPN', 'Jabil Media', 'MPQ_1', 'Date Release', 'Delivery Date', 'POCreateDate Hierarchy - POCreateDate', 'SupplierGlobalName Hierarchy - SupplierGlobalName', 'Open Order Cost', 'TP', 'Lead Time', 'PR QTY'])

    merged_data = merged_data.rename(columns={
        'STD Site': 'Site',
        'STD JPN': 'JPN',
        'Offer MPN': 'MPN',
        'Supplier Media': 'Media',
        'StandardCostUSD': 'BU STD',
    })

    cols = merged_data.columns.tolist()
    cols.insert(cols.index("BU STD")+1, cols.pop(cols.index('SAT Active Price')))
    merged_data = merged_data[cols]

    st.write(merged_data)

    st.markdown(get_table_download_link(merged_data), unsafe_allow_html=True)
