import requests
from bs4 import BeautifulSoup
import streamlit as st
import pandas as pd
import math
from io import BytesIO


def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data


def process_items(df: pd.DataFrame):
    items = []
    manufacturer = ''
    for index, row in df.iterrows():
        if 'Total' in str(row['Manufacturer']):
            continue

        if not pd.isna(row['Manufacturer']):
            manufacturer = row['Manufacturer']

        if len(row) <= 1:
            continue

        if 'sold' in str(row['Model']) or '?print=customer' in str(row['Model']):
            continue

        print(f"Manufacturer: {manufacturer}")
        print(f"Model: {row['Model']}")
        items.append({'Manufacturer': manufacturer, 'Model': str(row['Model'])})

    # items = list(filter(lambda x: 'sold' not in str(x['Model']) and '?print=customer' not in str(x['Model']), items))

    print(len(items))
    return items


uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    # Can be used wherever a "file-like" object is accepted:
    dataframe = pd.read_csv(uploaded_file)

    st.write(dataframe)
    # process_report(dataframe)

    items = process_items(dataframe)

    url = "https://www.carpricetracker.com/history/search/car?searchTerm="

    data = {
        "Manufacturer": [],
        "Model": [],
        "Year": [],
        "Price": [],
        "Prices": [],
        "Price Changes": []
    }



    for car in items:
        formattedManufacturer = car['Manufacturer'].replace(' ', '+')
        formattedModel = car['Model'].replace(' ', '+')
        searchTerm = f"{formattedManufacturer}+{formattedModel}"
        data[f"{searchTerm}"] = []
        request_url = f"{url}{searchTerm}"
        print(request_url)

        try:
            page = requests.get(request_url, timeout=10)  # Added timeout
            content = page.text
            soup = BeautifulSoup(content, "html.parser")
            rows = soup.findAll("tr")
            # data[f"{searchTerm}"].append(["Year", "Price", "Prices", "Price Changes"])




            for row in rows:
                row_data = row.findAll("td")
                if not row_data:
                    continue
                year = row_data[1].text
                price = row_data[3].text
                prices = row_data[4].text
                price_changes = row_data[5].text
                # data[f"{searchTerm}"].append([year, price, prices, price_changes])
                data["Manufacturer"].append(car['Manufacturer'])
                data["Model"].append(car['Model'])
                data["Year"].append(year)
                data["Price"].append(price)
                data["Prices"].append(prices)
                data["Price Changes"].append(price_changes)



        except Exception as e:
            print(e)

    dataframe = pd.DataFrame(data, columns=["Manufacturer", "Model", "Year", "Price", "Prices", "Price Changes"])
    excel = to_excel(dataframe)
    st.download_button(label='Download Excel file', data=excel, file_name='data.xlsx',
                       mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
