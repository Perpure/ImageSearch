from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, MultipleFileField
from wtforms.validators import Length, EqualTo, ValidationError, Optional

from web import images
from web.models import User
import re


def not_exist(form, field):
    if not field.data and User.get(login=field.data) is None:
        raise ValidationError("Такого пользователя не существует")


def match(form, field):
    if not form.login_log.data:
        user = None
    else:
        user = User.get(login=form.login_log.data)
    if user and not user.check_pass(field.data):
        raise ValidationError("Неправильный пароль")
        

def exist(form, field):
    if field.data and User.get(login=field.data):
        raise ValidationError("Такой пользователь уже существует")


def check_correct_name(form, field):
    if not field.data or not re.fullmatch(r'[a-zA-Z0-9_]+', field.data):
        raise ValidationError("В имени пользователя могут быть только цифры, латинские буквы и нижние подчёркивания")


class RegForm(FlaskForm):
    login_reg = StringField("Имя пользователя", validators=[Length(3, message='Логин слишком короткий'),
                                                            exist, check_correct_name])
    password_reg = PasswordField("Пароль", validators=[Length(8, message='Пароль слишком короткий')])
    confirm_reg = PasswordField("Повторите пароль",
                                validators=[Length(8, message='Пароль слишком короткий'),
                                            EqualTo("password_reg", message="Пароли должны совпадать")])
    submit_reg = SubmitField("Зарегистрироваться")
    submit_main = SubmitField("На главную")


class LogForm(FlaskForm):
    login_log = StringField("Имя пользователя", validators=[Length(3, message='Логин слишком короткий'),
                                                            check_correct_name, not_exist])
    password_log = PasswordField("Пароль", validators=[Length(8, message='Пароль слишком короткий'),
                                                       match])
    submit_log = SubmitField("Войти")
    submit_main = SubmitField("На главную")


class PublicationForm(FlaskForm):
    text = TextAreaField("Текст публикации", validators=[Optional()])
    files = MultipleFileField('Прикрепить изображения', validators=[FileAllowed(images,
                                                                                message="Некорректное расширение")])
    submit = SubmitField("Опубликовать")

class CommentForm(FlaskForm):
    text = TextAreaField("", validators=[])
    submit = SubmitField("Комментировать")

class SearchForm(FlaskForm):
    text = StringField("", validators=[])
    submit = SubmitField("Поиск")