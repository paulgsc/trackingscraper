#!/usr/bin/env python
# coding: utf-8

# In[1]:


# required libararies
import pandas as pd;
from googleapiclient.discovery import build;
from google_auth_oauthlib.flow import InstalledAppFlow,Flow;
from google.auth.transport.requests import Request;
import os;
import pickle;


# In[4]:


"""
Authenticated Google API by a downloaded JSON file. 
by using this file, we created ‘token.pickle’ 
file which will be stored in our pc 
for future use and whenever this pickle 
file will expire our code will refresh the file.
"""
FILE_NAME = 'client_secret_file.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def main(gsheetId,SAMPLE_RANGE_NAME):
    global values_input, service
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                FILE_NAME, SCOPES) # here enter the name of your downloaded JSON file
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    
     # Call the Sheets API
    sheet = service.spreadsheets()
    result_input = sheet.values().get(spreadsheetId=gsheetId,
                                range=SAMPLE_RANGE_NAME).execute()
    values_input = result_input.get('values', [])

    if not values_input and not values_expansion:
        print('No data found.')
    return pd.DataFrame(values_input[1:], columns=values_input[0])


