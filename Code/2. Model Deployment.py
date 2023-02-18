#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import xgboost as xgb
import streamlit as st
import pandas as pd

#Loading up the Regression model we created
# model = xgb.XGBClassifier()
# model.load_model('xgb_model.json')

# @st.cache

st.title('Hotel Bookings')
st.image("""https://www.frommers.com/system/media_items/attachments/000/864/746/s980/shutterstock_ribkhan-crop.jpg?1571248109""")
st.header('Enter the hotel booking info or upload a file:')
no_of_weekday_nights = st.number_input('No. of Weekday Nights:', value = 1)
no_of_weekend_nights = st.number_input('No. of Weekend Nights:', value = 1)
market_segment = st.selectbox('Customer Market Segment:', ['Aviation','Complementary','Corporate','Offline','Online'])


