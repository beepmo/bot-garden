import time

import pandas as pd
import requests
import io
from dotenv import load_dotenv
import os

# -------------------------------------------------------
# Secrets

load_dotenv()
username = os.getenv('USERNAME')
pat = os.getenv('PAT')

# Creates a re-usable session object with your creds in-built

github_session = requests.Session()
github_session.auth = (username, pat)

# -------------------------------------------------------
# Downloading the csv_pddf file from GitHub

url = 'https://raw.githubusercontent.com/beepmo/gardens/main/' \
      + 'dashboard_food.csv_pddf?token=GHSAT0AAAAAAB4Y6LCO7PDEY5NL4O76IHFEY5OJJKQ'

result = github_session.get(url)

status = result.status_code
# assert status != 404
# >>> AssertionError
# FIXME: 404 error. I had to make local csv to test other features

download = result.content


# -------------------------------------------------------
# Reading the downloaded content and making it a pandas dataframe


def to_bool(label):
    return bool(label)


start_csv = time.time()
csv_pddf = pd.read_csv('dashboard_food.csv',
                       header=0,
                       names=['Bed', 'Label', 'Geo?', 'Status', 'Status Date', 'Taxon'],
                       parse_dates=['Status Date'],
                       # converters={'Geo?': to_bool,
                       #             'Label': to_bool
                       #             },
                       # dtype={'Bed': 'category',
                       #        'Status': 'category',
                       #        }
                       )
end_csv = time.time()
memory = csv_pddf.memory_usage(deep=True)

print(f'Time taken to read csv into df: {(end_csv - start_csv):f}.\n'
      f'Memory usage: \n {memory}')

print(csv_pddf.head())
