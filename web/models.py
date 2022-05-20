import hashlib
from sqlalchemy import desc
from web import db, app
from datetime import datetime
import requests
from sqlalchemy import text

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(32), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(32), nullable=False)
    info = db.Column(db.String())
    publications = db.relationship('Publication', backref='author', lazy='select')

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
    __tablename__ = 'publication'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String(), unique=False, nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    images = db.relationship('Image', backref='publication', lazy='select')

    def __init__(self, user_id, text='', image_paths=None, image_texts=None):
        self.date = datetime.now(tz=None)
        self.author_id = user_id
        self.text = text

        db.session.add(self)
        db.session.commit()

        if image_texts:
            for image_path, image_text in zip(image_paths, image_texts):
                Image(image_path, self, image_text)
        else:
            for image_path in image_paths:
                Image(image_path, self)
        db.session.add(self)
        db.session.commit()

    def get_str_date(self):
        return self.date.strftime('%d/%m/%Y %H:%M:%S')

    @staticmethod
    def full_text_search(query):
        with db.engine.connect() as connection:
            result = connection.execute(text(('SET pg_trgm.word_similarity_threshold = 0.4;'
                                              f'SELECT * FROM full_text_search(\'{query}\');'))).all()
            return result


    @staticmethod
    def get_all_publications(limit=None, offset=None):
        query = Publication.query.order_by(desc(Publication.date))
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query

    @staticmethod
    def get(id=None):
        if id:
            return Publication.query.get(id)
        return Publication.query.all()


class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    path = db.Column(db.String(256), unique=True, nullable=False)
    text = db.Column(db.String(), unique=False, nullable=True)
    publication_id = db.Column(db.Integer, db.ForeignKey('publication.id'), nullable=False)

    def __init__(self, path, publication, text=None):
        self.path = path
        self.publication_id = publication.id
        self.text = text

        if not text and app.config['TEXT_RECOGNITION_URL']:
            file = {'file': ('image.jpg', open(path, 'rb'), 'image/jpeg')}
            res = requests.post(url=app.config['TEXT_RECOGNITION_URL'] + '/predictions/TextDetection', files=file)
            if res.ok:
                self.text = res.text

        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get(id=None, path=None):
        if id:
            return Image.query.get(id)
        if path:
            return Image.query.filter_by(path=path).first()
        return Image.query.all()


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.Text())
    publication_id = db.Column(db.Integer, db.ForeignKey('publication.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)

    def __init__(self, text, publication_id, user_id):
        self.date = datetime.now(tz=None)
        self.text = text
        self.user_id = user_id
        self.publication_id = publication_id
        db.session.add(self)
        db.session.commit()

    def get_str_date(self):
        return self.date.strftime('%d/%m/%Y %H:%M:%S')

    @staticmethod
    def get(id=None, publication_id=None):
        if id:
            return Comment.query.get(id)
        if publication_id:
            return Comment.query.filter_by(publication_id=publication_id) \
                .join(User)
        return Comment.query.all()