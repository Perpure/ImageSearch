from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import IMAGES, UploadSet, configure_uploads
import os

app = Flask(__name__, static_url_path='/static')

with open('db_password.txt', 'r') as f:
    password = f.read()
app.config['SQLALCHEMY_DATABASE_URI'] = f'mssql+pyodbc://sa:{password}@DESKTOP-U8HBBNN/hs?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

images = UploadSet("images", IMAGES)
imgs_path = 'img/'
app.config["UPLOADED_IMAGES_DEST"] = os.path.join('web/static', imgs_path)
app.config["SECRET_KEY"] = os.urandom(24)
configure_uploads(app, [images])

import web.views

