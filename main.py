import streamlit as st
import pandas as pd

def load_data(upload):
    data = pd.read_csv(upload)
    data = data.drop(data.index[-2:])
    data['FinalKey'] = data['FinalKey'].str.upper()
    return data

def process_ppv_offers(data):
    data['Offer MPN'] = data['Offer MPN'].str.upper()
    data['STD MPN'] = data['STD MPN'].str.upper()
    data['Offer JPN'] = data['Offer JPN'].str.upper()
    data['STD JPN'] = data['STD JPN'].str.upper()
    data['JPN'] = data['JPN'].str.upper()
    data['Site'] = data['Site'].str.upper()
    data['Offer Site'] = data['Offer Site'].str.upper()
    data['STD Site'] = data['STD Site'].str.upper()
    data['FinalKey'] = data['FinalKey'].str.upper()

    data = data[data['Offer JPN'] == data['STD JPN']]
    data = data[data['Offer MPN'] == data['STD MPN']]
    data = data[data['Offer Site'] == data['STD Site']]

    return data

def main():
    st.title("CSV Data Processor")
    ppv_file = st.file_uploader("Upload PPV Offers", type=['csv'])
    sat_file = st.file_uploader("Upload SAT Quotes", type=['csv'])
    open_file = st.file_uploader("Upload Open Orders", type=['csv'])

    if ppv_file is not None and sat_file is not None and open_file is not None:
        ppv_offers = load_data(ppv_file)
        ppv_offers = process_ppv_offers(ppv_offers)
        sat_quotes = load_data(sat_file)
        open_orders = load_data(open_file)

        merged_data = ppv_offers.merge(sat_quotes, on='FinalKey', how='left')
        # merged_data = merged_data.merge(open_orders, on='FinalKey', how='left')

        st.write(merged_data)

        csv = merged_data.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  
        href = f'<a href="data:file/csv;base64,{b64}" download="merged_data.csv">Download CSV File</a>'
        st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

