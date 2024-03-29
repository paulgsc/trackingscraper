#!/usr/bin/env python
# coding: utf-8

# In[1]:


# import os;
from pathlib import Path;
from scripts.Google import Create_Service;
from scripts.readSheets import *;
import pandas as pd;
import numpy as np;
import re;




FOLDER_PATH = Path.cwd()
FILE_NAME = 'client_secret_file.json'
API_NAME = 'sheets'
API_VERSION = 'v4'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']



# In[4]:



CLIENT_SECRET_FILE = FOLDER_PATH / FILE_NAME
# CLIENT_SECRET_FILE = os.path.join(FOLDER_PATH, 'Client_Secret.json')

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

def SheetsNew():
    """
    To specify Google Sheets file basic settings and as well as configure default worksheets
    """
    sheet_body = {
        'properties': {
            'title': 'ApiSheetsNew',
            'locale': 'en_US', # optional
            'timeZone': 'America/Los_Angeles'
            }
        ,
        'sheets': [
            {
                'properties': {
                    'title': 'Data'
                }
            },
            {
                'properties': {
                    'title': 'Pivot'
                }
            }
        ]
    }

    sheets_file2 = service.spreadsheets().create(body=sheet_body).execute()
    return {'Url':sheets_file2['spreadsheetUrl'],'gsheetId':sheets_file2['spreadsheetId'],'sheet_names':sheets_file2['sheets']}



# In[11]:

def createNewSpreadsheet():   
    sheet_body = {
        'properties': {
            'title': 'ApiSheetsNew',
            'locale': 'en_US', # optional
            'timeZone': 'America/Los_Angeles'
            }
        ,
        'sheets': [
            {
                'properties': {
                    'title': 'default'
                }
            }
        ]
    }

    sheets_file2 = service.spreadsheets().create(body=sheet_body).execute()
    return {'Url':sheets_file2['spreadsheetUrl'],'gsheetId':sheets_file2['spreadsheetId'],'sheet_names':sheets_file2['sheets']}


def copySheets():
    url='https://docs.google.com/spreadsheets/d/1z0U-WEYjoc8ByMUECr_zNSxTMPAVgyg3_w9pPuoVWDE/edit#gid=1891707339'
    sourcegSheetId=getSheetId(url)
    df = getSheetProperties(url)
    worksheet_id=list(map(lambda x: df[x]['properties']['sheetId'],range(len(df))))
    worksheet_names=list(map(lambda x: df[x]['properties']['title'],range(len(df))))
    df1 = createNewSpreadsheet()
    destgSheetId=getSheetId(df1['Url'])

    for i in worksheet_id:
        print('copying ' + str(i))
       	service.spreadsheets().sheets().copyTo(
        spreadsheetId=sourcegSheetId,
        sheetId=i,
        body={'destinationSpreadsheetId':destgSheetId}
        ).execute()
        copy_url = df1['Url']
        prop = getSheetProperties(copy_url)
        names=list(map(lambda x: prop[x]['properties']['title'],range(len(prop))))
        sheet_ids=list(map(lambda x: prop[x]['properties']['sheetId'],range(len(prop))))
        names=list(map(lambda x: x.replace('Copy of ',''),names))
        for indx, sheet_id in enumerate(sheet_ids):
            service.spreadsheets().batchUpdate(
            spreadsheetId=destgSheetId,
            body=request_template(sheet_id,names[indx])
            ).execute()
    return df1['Url']

def file_time_stamp(pattern):

    """
    Createing nest file
    """

    # read export
    # first define path
    location = 'Downloads'
    file_path = Path.cwd() / location

    # next assign path and define pattern of file name
    downloaded_file = Path.cwd() / 'Downloads'
    pattern = '*'+pattern+'*'

    # use funciton to get latest time of file
    return {'time': getLatestFileNameTime(downloaded_file, pattern) , 'file':getLatestFileName(downloaded_file,pattern)}

