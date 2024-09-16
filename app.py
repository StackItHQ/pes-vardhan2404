from flask import Flask, request, jsonify, render_template
import pymysql
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime

app = Flask(__name__)
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
    password="Vardhan@24",
    database="sheet_db"
)
cursor = db_connection.cursor()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/google_sheets')
def google_sheets():
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_range_name).execute()
    sheet_data = result.get('values', [])
    return render_template('google_sheets.html', sheet_data=sheet_data)

@app.route('/database')
def database():
    cursor.execute("SELECT id, value1, value2, last_updated FROM sheet1")
    db_data = cursor.fetchall()
    return render_template('database.html', db_data=db_data)

@app.route('/update-sheet', methods=['POST'])
def update_sheet():
    data = request.json
    row = int(data['row'])
    id = data['id']
    value1 = data['value1']
    value2 = data['value2']

    range_name = f'Sheet1!A{row}:D{row}'
    values = [[id, value1, value2, datetime.now().strftime('%Y-%m-%d %H:%M:%S')]]
    body = {'values': values}
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='RAW',
        body=body
    ).execute()
    
    return jsonify({'success': True})

@app.route('/delete-sheet', methods=['POST'])
def delete_sheet():
    data = request.json
    row = int(data['row'])
    return jsonify({'success': True})

@app.route('/add-sheet', methods=['POST'])
def add_sheet():
    data = request.json
    id = data['id']
    value1 = data['value1']
    value2 = data['value2']

    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=sheet_range_name,
        valueInputOption='RAW',
        body={'values': [[id, value1, value2, datetime.now().strftime('%Y-%m-%d %H:%M:%S')]]}
    ).execute()
    
    return jsonify({'success': True})

@app.route('/update-db', methods=['POST'])
def update_db():
    data = request.json
    id = data['id']
    value1 = data['value1']
    value2 = data['value2']

    query = "UPDATE sheet1 SET value1 = %s, value2 = %s WHERE id = %s"
    try:
        cursor.execute(query, (value1, value2, id))
        db_connection.commit()
        return jsonify({'success': True})
    except pymysql.MySQLError as e:
        print(f"Error executing query: {e}")
        return jsonify({'success': False})

@app.route('/add-db', methods=['POST'])
def add_db():
    data = request.json
    id = data['id']
    value1 = data['value1']
    value2 = data['value2']

    query = "INSERT INTO sheet1 (id, value1, value2, last_updated) VALUES (%s, %s, %s, NOW())"
    try:
        cursor.execute(query, (id, value1, value2))
        db_connection.commit()
        return jsonify({'success': True})
    except pymysql.MySQLError as e:
        print(f"Error executing query: {e}")
        return jsonify({'success': False})

@app.route('/delete-db', methods=['POST'])
def delete_db():
    data = request.json
    id = data['id']

    query = "DELETE FROM sheet1 WHERE id = %s"
    try:
        cursor.execute(query, (id,))
        db_connection.commit()
        return jsonify({'success': True})
    except pymysql.MySQLError as e:
        print(f"Error executing query: {e}")
        return jsonify({'success': False})

if __name__ == '__main__':
    app.run(debug=True)
