#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import xgboost as xgb
import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import zipfile
import calendar
import matplotlib.pyplot as plt
from datetime import date, timedelta
import plotly.express as px
# import streamlit.components.v1 as components
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

#Loading up the Classification model we created
model = xgb.XGBClassifier()
model.load_model('xgb_model.json')


#code taken and modified from: https://blog.streamlit.io/auto-generate-a-dataframe-filtering-ui-in-streamlit-with-filter_dataframe/#bringing-it-all-together
def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", ['Booking_ID','Prediction'])
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    min_value=_min,
                    max_value=_max,
                    value=(_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring in {column}",
                )
                if user_text_input:
                    df = df[df[column].astype(str).str.contains(user_text_input)]

    return df



st.set_page_config(page_title="My App",layout='wide')

st.title('Hotel Booking Cancellation Predictions')
st.image("""https://www.frommers.com/system/media_items/attachments/000/864/746/s980/shutterstock_ribkhan-crop.jpg?1571248109""")

# Create a zip folder
zipObj = zipfile.ZipFile("sample.zip", "w")

df_viz = pd.DataFrame()

with st.sidebar:
    capacity = st.number_input('Capacity of the hotel:', value = 1) 
    counter = 0
    uploaded_files = st.file_uploader("Upload CSV file(s)", accept_multiple_files=True)
    process_data = st.checkbox("Process")
    if process_data:
        for uploaded_file in uploaded_files:
            if uploaded_file is not None:
                counter += 1
                df = pd.read_csv(uploaded_file)
                file_name = uploaded_file.name[:-4] + '_returns.csv'

                #Pre-processing 
                df2 = df.copy()

                df2['no_of_previous_bookings'] = df2['no_of_previous_cancellations'] + df2['no_of_previous_bookings_not_canceled']
                df2['no_of_nights'] = df2['no_of_week_nights'] + df2['no_of_weekend_nights']
                df2['date_combined'] = (df2['arrival_year'].astype(str) + '-' 
                                          + df2['arrival_month'].astype(str) + '-' + df['arrival_date'].astype(str))

                df2['date_combined'].replace('2023-2-29','2023-3-1', inplace=True)

                df2['date_combined'] = pd.to_datetime(df2['date_combined'])

                df2['arrival_day'] = df2['date_combined'].dt.dayofweek

                df3 = df2.drop(['Booking_ID','date_combined'],axis=1)

                df4 = pd.get_dummies(df3, columns=['type_of_meal_plan','room_type_reserved','market_segment_type'], drop_first=True)
                                
                #Model prediction
                prediction = model.predict(df4)
                
                df['Prediction'] = prediction
                df['Prediction'] = np.where(df['Prediction'] == 1, 'Cancelled', 'Not Cancelled')
                
                #save and append df for visualisation
                df2['Prediction'] = prediction
                df2['Prediction'] = np.where(df2['Prediction'] == 1, 'Cancelled', 'Not Cancelled')
                df_viz = df_viz.append(df2)

                #For single file
                csv = df.to_csv(index=False).encode('utf-8')

                #For multiple files

                df.to_csv(file_name, index= False)

                zipObj.write(file_name)
        # close the Zip File
        zipObj.close()
        ZipfileDotZip = "sample.zip"
        
        if len(uploaded_files) > 1: 
            with open(ZipfileDotZip, "rb") as fp:
                btn = st.download_button(
                    label="Download the returns as ZIP",
                    data=fp,
                    file_name="returns.zip",
                    mime="application/zip"
                    )
        else:
            st.download_button(label=f'Download the returns for {uploaded_file.name[:-4]} as CSV',
                                   data=csv,
                                   file_name=file_name,
                                   mime='text/csv',
                                   key=counter
                                  )

   

## Visualisations

if process_data:
    
    occupancy_df = df_viz.groupby('date_combined').size().reset_index(name='Occupancy')
    today_date = date.today().strftime('%Y-%m-%d')
    occupancy = occupancy_df.loc[occupancy_df['date_combined'] == today_date]['Occupancy']
                                                                              
    col1, col2, col3 = st.columns(3)
    col1.metric("Date", date.today().strftime('%d-%b-%Y'))
    col2.metric("No. of Rooms Booked", occupancy)
    col3.metric("% Occupied", round(occupancy/capacity*100,1)) 

    if st.checkbox("Click here to view the dataframe with predictions"):
        st.write(filter_dataframe(df))
#     st.write(df)
    
    col1, col2, col3 = st.columns([1,5,1])
    with col2:
        st.subheader("Percentage of rooms occupied over time")
        # % Occupied chart
        df_occ = df_viz[df_viz['Prediction'] != 'Cancelled'] 
        df_occ = df_occ.groupby('date_combined').size().reset_index(name='Occupancy')
        df_occ['% Occupied'] = df_occ['Occupancy'].apply(lambda x: x/capacity*100)
        fig = px.line(df_occ, x='date_combined', y='% Occupied')
        st.plotly_chart(fig)

        st.subheader("Percentage of room cancellations by lead time")
        # Lead Time chart
        df_pct = df.groupby('lead_time')['Prediction'].value_counts(normalize=True).mul(100).rename('% Cancelled').reset_index()
        df_pct = df_pct.loc[df_pct['Prediction'] == 'Cancelled']
        fig = px.line(df_pct, x='lead_time', y='% Cancelled')
        st.plotly_chart(fig)

        st.subheader("Percentage of room cancellations by market segment type")
        # Market Segment Type chart
        df_pct = df_viz.groupby('market_segment_type')['Prediction'].value_counts(normalize=True).mul(100).rename('percent').reset_index()
        fig = px.bar(df_pct, x='market_segment_type', y='percent', color='Prediction', barmode='stack')
        st.plotly_chart(fig)

        st.subheader("Percentage of room cancellations by returning guests")
        # Repeated Guest chart
        df_pct = df_viz.groupby('repeated_guest')['Prediction'].value_counts(normalize=True).mul(100).rename('percent').reset_index()
        df_pct['repeated_guest'] = np.where(df_pct['repeated_guest'] == 1, 'Yes', 'No')
        fig = px.bar(df_pct, x='repeated_guest', y='percent', color='Prediction', barmode='stack')
        st.plotly_chart(fig)
        
        st.subheader("No. of 1st-time guests over time")
        df_new = df_viz.loc[df_viz['repeated_guest'] == 0]
        df_new = df_new.groupby('date_combined').size().reset_index(name='No. of 1st-time guests')
        fig = px.line(df_new, x='date_combined', y='No. of 1st-time guests')
        st.plotly_chart(fig)



    