def writeDataToSheetDf(worksheet_name,gsheetId,df):
    cell_range_insert = 'A1'
    
    # Replace Null values
    df.replace(np.nan,'',inplace=True)

    # Convert all date columns to string type
    for col in  df.select_dtypes(include=['datetime64']).columns.tolist():
        df[col] = df[col].astype(str)

    response_date = service.spreadsheets().values().append(
        spreadsheetId=gsheetId,
        valueInputOption='RAW',
        range=worksheet_name,
        body=dict(
            majorDimension = 'ROWS',
            values = df.T.reset_index().T.values.tolist()
        )
    ).execute()



def writeDataToSheet(worksheet_name,gsheetId,file_name,sheet_name):
    cell_range_insert = 'A1'
    # read file in path
    file_string = str(file_name)
    if 'xls' not in file_string:
    	df = pd.read_csv(file_name)
    else:
    	df = pd.read_excel(file_name,sheet_name,index_col=False)

    # Replace Null values
    df.replace(np.nan,'',inplace=True)

    # Convert all date columns to string type
    for col in  df.select_dtypes(include=['datetime64']).columns.tolist():
        df[col] = df[col].astype(str)

    response_date = service.spreadsheets().values().append(
        spreadsheetId=gsheetId,
        valueInputOption='RAW',
        range=worksheet_name,
        body=dict(
            majorDimension = 'ROWS',
            values = df.T.reset_index().T.values.tolist()
        )
    ).execute()



# In[8]:


# method to add inv for nest pivot
def addInvValues(df):
    # read the fabric inventory
    df_inv = main('1tOkainSd6Q_cdwyPMpAyvs3ze2fCU20yhM1yp4VEHRc','Fabrics Master Data!A:E')
    options = ['Tony Stock','Justin Stock']
    for i in range(0,len(options)):
        df_loc = df_inv.loc[df_inv['Stock']==options[i]]
         # merge inventory to data table
        df = pd.merge(df,df_loc[['Fabric #','Fabric Yards']],on='Fabric #', how='left')
        temp = options[i] + ' Fabric Yards'
        df = df.rename(columns={"Fabric Yards": temp})
        df[temp] = df[temp].astype(str).astype(float)
      

    # get inv per wo line for pivot view cal field
    

    # so_count = []
    # list1 = nest_file['Sale Order Line/Qty to Produce'].tolist()
    # tempList = nest_file['Fabric Yards'].tolist()
    # for x in tempList:
    #     so_count.append(tempList.count(x))
    # ar1 = np.array(list1)
    # ar2 = np.array(so_count)
    # ar3 = ar1 / ar2
    # nest_file['Fabric Inv Per WO line'] = ar3
    return df


# method to create new sheets  tabs

def add_sheets(gsheetId, sheet_name):
    spreadsheets = service.spreadsheets()
    try:
        request_body = {
            'requests': [{
                'addSheet': {
                    'properties': {
                        'title': sheet_name,
                        'tabColor': {
                            'red': 0.44,
                            'green': 0.99,
                            'blue': 0.50
                        }
                    }
                }
            }]
        }

        response = spreadsheets.batchUpdate(
            spreadsheetId=gsheetId,
            body=request_body
        ).execute()

        return response
    except Exception as e:
        print(e)

def getSheetProperties(Url):
   
    gsheetId = re.sub(r'(?i)(^.+?/d/|/edit.*$)','',Url)
    print('this is the gsheetId ' + gsheetId)
    sheet_metadata = service.spreadsheets().get(spreadsheetId=gsheetId).execute()
    return sheet_metadata.get('sheets', '')

def getSheetId(Url):
    return re.sub(r'(?i)(^.+?/d/|/edit.*$)','',Url)


def clearSheets(gsheetId,worksheet_name):
    service.spreadsheets().values().clear(
        spreadsheetId = gsheetId,
        range=worksheet_name
    ).execute()

def clearSheetsRange(gsheetId,worksheet_name,cell_range):    
    service.spreadsheets().values().clear(
        spreadsheetId = gsheetId,
        range=worksheet_name + '/s' + cell_range
    ).execute()

def getLatestFileName (path: Path, pattern: str = "*"):
    files = path.rglob(pattern)
    return max(files,key=lambda x: x.stat().st_ctime)
