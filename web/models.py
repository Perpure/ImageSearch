import shutil
import hashlib
import os
import json
from datetime import datetime
from uuid import uuid4
from flask import url_for
from web import db, app

ImageObjects = db.Table('ImageObjects', db.Model.metadata,
                        db.Column('image_id', db.Integer, db.ForeignKey('Image.id')),
                        db.Column('object_id', db.Integer, db.ForeignKey('Object.id')))

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(32), nullable=False)
    info = db.Column(db.String())
    publications = db.relationship('Publication', backref='author', lazy='joined')

    def __init__(self, login, password):
        self.login = login
        self.name = login
        self.channel_info = ""
        self.password = hashlib.sha512(password.encode("utf-8")).hexdigest()
        db.session.add(self)
        db.session.commit()

    def check_pass(self, password):
        hash = hashlib.sha512(password.encode("utf-8")).hexdigest()
        return self.password == hash

    def change_name(self, name):
        self.name = name
        db.session.add(self)
        db.session.commit()

    def change_info(self, info):
        self.info = info
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get(id=None, login=None):
        if login:
            return User.query.filter_by(login=login).first()
        if id:
            return User.query.get(id)
        return User.query.all()

class Publication(db.Model):
    __tablename__ = 'Publication'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(), unique=False, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    images = db.relationship('Image', backref='publication', lazy='joined')

    def __init__(self, user, text='', image_paths=None):
        self.author_id = user.id
        self.text = text
        db.session.add(self)
        db.session.commit()
        for image_path in image_paths:
            Image(image_path, self)
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get(id=None):
        if id:
            return Publication.query.get(id)
        return Publication.query.all()

class Image(db.Model):
    __tablename__ = 'Image'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    path = db.Column(db.String(256), unique=True, nullable=False)
    text = db.Column(db.String(), unique=False, nullable=True)
    publication_id = db.Column(db.Integer, db.ForeignKey('Publication.id'), nullable=False)
    objects = db.relationship('Object', secondary=ImageObjects, backref='images', lazy='joined')

    def __init__(self, path, publication):
        self.path = path
        self.publication_id = publication.id
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get(id=None, path=None):
        if id:
            return Image.query.get(id)
        if path:
            return Image.query.filter_by(path=path).first()
        return Image.query.all()


class Object(db.Model):
    __tablename__ = 'Object'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get(id=None, name=None):
        if id:
            return Object.query.get(id)
        if name:
            return Object.query.filter_by(name=name).first()
        return Object.query.all()


class Comment(db.Model):
    __tablename__ = 'Comment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text())
    publication_id = db.Column(db.Integer, db.ForeignKey('Publication.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)

    def __init__(self, text, image_id, user_id):
        self.text = text
        self.user_id = user_id
        self.video_id = image_id
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get(id=None):
        if id:
            return Object.query.get(id)
        return Object.query.all()