# ONS_API_pipeline_consumer_price_indices
A small pipeline that extracts, cleans, validates and loads the latest dataset for the consumer price indices using ONS public API

# Click here to use the web app:
[ONS API on Consumer Price Indices -Pipeline - web App](https://onsapipipelineconsumerpriceindices-cgcqxkbseuqgzozfdhpyjj.streamlit.app/)

# Basic steps of the pipeline:
1. Reads the links.latest_version.hrefy
2. Get the latest version URL
3. Find the CSV download link
4. Download CSV and save into the RAW folder
5. Clean and Validate
6. Save this clean version into the Processed folder

# Web App steps are the same except it provides download links instead.

# Project structure:

ONS_API_pipeline_consumer_price_indices/

- get_ons_dataset.py

- notebook.ipynb

- requirements.txt

- .env.example

- data/

-----/raw/

----/ processed/

- logs/

# Steps on running this ONS pipeline on your personal computer instead of using the web app

This guide is for users who want to download the project and run the Python pipeline locally, instead of using the web app.

# I. Install Python

First, install Python on your laptop.

https://www.python.org/downloads/

Download and install Python.

During installation, make sure you tick:

Add Python to PATH

# II. Download this repository
On this GitHub page:
1. Click the green CODE button.
2. Click Download ZIP
3. Unzip the downloaded file.
4. Open the project folder on your laptop.
5. The folder should contain:
   
  app.py
  
  requirements.txt
  
  README.md
  
  ons_dataset_app_functions.py  --> this is the file used for local Python pipeline

# III. Setting up the Python pipeline
1. Open the project folder in a terminal
2. Install the required Python packages using this line in your terminal:
   
(for Windows)

python -m pip install -r requirements.txt

(for Mac/Linux try)

python3 -m pip install -r requirements.txt

4. In the project folder create a new 'text' file and rename it to .env
4.. Inside .env file add this two lines: (This tells the script which ONS dataset to download and where to save the files)
ONS_DATASET_ID=cpih01
ONS_OUTPUT_DIR=data

# IV. Running the Python Pipeline
1. Run this line in still in the same terminal
   
(for Windows)

python ons_dataset_app_functions.py

(for Mac/Linux try)

python3 ons_dataset_app_functions.py

# V. Finding the downloaded files
1. The pipeline script will create a 'data' folder, inside this folder is another 'raw' and 'processed' folders.
2. raw CSV inside raw, processed CSV inside processed folder and the logs will be saves inside logs.

# That's it!

Any errors feel free to contact me using my github contact details.

# Alternatively, if you have Python notebook already installed (e.g. Jupyter, Marimo)

You can just download the ONS_consumer_price_indices.ipynb file and run it in your notebook

# Sources

This project was built using the following documentation and public examples as references:

1. [ONS Developer Hub: Introduction](https://developer.ons.gov.uk/)  
  
2. [ONS Digital Blog: How to access data from the ONS beta API](https://digitalblog.ons.gov.uk/2021/02/15/how-to-access-data-from-the-ons-beta-api/)

3. - [David Corney GitHub Repo: How to access the ONS API via Python](https://github.com/dcorney/ons-api)
  
4. - [NHS England GitHub Repo: ons-api](https://github.com/nhsengland/ons-api)
  
5. [Streamlit Documentation: `st.download_button`](https://docs.streamlit.io/develop/api-reference/widgets/st.download_button)

6. [Streamlit Documentation: Session State](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state)  