def getLatestFileNameTime (path: Path, pattern: str = "*"):
    files = path.rglob(pattern)
    return max(files,key=lambda x: x.stat().st_ctime).stat().st_ctime

def request_template(sheet_id, sheet_name):
    request_body={
        'requests': [
            {
                'updateSheetProperties': {
                    'properties': {
                        'sheetId': sheet_id,
                        'title': sheet_name
                    },
                    'fields': 'title'
                }
            }
        ]
    }
    return request_body


def copyDiligentTemplate():
    url = copySheets()
    prop = getSheetProperties(url)
    names=list(map(lambda x: prop[x]['properties']['title'],range(len(prop))))
    sheet_ids=list(map(lambda x: prop[x]['properties']['sheetId'],range(len(prop))))
    names=list(map(lambda x: x.replace('Copy of ',''),names))
    gsheetId = getSheetId(url)
    for indx, sheet_id in enumerate(sheet_ids):
        service.spreadsheets().batchUpdate(
        spreadsheetId=gsheetId,
        body=request_template(sheet_id,names[indx])
        ).execute()
    return url

def createNestFile(pattern):
    """
    Creating nest file
    """

    # read export
    # first define path
    location = 'Downloads'
    file_path = Path.cwd() / location

    # next assign path and define pattern of file name
    downloaded_file = Path.cwd() / 'Downloads'
    pattern = '*'+pattern+'*'

    # use funciton to get latest file
    myFile = getLatestFileName(downloaded_file,pattern)

    # next read the contents of the file must be either csv or excel file
    if 'xls' not in str(myFile):
        nest_file = pd.read_csv(myFile,index_col=False)
    else:
        nest_file = pd.read_excel(myFile,sheet_name=0,index_col=False)
    return nest_file



def createCoversData(nest_file):
    # Mirror excel countif to generate sliced so line qty to produce
    tempList = nest_file['Sale Order Line/Product/Display Name'].fillna('blanks').tolist()
    bondi_chicory = []
    covers_rename = []
    for x in range(0,len(tempList)):
        if (re.search('(?i)(?:mst1 bondi|mst1 chicory)',tempList[x])!=None):
            bondi_chicory.append((re.search('(?i)(?:mst1 bondi|mst1 chicory)',tempList[x])).group(0))
        else:
            bondi_chicory.append('other')
    nest_file['BONDI|CHICORY'] = bondi_chicory

    covers_rename = nest_file['Product/Display Name'].fillna('blanks').tolist()
    for x in range(0,len(covers_rename)):
        covers_rename[x] = re.sub(r'(?i)(?:\[.+\]\s|\sv2$)','',covers_rename[x])

    nest_file['Covers'] = covers_rename
    rename = nest_file['Sale Order Line/Product/Display Name'].fillna('blanks').tolist()
    rename2 = nest_file['Product/Display Name'].fillna('blanks').tolist()
    for x in range(0,len(rename)):
        rename[x] = re.sub(r'(?i)(.*\]\s)','',rename[x])
        rename2[x] = re.sub(r'(?i)(.*\]\s)','',rename2[x])
    to_assign = {'Product Name':rename,'Component Name':rename2}
    nest_file = nest_file.assign(**to_assign)

    # use numpy to create countif of so quantity
    so_count = []
    list1 = nest_file['Sale Order Line/Qty to Produce'].tolist()
    tempList = nest_file['Sale Order Line/ID'].tolist()
    for x in tempList:
        so_count.append(tempList.count(x))
    ar1 = np.array(list1)
    ar2 = np.array(so_count)
    ar3 = ar1 / ar2
    nest_file['SO Line Product Qty'] = ar3
    ar4 =  nest_file['Quantity To Be Produced'].tolist()
    nest_file['Qty per SO qty'] = ar4 / ar1

    """
    sewing wo data detailed table

    """
    # creating column for fabric number

    # read the fabric color and number for mapping
    fabric_color = main('1tOkainSd6Q_cdwyPMpAyvs3ze2fCU20yhM1yp4VEHRc','Fabric Color!A:B').dropna()
    color_att = (nest_file['Sale Order Line/Product Attributes'].astype(str)+', ').str.extract(r'Color:\s(.+?),\s')
    color_att.columns = ['color']
    kwargs = {'Fabric Color': color_att['color']}
    nest_file = nest_file.assign(**kwargs) 
    nest_file = nest_file.merge(fabric_color,left_on='Fabric Color',right_on='CABA NAME',sort=False).drop('CABA NAME',axis=1)


    # s = []
    # for x in range(0,len(colorList)):
    #     s.append(re.sub(',.*','',test[x].split('Color: ')[1]))
    # d = {'Color': s}
    # color_att = pd.DataFrame(data=d)

    # add target week column
    df_week = nest_file['Sale Order Line/Commitment Date']
    df_week = pd.to_datetime(df_week, infer_datetime_format=True)  
    df_week = df_week.dt.tz_localize('UTC')
    a=df_week.dt.strftime('%W').fillna(0)
    a = np.array(a)
    a = a.astype(int)+1
    a = pd.DataFrame({'target week': a.tolist()})
    nest_file['So Target Week'] = a



    # rename covers to give chicory accent pillow size
    accentAttr = nest_file['Sale Order Line/Product Attributes'].fillna('blanks').tolist()
    for x in range(0,len(accentAttr)):
        accentAttr[x] =  re.sub(r'(?i)(?:.*\spillow\soptions\W\s|\sw/insert)','',accentAttr[x])
    accentAttr = pd.DataFrame({'attr':accentAttr}) 
    df4 = pd.DataFrame({'prod':nest_file['Covers']})
    df = nest_file['Covers'].str.cat(accentAttr['attr'],sep=' ')
    df1  = pd.DataFrame({'attrProduct':df})
    df5 = df4.where(~(df4['prod'].str.match('(.*for chicory.*)',case=False)),df1['attrProduct'],axis=0)
    nest_file['Covers'] =  df5
    nest_file = addInvValues(nest_file)
    nest_file['Fabric #'] = nest_file['Fabric #'].fillna(0)
    nest_file['Fabric #'] = nest_file['Fabric #'].astype(str).astype(int)
    return nest_file

