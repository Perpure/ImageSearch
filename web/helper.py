from functools import wraps

from flask import session, redirect, url_for

from web.forms import CommentForm
from web.models import User, Comment


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


def extract_pub_id(request):
    dict = request.values
    if dict:
        pub_id = next(iter(dict)).split('-')[0]
        if pub_id.isdigit():
            return int(pub_id)
    return None


def gather_comments_and_forms(publications):
    comments = []
    comment_forms = []
    for publication in publications:
        comments.append(Comment.get(publication_id=publication.id))
        comment_forms.append(CommentForm(prefix=str(publication.id)))
    return comments, comment_forms

def get_str_date(date):
    return date.strftime('%d/%m/%Y %H:%M:%S')