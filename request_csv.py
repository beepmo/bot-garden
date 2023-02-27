import time
from datetime import datetime
import pandas as pd
import requests
import io
from dotenv import load_dotenv
import os

# -------------------------------------------------------
RAW_ATTRIBUTES = ['Bed', 'Label', 'Geo?', 'Days elapsed since ItemStatusDate', 'Taxon']

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

url = 'https://raw.githubusercontent.com/beepmo/gardens/main/dashboard_food.csv?token=GHSAT0AAAAAAB4Y6LCOT56H4RHZEM73B7LAY6XIRMQ'

result = github_session.get(url)

status = result.status_code
assert status != 404

download = result.content

# -------------------------------------------------------
# Reading the downloaded content and making it a pandas dataframe

today = datetime.today()


def days_since(strin):
    try:
        date = datetime.strptime(strin, '%m/%d/%y')
        delta = today - date
        # If %y < 70, strptime defaults to 2000s. check for 1916-60s.
        # count on nothing being unchecked for 100 years. I checked; seems true
        days = int(delta.days)
        if days < 0:
            days += 36500  # 100 years
        return days
    except ValueError:
        try:
            date = datetime.strptime(strin, '%Y-%m')  # full year specified
            delta = today - date
            return delta.days
        except:
            pass


def to_bool(label):
    return bool(label)


start_csv = time.time()
# noinspection PyTypeChecker
csv_pddf = pd.read_csv(io.StringIO(download.decode('utf-8')),

                       # replace header names
                       header=0,  # do not infer headers from columns
                       names=['Bed', 'Label', 'Geo?', 'Days elapsed since ItemStatusDate', 'Taxon'],

                       converters={'Geo?': to_bool,
                                   'Label': to_bool,
                                   'Days elapsed since ItemStatusDate': days_since
                                   },
                       dtype={'Bed': 'category',
                              'Status': 'category',
                              }
                       )
csv_pddf = csv_pddf.astype({'Days elapsed since ItemStatusDate': 'int32'}, copy=False)
end_csv = time.time()
memory = csv_pddf.memory_usage(deep=True)

''' quick debug

print(f'Time taken to read csv into df: {(end_csv - start_csv):f}.\n'
      f'Memory usage: \n {memory}')
'''
print(csv_pddf.head())