def createSummaData(nest_file):
    # Mirror excel countif to generate sliced so line qty to produce
    tempList = nest_file['Sale Order Line/Product/Display Name'].fillna('blanks').tolist()
    bondi_chicory = []
    for x in range(0,len(tempList)):
        if (re.search('(?i)(?:mst1 bondi|mst1 chicory)',tempList[x])!=None):
            bondi_chicory.append((re.search('(?i)(?:mst1 bondi|mst1 chicory)',tempList[x])).group(0))
        else:
            bondi_chicory.append('other')
    nest_file['BONDI|CHICORY'] = bondi_chicory

    anaAeroAce = []
    for x in range(0,len(tempList)):
        if (re.search('(?i)(?:mst1 ana|mst1 ace|mst1 aero)',tempList[x])!=None):
            anaAeroAce.append((re.search('(?i)(?:mst1 ana|mst1 ace|mst1 aero)',tempList[x])).group(0))
        else:
            anaAeroAce.append('other')
    nest_file['ANA|AERO|ACE'] = anaAeroAce

    rename = nest_file['Sale Order Line/Product/Display Name'].fillna('blanks').tolist()
    rename2 = nest_file['Product/Display Name'].fillna('blanks').tolist()
    for x in range(0,len(rename)):
        rename[x] = re.sub(r'(?i)(.*\]\s)','',rename[x])
        rename2[x] = re.sub(r'(?i)(.*\]\s)','',rename2[x])
    to_assign = {'Product Name':rename,'Component Name':rename2}
    nest_file = nest_file.assign(**to_assign)

    # use numpy to create countif of so quantity
    so_count = []
    list1 = nest_file['Sale Order Line/Qty to Produce'].tolist()
    tempList = nest_file['Sale Order Line/ID'].tolist()
    for x in tempList:
       so_count.append(tempList.count(x))
    ar1 = np.array(list1)
    ar2 = np.array(so_count)
    ar3 = ar1 / ar2
    nest_file['SO Line Product Qty'] = ar3
    ar4 =  nest_file['Quantity To Be Produced'].tolist()
    #nest_file['Qty per SO qty'] = ar4 / ar1

    """
    Summa wo data detailed table

        """
    # creating column for fabric number

    fabric_no = (nest_file['First Raw Material/Display Name'].astype(str)+', ').str.extract(r'\]\s(\d{3}?)\s')
    fabric_no.columns = ['color']
    kwargs = {'Fabric #': fabric_no['color']}
    nest_file = nest_file.assign(**kwargs) 



    # add target week column
    df_week = nest_file['Sale Order Line/Commitment Date']
    df_week = pd.to_datetime(df_week, infer_datetime_format=True)  
    df_week = df_week.dt.tz_localize('UTC')
    a=df_week.dt.strftime('%W').fillna(0)
    a = np.array(a)
    a = a.astype(int)+1
    a = pd.DataFrame({'target week': a.tolist()})
    nest_file['So Target Week'] = a
    nest_file = addInvValues(nest_file)
    nest_file['Fabric #'] = nest_file['Fabric #'].fillna(0)
    nest_file['Fabric #'] = nest_file['Fabric #'].astype(str).astype(int)

    return nest_file

