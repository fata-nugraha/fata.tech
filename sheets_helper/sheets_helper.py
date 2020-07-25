import os
import redis
from google.oauth2 import service_account
from googleapiclient.discovery import build
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'gsheet.json'
credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
r = redis.Redis(host=os.environ.get("REDIS_HOST"), port=17990, password=os.environ.get("REDIS_PASS"), health_check_interval=30)

def update_sheets(val):
    service = build('sheets', 'v4', credentials=credentials)
    spreadsheet_id = os.environ.get("SHEET_ID")
    range_ = 'Jenius Rates!B{row}:H{row}'.format(row=r.get("row").decode('ascii'))
    batch_update_values_request_body = {
        "data": [
            {
                "majorDimension": "ROWS",
                "range": range_,
                "values": [val]
            }
        ],
        "valueInputOption": "RAW"
    }
    request = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id, body=batch_update_values_request_body)
    response = request.execute()
    r.incr("row")
    return response['responses'][0]['updatedRange']

def convert_currencies(texts):
    currencies = ["AUD", "EUR", "GBP", "HKD", "JPY", "SGD", "USD"]
    retval = []
    for currency in currencies:
        index = texts.index(currency)
        if currency=="JPY":
            retval.append(float(texts[index+1].replace(",", ".")))
        else:
            retval.append(int(texts[index+1].replace(".", "")))
    return retval