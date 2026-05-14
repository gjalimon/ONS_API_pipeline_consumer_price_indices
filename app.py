#!/usr/bin/env python
# coding: utf-8

# In[1]:


#Main Streamlit App code 
#This turns the ONS pipeline python code into a web app

import io #makes downloaded bytes treated like a file
from datetime import datetime, timezone
import pandas as pd
import requests #allows downloads CSV files from the internet
import streamlit as st #use to create the web app interface

#functions from python notebook: ONS consumer price indices pipeline
from ons_dataset_app_functions import (
    get_latest_version_metadata,
    find_csv_download_url,
    clean_dataset,
    validate_dataset,
)  

#Page setup

#Browser tab title, icon and page layout
st.set_page_config(
    page_title='ONS API Pipeline Consumer Price Indices',
    page_icon ='📊',
    layout='wide',
)

#App Title
st.title('ONS API Pipeline Consumer Price Indices')

#App Description
st.write(
    'Downloads the latest ONS dataset on Consumer Price Indices, cleans and validates,'
    'it will provide the raw and processed CSV files.'
)

# Session state setup
# Session state keeps values even when Streamlit reruns the page.
# This stops the app from going back to the starting screen after a download click.

if "result_ready" not in st.session_state:
    st.session_state.result_ready = False

if "raw_csv_bytes" not in st.session_state:
    st.session_state.raw_csv_bytes = None

if "processed_csv_bytes" not in st.session_state:
    st.session_state.processed_csv_bytes = None

if "cleaned_preview" not in st.session_state:
    st.session_state.cleaned_preview = None

if "csv_url" not in st.session_state:
    st.session_state.csv_url = None

if "timestamp" not in st.session_state:
    st.session_state.timestamp = None

if "dataset_id" not in st.session_state:
    st.session_state.dataset_id = "cpih01"
    
#User Input
#Text box where user can type an ONS dataset ID
#The ONLY value for now is cpih01

dataset_id = st.text_input(
    'ONS dataset ID',
    value='cpih01',
    help='Only available dataset (for now) is: cpih01'
)

#Creates button that will run the pipeline
run_button = st.button('Get latest ONS dataset')

#Main app LOGIC

#This block runs only when the user clicks the button
if run_button:
    try:
        with st.spinner('Getting latest dataset fron ONS...'):
            latest_metadata = get_latest_version_metadata(dataset_id) #get metadata for latest version
            csv_url = find_csv_download_url(latest_metadata) #find download url for csv inside metadata
            response= requests.get(csv_url, timeout=60) #download csv file from url
            response.raise_for_status() #Raise an error if download fail
            raw_csv_bytes = response.content #store downloaded raw csv content as bytes
            raw_df = pd.read_csv(io.BytesIO(raw_csv_bytes)) #convert raw bytes into file-like object then read as pandas df
            cleaned_df = clean_dataset(raw_df) #clean dataset using pre existing function
            validate_dataset(cleaned_df) #validate using pre exisiting function
            processed_csv_bytes = cleaned_df.to_csv(index=False).encode("utf-8")
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

            #Save everything into session state
            st.session_state.result_ready = True
            st.session_state.raw_csv_bytes = raw_csv_bytes
            st.session_state.processed_csv_bytes = processed_csv_bytes
            st.session_state.cleaned_preview = cleaned_df.head(10)
            st.session_state.csv_url = csv_url
            st.session_state.timestamp = timestamp
            st.session_state.dataset_id = dataset_id

        #If everything worked, show success message
        st.success('Dataset downloaded, cleaned and validated successfully.')

    #Error if something goes wrong in the streamlit app
    except Exception as error:
        st.session_state.result_ready = False
        st.error("Something went wrong.")
        st.exception(error)

#Show results
if st.session_state.result_ready:
    #Show a small preview of the processed dataset
    st.subheader('Preview of processed data')
    st.dataframe(st.session_state.cleaned_preview)

    #Create two columns so the download buttons sit side by side.
    col1, col2 = st.columns(2)

        # First column: raw CSV download button
    with col1:
        st.download_button(
            label='Download raw CSV',
            data= st.session_state.raw_csv_bytes,
            file_name = f'{st.session_state.dataset_id}_{st.session_state.timestamp}_raw.csv',
            mime='text/csv',
        )

    # Second column: processed CSV download button
    with col2:
        st.download_button(
            label='Download processed CSV',
            data=st.session_state.processed_csv_bytes,
            file_name=f'{st.session_state.dataset_id}_{st.session_state.timestamp}_processed.csv',
            mime='text/csv',
        )

    # Show the original ONS source CSV URL in an expandable section
    #for tranparency and debugging
    with st.expander('Source CSV URL'):
        st.write(st.session_state.csv_url)