def createSewingPivot(dict,nest_file):


    gsheetId = dict['gsheetId']
    sheetProperties = dict['sheet_names']
    Url = dict['Url']
    sheet_names = [sheetProperties[0]['properties']['title'],sheetProperties[1]['properties']['title']]
    sheetIds = [sheetProperties[0]['properties']['sheetId'],sheetProperties[1]['properties']['sheetId']]


    # rename worksheet to Sewing
    request_body = {
      'requests': [
         {
           'updateSpreadsheetProperties': {
                'properties':  {
                     'title': 'Sewing Nesting API'
                },
              'fields': 'title'   
           }

        } 
      ]

    }
    request = service.spreadsheets().batchUpdate(
        spreadsheetId=gsheetId,
        body=request_body
    ).execute()



    # In[ ]:


    # PivotTable JSON Template
    request_body = {
        'requests': [
            {
                'updateCells': {
                    'rows': {
                        'values': [
                            {
                                'pivotTable': {
                                    # Data Source
                                    'source': {
                                        'sheetId': sheetIds[0],
                                        'startRowIndex': 0,
                                        'startColumnIndex': 0,
                                        'endRowIndex': len(nest_file),
                                        'endColumnIndex': len(nest_file.columns) # base index is 1
                                    },

                                    # Rows Field(s)
                                    'rows': [
                                        # row field #1
                                        {
                                            'sourceColumnOffset': nest_file.columns.get_loc('Fabric #'),
                                            'showTotals': True, # display subtotals
                                            'sortOrder': 'ASCENDING',
                                            'repeatHeadings': False,
                                            'label': 'Fabric #',
                                         },

                                        {
                                            'sourceColumnOffset': nest_file.columns.get_loc('Lot/Serial Number/Lot/Serial Number'),
                                            'showTotals': True, # display subtotals
                                            'sortOrder': 'ASCENDING',
                                            'repeatHeadings': False,
    #                                         'label': 'Product List',
                                        },

                                        {
                                            'sourceColumnOffset': nest_file.columns.get_loc('Sale Order Line/Product/Display Name'),
                                            'showTotals': False, # display subtotals
                                            'sortOrder': 'ASCENDING',
                                            'repeatHeadings': False,
    #                                         'label': 'Product List',
                                        },

                                        {
                                            'sourceColumnOffset': nest_file.columns.get_loc('Sale Order Line/Qty to Produce'),
                                            'showTotals': False, # display subtotals
                                            'sortOrder': 'ASCENDING',
                                            'repeatHeadings': False,
    #                                         'label': 'Product List',
                                        }

    #                                     {
    #                                         'sourceColumnOffset': 16,
    #                                         'showTotals': False, # display subtotals
    #                                         'sortOrder': 'ASCENDING',
    #                                         'repeatHeadings': False,
    # #                                         'label': 'Product List',
    #                                     }                   

                                    ],

    #                                 Columns Field(s)
                                    'columns': [
                                        # column field #1
                                        {
                                            'sourceColumnOffset': nest_file.columns.get_loc('Covers'),
                                            'sortOrder': 'ASCENDING', 
                                            'showTotals': True
                                        }
                                    ],

                                    'criteria': {
                                        nest_file.columns.get_loc('Operation/Display Name'): {
                                            'visibleValues': [
                                                'Sewing QC/Prep'
                                            ]
                                        },

                                        nest_file.columns.get_loc('BONDI|CHICORY'): {
                                            'visibleValues': [
                                                'MST1 Bondi', 'MST1 Chicory'
                                            ]
                                        },
                                           nest_file.columns.get_loc('Assigned to/Display Name'): {
                                            'visibleValues': [
                                                'FALSE'
                                            ]
                                        },

    #                                     11: {
    #                                         'condition': {
    #                                             'type': 'NUMBER_BETWEEN',
    #                                             'values': [
    #                                                 {
    #                                                     'userEnteredValue': '10000'
    #                                                 },
    #                                                 {
    #                                                     'userEnteredValue': '100000'
    #                                                 }
    #                                             ]
    #                                         },
    #                                         'visibleByDefault': True
    #                                     }
                                    },

                                    # Values Field(s)
                                    'values': [
                                        # value field #1
                                        {
                                            'sourceColumnOffset': nest_file.columns.get_loc('Quantity To Be Produced'),
                                            'summarizeFunction': 'SUM',
                                            'name': 'Covers Qty:'
                                        }
                                    ],

                                    'valueLayout': 'HORIZONTAL'
                                }
                            }
                        ]
                    },

                    'start': {
                        'sheetId': sheetIds[1],
                        'rowIndex': 0, # 4th row
                        'columnIndex': 0 # 3rd column
                    },
                    'fields': 'pivotTable'
                }
            }
        ]
    }

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=gsheetId,
        body=request_body
    ).execute()


