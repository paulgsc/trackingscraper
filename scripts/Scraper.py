#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from selenium import webdriver
from bs4 import BeautifulSoup
import urllib.request
import time
import pandas as pd
import re


# In[ ]:

def scrape_metro_tracking(url):
    driver=webdriver.Chrome()
    driver.implicitly_wait(.1)
    try:
        driver.get(url)
        html_source=driver.page_source
        driver.close()
    except:
        print('Alert! Incorrect Reference included in list, url link is invalid')
        return

    dfs=pd.read_html(html_source)
    dfs[1].columns=dfs[0].columns
    df_metro=dfs[1].iloc[:1, :]
    df_metro.insert(0,'Tracking',[re.sub(r'^.*id=','',url)])
    return df_metro

def scrape_tracking(url):
    driver=webdriver.Chrome()
    driver.implicitly_wait(1)
    try:
    	driver.get(url)
    	button=driver.find_element('xpath', '//*[@id="btnSubmit"]')
    	button.click()
    	# time.sleep(2)
    	html_source=driver.page_source
    except:
    	print('Alert! Incorrect Reference included in list, url link is invalid')
    	return

    dfs=pd.read_html(html_source)
    result=' '.join(map(str,dfs))
    result=re.sub(r"(?:\n|\\n\d{2}|\\n\d{1}|NaN)",'',result)
    result=' '.join(map(str,result.split()))
    shipment_created=result.find('Shipment created.')>0
    shipped=result.find('IN TRANSIT')>0
    delivered=result.find('SHIPMENT DELIVERED')>0
    multiple_list=result.find('Multiple Shipments were found')>0
    soup = BeautifulSoup(html_source, 'html.parser')
    try:
        message_list=soup.find("span", {"id":"lblStatus"}).text
    except:
        message_list='null'	
    return {'shipment_created':shipment_created, 'shipped':shipped, 'delivered':delivered, 'Multiple Shipments': multiple_list, 'Response': message_list}

