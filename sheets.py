import httplib2
import ssl
import pymysql
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime
import time

httplib2.Http(disable_ssl_certificate_validation=True)
httplib2.disable_ssl_certificate_validation = False
httplib2.ssl_version = ssl.PROTOCOL_TLSv1_2

creds = Credentials.from_service_account_file('C:/Users/kvard/OneDrive/Desktop/SuperJoin/pes-vardhan2404/realtimesynchronization-33ae2b7c097f.json')
service = build('sheets', 'v4', credentials=creds)
spreadsheet_id = '1miFR4fkzlrkDLxWIBzXUvB7lW2exDRa0VQOiV8abwFs'
sheet_range_name = 'Sheet1!A1:D'

db_connection = pymysql.connect(
    host="localhost",
    user="root",
    password="password",
    database="sheet_db"
)
cursor = db_connection.cursor()
print("Database connection successful!")

def fetch_from_sheet(sheet_id, range_name):
    result = service.spreadsheets().values().get(spreadsheetId=sheet_id, range=range_name).execute()
    return result.get('values', [])

def update_google_sheet(sheet_id, range_name, values):
    body = {'values': values}
    result = service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption='RAW',
        body=body
    ).execute()
    print(f"{result.get('updatedCells')} cells updated.")

def fetch_from_db(query):
    cursor.execute(query)
    return cursor.fetchall()

def execute_db_query(query, data=None):
    try:
        if data:
            cursor.execute(query, data)
        else:
            cursor.execute(query)
        db_connection.commit()
    except pymysql.MySQLError as e:
        print(f"Error executing query: {e}")

def sync_data():
    sheet_data = fetch_from_sheet(spreadsheet_id, sheet_range_name)
    sheet_data_dict = {row[0]: {'values': row[1:3], 'timestamp': row[3]} for row in sheet_data if len(row) == 4}
    print(f"Fetched {len(sheet_data)} rows from Google Sheets.")
    db_data = fetch_from_db("SELECT id, value1, value2, last_updated FROM sheet1")
    db_data_dict = {row[0]: {'values': row[1:3], 'timestamp': row[3].strftime('%Y-%m-%d %H:%M:%S')} for row in db_data}
    print(f"Fetched {len(db_data)} rows from the database.")
    updated_sheet_data = []
    for id, sheet_info in sheet_data_dict.items():
        sheet_timestamp = datetime.strptime(sheet_info['timestamp'], '%Y-%m-%d %H:%M:%S')
        
        if id in db_data_dict:
            db_timestamp = datetime.strptime(db_data_dict[id]['timestamp'], '%Y-%m-%d %H:%M:%S')
            if sheet_timestamp > db_timestamp:
                query = "UPDATE sheet1 SET value1 = %s, value2 = %s, last_updated = %s WHERE id = %s"
                execute_db_query(query, (sheet_info['values'][0], sheet_info['values'][1], sheet_timestamp.strftime('%Y-%m-%d %H:%M:%S'), id))
            elif db_timestamp > sheet_timestamp:
                updated_sheet_data.append([id] + list(db_data_dict[id]['values']) + [db_timestamp.strftime('%Y-%m-%d %H:%M:%S')])
        else:
            query = "INSERT INTO sheet1 (id, value1, value2, last_updated) VALUES (%s, %s, %s, %s)"
            execute_db_query(query, (id, sheet_info['values'][0], sheet_info['values'][1], sheet_timestamp.strftime('%Y-%m-%d %H:%M:%S')))
    
    if updated_sheet_data:
        range_name = f'Sheet1!A1:D{len(updated_sheet_data) + 1}'  # Fix range calculation
        update_google_sheet(spreadsheet_id, range_name, updated_sheet_data)

def main():
    while True:
        print("Starting sync...")
        sync_data()
        print("Sync completed. Waiting for the next cycle.")
        time.sleep(30)

if __name__ == "__main__":
    main()

cursor.close()
db_connection.close()