def createSummaPivot(dict,nest_file):


    gsheetId = dict['gsheetId']
    sheetProperties = dict['sheet_names']
    Url = dict['Url']
    sheet_names = [sheetProperties[0]['properties']['title'],sheetProperties[1]['properties']['title']]
    sheetIds = [sheetProperties[0]['properties']['sheetId'],sheetProperties[1]['properties']['sheetId']]

    # rename worksheet to Summa
    request_body = {
      'requests': [
         {
           'updateSpreadsheetProperties': {
                'properties':  {
                     'title': 'Summa Nesting API'
                },
              'fields': 'title'   
           }

        } 
      ]

    }
    request = service.spreadsheets().batchUpdate(
        spreadsheetId=gsheetId,
        body=request_body
    ).execute()
    


    """
    create pivot table using data inserted to sheets

    """

    # PivotTable JSON Template
    request_body = {
        'requests': [
            {
                'updateCells': {
                    'rows': {
                        'values': [
                            {
                                'pivotTable': {
                                    # Data Source
                                    'source': {
                                        'sheetId': sheetIds[0],
                                        'startRowIndex': 0,
                                        'startColumnIndex': 0,
                                        'endRowIndex': len(nest_file),
                                        'endColumnIndex': len(nest_file.columns) # base index is 1
                                    },

                                    # Rows Field(s)
                                    'rows': [
                                        # row field #1
                                        {
                                            'sourceColumnOffset': nest_file.columns.get_loc('Fabric #'),
                                            'showTotals': True, # display subtotals
                                            'sortOrder': 'ASCENDING',
                                            'repeatHeadings': False,
                                            'label': 'Fabric #',
                                         },

                                        {
                                            'sourceColumnOffset': nest_file.columns.get_loc('Sale Order Line/Product/Display Name'),
                                            'showTotals': True, # display subtotals
                                            'sortOrder': 'ASCENDING',
                                            'repeatHeadings': False,
    #                                         'label': 'Product List',
                                        },

                                        {
                                            'sourceColumnOffset': nest_file.columns.get_loc('Lot/Serial Number/Lot/Serial Number'),
                                            'showTotals': False, # display subtotals
                                            'sortOrder': 'ASCENDING',
                                            'repeatHeadings': False,
    #                                         'label': 'Product List',
                                        },

                                        {
                                            'sourceColumnOffset': nest_file.columns.get_loc('Sale Order Line/Product Attributes'),
                                            'showTotals': False, # display subtotals
                                            'sortOrder': 'ASCENDING',
                                            'repeatHeadings': False,
    #                                         'label': 'Product List',
                                        },
                                        
                                        {
                                            'sourceColumnOffset': nest_file.columns.get_loc('Sale Order Line/Qty to Produce'),
                                            'showTotals': False, # display subtotals
                                            'sortOrder': 'ASCENDING',
                                            'repeatHeadings': False,
    #                                         'label': 'Product List',
                                        }

    #                                     {
    #                                         'sourceColumnOffset': 16,
    #                                         'showTotals': False, # display subtotals
    #                                         'sortOrder': 'ASCENDING',
    #                                         'repeatHeadings': False,
    # #                                         'label': 'Product List',
    #                                     }                   

                                    ],

    #                                 Columns Field(s)
#                                     'columns': [
#                                         # column field #1
#                                         {
#                                             'sourceColumnOffset': nest_file.columns.get_loc('Covers'),
#                                             'sortOrder': 'ASCENDING', 
#                                             'showTotals': True
#                                         }
#                                     ],

                                    'criteria': {
#                                         nest_file.columns.get_loc('Operation/Display Name'): {
#                                             'visibleValues': [
#                                                 'Sewing QC/Prep'
#                                             ]
#                                         },

                                        nest_file.columns.get_loc('ANA|AERO|ACE'): {
                                            'visibleValues': [
                                                'MST1 ANA', 'MST1 Aero, MST1 Ace'
                                            ]
                                        },
                                           nest_file.columns.get_loc('Assigned to/Display Name'): {
                                            'visibleValues': [
                                                'FALSE'
                                            ]
                                        },

    #                                     11: {
    #                                         'condition': {
    #                                             'type': 'NUMBER_BETWEEN',
    #                                             'values': [
    #                                                 {
    #                                                     'userEnteredValue': '10000'
    #                                                 },
    #                                                 {
    #                                                     'userEnteredValue': '100000'
    #                                                 }
    #                                             ]
    #                                         },
    #                                         'visibleByDefault': True
    #                                     }
                                    },

                                    # Values Field(s)
                                    'values': [
                                        # value field #1
                                        {
                                            'sourceColumnOffset': nest_file.columns.get_loc('Quantity To Be Produced'),
                                            'summarizeFunction': 'SUM',
                                            'name': 'SO Line Product Qty'
                                        }
                                    ],

                                    'valueLayout': 'HORIZONTAL'
                                }
                            }
                        ]
                    },

                    'start': {
                        'sheetId': sheetIds[1],
                        'rowIndex': 0, # 4th row
                        'columnIndex': 0 # 3rd column
                    },
                    'fields': 'pivotTable'
                }
            }
        ]
    }

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=gsheetId,
        body=request_body
    ).execute()
    
