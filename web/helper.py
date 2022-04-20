from functools import wraps

from flask import session, redirect, url_for
from web.models import User


def cur_user():
    if 'Login' in session:
        return User.get(login=session['Login'])
    return None

def requiresauth(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if cur_user() is None:
            return redirect(url_for('log'))
        return f(*args, **kwargs)

    return wrapped