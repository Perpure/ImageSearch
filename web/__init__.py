from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import IMAGES, UploadSet, configure_uploads
import os
import pathlib

app = Flask(__name__, static_url_path='/static')

with open(os.path.join(pathlib.Path(__file__).parent.resolve(), 'db_password.txt'), 'r') as f:
    password = f.read()

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{password}@localhost:5432/ImageSearch'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['TEXT_RECOGNITION_URL'] = None
app.config['MANUAL_WORDS_UPDATE'] = False

db = SQLAlchemy(app)

images = UploadSet("images", IMAGES)
imgs_path = 'img/'
app.config["UPLOADED_IMAGES_DEST"] = os.path.join('web/static', imgs_path)
app.config["SECRET_KEY"] = os.urandom(24)
configure_uploads(app, [images])

import web.views

