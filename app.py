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


def process_items_caredge(df: pd.DataFrame):
    items = []
    for index, row in df.iterrows():
        items.append({'Manufacturer': row['Manufacturer'], 'Model': row['Model']})

    return items


def process_items_carpricetracker(df: pd.DataFrame):
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

        items.append({'Manufacturer': manufacturer, 'Model': str(row['Model'])})

    return items


st.header("Upload a Car Price Tracker CSV file")
uploaded_file_carpricetracker = st.file_uploader("Choose a file", key='carpricetracker')
if uploaded_file_carpricetracker is not None:
    # Can be used wherever a "file-like" object is accepted:
    dataframe = pd.read_csv(uploaded_file_carpricetracker)

    st.write(dataframe)

    items = process_items_carpricetracker(dataframe)

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

        try:
            page = requests.get(request_url, timeout=10)  # Added timeout
            content = page.text
            soup = BeautifulSoup(content, "html.parser")
            rows = soup.findAll("tr")

            for row in rows:
                row_data = row.findAll("td")
                if not row_data:
                    continue
                year = row_data[1].text
                price = row_data[3].text
                prices = row_data[4].text
                price_changes = row_data[5].text
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

st.header("Upload a Car Edge CSV file")
uploaded_file_caredge = st.file_uploader("Choose a file", key='caredge')
if uploaded_file_caredge is not None:
    # Can be used wherever a "file-like" object is accepted:
    dataframe = pd.read_csv(uploaded_file_caredge)

    st.write(dataframe)

    items = process_items_caredge(dataframe)
    #
    url = "https://www.caredge.com/"
    #
    data = {
        "Manufacturer": [],
        "Model": [],
        "Years Old": [],
        "Depreciation": [],
        "Residual Value": [],
        "Resale Value": [],
        "Mileage": [],
        "Resale Year": []
    }
    #
    for car in items:
        request_url = f"{url}{car['Manufacturer'].replace(' ', '-').lower()}/{car['Model'].replace(' ', '-').lower()}/depreciation"

        try:
            page = requests.get(request_url, timeout=10)  # Added timeout
            content = page.text
            soup = BeautifulSoup(content, "html.parser")
            table = soup.find('table', attrs={'class': 'table table-striped pillar-table-border-none'})
            rows = table.findAll("tr")
            for row in rows:
                row_data = row.findAll("td")
                if not row_data:
                    continue

                data["Manufacturer"].append(car['Manufacturer'])
                data["Model"].append(car['Model'])
                data["Years Old"].append(row_data[0].text)
                data["Depreciation"].append(row_data[1].text)
                data["Residual Value"].append(row_data[2].text)
                data["Resale Value"].append(row_data[3].text)
                data["Mileage"].append(row_data[4].text)
                data["Resale Year"].append(row_data[5].text)


        except Exception as e:
            print(e)

    dataframe = pd.DataFrame(data, columns=["Manufacturer", "Model", "Years Old", "Depreciation", "Residual Value",
                                            "Resale Value", "Mileage", "Resale Year"])
    excel = to_excel(dataframe)
    st.download_button(label='Download Excel file', data=excel, file_name='data.xlsx',
                       mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
