#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#Functions copied from ONS_consumer_price_indices python notebook
#This is purely for the app.py to retrive the functions from
#for full details check out the python notebook 

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pandas as pd
import requests
from dotenv import load_dotenv

#Configurations

load_dotenv()

BASE_URL = 'https://api.beta.ons.gov.uk/v1'

DATASET_ID = os.getenv('ONS_DATASET_ID', 'cpih01')
OUTPUT_DIR = Path(os.getenv('ONS_OUTPUT_DIR', 'data'))

RAW_DIR = OUTPUT_DIR / 'raw'
PROCESSED_DIR = OUTPUT_DIR / 'processed'
LOG_DIR = Path('logs')

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

#Logging

# better than print() errors, because this might run unattended

log_file = LOG_DIR / 'ons_pipeline.log'

logging.basicConfig(
    level = logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)

#HTTP helpers

#make GET reqeusts and return JSON, raises error if not successful
def get_json(url: str, timeout: int = 30) -> dict[str, Any]:
    logger.info("Requesting JSON: %s", url)

    response = requests.get(url, timeout=timeout)
    response.raise_for_status()

    return response.json()

#Download a file from a URL to local
def download_file(url: str, output_path: Path, timeout: int = 60) -> None:
    logger.info("Downloading file: %s", url)

    response = requests.get(url, timeout=timeout)
    response.raise_for_status()

    output_path.write_bytes(response.content)

    logger.info("Saved raw file: %s", output_path)

#ONS-Specific helpers

#Get metadata for lateste version of ONS dataset
def get_latest_version_metadata(dataset_id: str) -> dict[str, Any]:
    dataset_url = f"{BASE_URL}/datasets/{dataset_id}"

    dataset_metadata = get_json(dataset_url)

    try:
        latest_version_url = dataset_metadata["links"]["latest_version"]["href"]
    except KeyError as exc:
        raise KeyError(
            "Could not find links.latest_version.href in dataset metadata."
        ) from exc

    latest_version_metadata = get_json(latest_version_url)

    return latest_version_metadata

#Search recuesively for ONS version metadata for a CSV download URL
def find_csv_download_url(metadata: dict[str, Any]) -> str:
    candidate_urls: list[str] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"href", "url"} and isinstance(item, str):
                    candidate_urls.append(item)
                walk(item)

        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(metadata)

    csv_urls = [
        url for url in candidate_urls
        if ".csv" in url.lower() or "csv" in url.lower()
    ]

    if not csv_urls:
        raise ValueError("Could not find a CSV download URL in the metadata.")

    # Prefer a normal CSV over CSVW metadata.
    normal_csv_urls = [
        url for url in csv_urls
        if "csvw" not in url.lower()
    ]

    return normal_csv_urls[0] if normal_csv_urls else csv_urls[0]

#Cleaning

#Cleans downloaded ONS csv
def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    logger.info('Starting cleaning. Original shape: %s', df.shape)

    df = df.copy()

    #Standardise column names
    df.columns = [
        col.strip().lower().replace(' ', '_').replace('-', '_')
        for col in df.columns
    ]

    #Remove fully empty rows and columns
    df = df.dropna(how='all')
    df = df.dropna(axis=1, how='all')

    #Strip whitespace from text columns.
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].astype(str).str.strip()

    #Convert obvious numeric columns where possible
    for col in df.columns:
        if col in {'v4_0', 'value', 'observation', 'obs_value'} or 'value' in col:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    #Try to parse columns that look like date/time
    for col in df.columns:
        if col in {'time', 'date', 'month', 'year'} or 'date' in col:
            parsed = pd.to_datetime(df[col], errors='coerce')
            if parsed.notna().sum() > 0:
                df[f'{col}_parsed'] = parsed

    logger.info('Finished cleaning. Cleaned shape: %s', df.shape)

    return df

#Validation

#Validate the 'cleaned' dataset
#Return error if somethins is wrong
def validate_dataset(df: pd.DataFrame) -> None:
    logger.info('Starting validation.')

    if df.empty:
        raise ValueError('Validation failed: dataset is empty.')

    if df.columns.duplicated().any():
        duplicated = df.columns[df.columns.duplicated()].tolist()
        raise ValueError(f'Validation failed: duplicate columns: {duplicated}')

    duplicate_rows = df.duplicated().sum()
    if duplicate_rows > 0:
        logger.warning('Found %s duplicate rows.', duplicate_rows)

    missing_summary = df.isna().mean().sort_values(ascending=False)
    high_missing = missing_summary[missing_summary > 0.95]

    if not high_missing.empty:
        logger.warning(
            'Columns with more than 95%% missing values: %s',
            high_missing.to_dict(),
        )

    logger.info('Validation passed.')

    
#Main Pipeline

def main() -> None:
    run_timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S') #prevents overwriting yesteradays file

    logger.info('Starting ONS pipeline.')
    logger.info('Dataset ID: %s', DATASET_ID)

    latest_metadata = get_latest_version_metadata(DATASET_ID)
    csv_url = find_csv_download_url(latest_metadata)

    parsed_url = urlparse(csv_url)
    original_filename = Path(parsed_url.path).name or f'{DATASET_ID}.csv'

    raw_path = RAW_DIR / f'{DATASET_ID}_{run_timestamp}_{original_filename}'
    processed_path = PROCESSED_DIR / f'{DATASET_ID}_{run_timestamp}_clean.csv'

    download_file(csv_url, raw_path)

    logger.info('Reading raw CSV with pandas.')
    df = pd.read_csv(raw_path)

    cleaned_df = clean_dataset(df)
    validate_dataset(cleaned_df)

    cleaned_df.to_csv(processed_path, index=False)

    logger.info('Saved processed dataset: %s', processed_path)
    logger.info('Pipeline complete.')

if __name__ == '__main__':
    try:
        main()
    except requests.HTTPError as exc:
        logger.exception('HTTP error while calling ONS API: %s', exc)
        raise
    except requests.RequestException as exc:
        logger.exception('Network error while calling ONS API: %s', exc)
        raise
    except Exception as exc:
        logger.exception('Pipeline failed: %s', exc)
        raise

