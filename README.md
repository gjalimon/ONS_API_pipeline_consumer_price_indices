# ONS_API_pipeline_consumer_price_indices
A small pipeline that extracts, cleans, validates and loads the latest dataset for the consumer price indices using ONS public API

Basic steps of the pipeline:
1. Reads the links.latest_version.hrefy
2. Get the latest version URL
3. Find the CSV download link
4. Download CSV and save into the RAW folder
5. Clean and Validate
6. Save this clean version into the Processed folder

Project structure

ONS_API_pipeline_consumer_price_indices/

- get_ons_dataset.py

- notebook.ipynb

- requirements.txt

- .env.example

- data/

-----/raw/

----/ processed/

- logs/
