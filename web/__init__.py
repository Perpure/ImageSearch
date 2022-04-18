from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_url_path='/static')
with open('db_password.txt', 'r') as f:
    password = f.read()
app.config['SQLALCHEMY_DATABASE_URI'] = f'mssql+pyodbc://sa:{password}@DESKTOP-U8HBBNN/hs?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