def createSummaPivotConsumption(dict,Url,nest_file):

    gsheetId = dict['gsheetId']
    add_sheets(gsheetId, 'Pivot Fabric Consumption')
    print('next is get sheet')
    sheetProperties = getSheetProperties(Url)
    print('get sheet is done')
    sheet_names = [sheetProperties[0]['properties']['title'],sheetProperties[2]['properties']['title']]
    sheetIds = [sheetProperties[0]['properties']['sheetId'],sheetProperties[2]['properties']['sheetId']]
    print(sheetIds)
    print(Url)


    """
    create pivot table using data inserted to sheets

    """

    # PivotTable JSON Template
    request_body = {
        'requests': [
            {
                'updateCells': {
                    'rows': {
                        'values': [
                            {
                                'pivotTable': {
                                    # Data Source
                                    'source': {
                                        'sheetId': sheetIds[0],
                                        'startRowIndex': 0,
                                        'startColumnIndex': 0,
                                        'endRowIndex': len(nest_file),
                                        'endColumnIndex': len(nest_file.columns) # base index is 1
                                    },

                                    # Rows Field(s)
                                    'rows': [
                                        # row field #1
                                        {
                                            'sourceColumnOffset': nest_file.columns.get_loc('Fabric #'),
                                            'showTotals': True, # display subtotals
                                            'sortOrder': 'ASCENDING',
                                            'repeatHeadings': False,
                                            'label': 'Fabric #',
                                         },

                                        {
                                            'sourceColumnOffset': nest_file.columns.get_loc('Sale Order Line/Product/Display Name'),
                                            'showTotals': True, # display subtotals
                                            'sortOrder': 'ASCENDING',
                                            'repeatHeadings': False,
    #                                         'label': 'Product List',
                                        },

                                        {
                                            'sourceColumnOffset': nest_file.columns.get_loc('Lot/Serial Number/Lot/Serial Number'),
                                            'showTotals': False, # display subtotals
                                            'sortOrder': 'ASCENDING',
                                            'repeatHeadings': False,
    #                                         'label': 'Product List',
                                        },

                                        {
                                            'sourceColumnOffset': nest_file.columns.get_loc('Sale Order Line/Product Attributes'),
                                            'showTotals': False, # display subtotals
                                            'sortOrder': 'ASCENDING',
                                            'repeatHeadings': False,
    #                                         'label': 'Product List',
                                        },
                                        
                                        {
                                            'sourceColumnOffset': nest_file.columns.get_loc('Sale Order Line/Qty to Produce'),
                                            'showTotals': False, # display subtotals
                                            'sortOrder': 'ASCENDING',
                                            'repeatHeadings': False,
    #                                         'label': 'Product List',
                                        }

    #                                     {
    #                                         'sourceColumnOffset': 16,
    #                                         'showTotals': False, # display subtotals
    #                                         'sortOrder': 'ASCENDING',
    #                                         'repeatHeadings': False,
    # #                                         'label': 'Product List',
    #                                     }                   

                                    ],

    #                                 Columns Field(s)
#                                     'columns': [
#                                         # column field #1
#                                         {
#                                             'sourceColumnOffset': nest_file.columns.get_loc('Covers'),
#                                             'sortOrder': 'ASCENDING', 
#                                             'showTotals': True
#                                         }
#                                     ],

                                    'criteria': {
#                                         nest_file.columns.get_loc('Operation/Display Name'): {
#                                             'visibleValues': [
#                                                 'Sewing QC/Prep'
#                                             ]
#                                         },

                                        nest_file.columns.get_loc('ANA|AERO|ACE'): {
                                            'visibleValues': [
                                                'MST1 ANA', 'MST1 Aero, MST1 Ace'
                                            ]
                                        },
                                           nest_file.columns.get_loc('Assigned to/Display Name'): {
                                            'visibleValues': [
                                                'FALSE'
                                            ]
                                        },

    #                                     11: {
    #                                         'condition': {
    #                                             'type': 'NUMBER_BETWEEN',
    #                                             'values': [
    #                                                 {
    #                                                     'userEnteredValue': '10000'
    #                                                 },
    #                                                 {
    #                                                     'userEnteredValue': '100000'
    #                                                 }
    #                                             ]
    #                                         },
    #                                         'visibleByDefault': True
    #                                     }
                                    },

                                    # Values Field(s)
                                    'values': [
                                        # value field #1
                                        {
                                            'sourceColumnOffset': nest_file.columns.get_loc('Quantity To Be Produced'),
                                            'summarizeFunction': 'SUM',
                                            'name': 'SO Line Product Qty'
                                        }
                                    ],

                                    'valueLayout': 'HORIZONTAL'
                                }
                            }
                        ]
                    },

                    'start': {
                        'sheetId': sheetIds[1],
                        'rowIndex': 0, # 4th row
                        'columnIndex': 0 # 3rd column
                    },
                    'fields': 'pivotTable'
                }
            }
        ]
    }

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=gsheetId,
        body=request_body
    ).execute()
    












