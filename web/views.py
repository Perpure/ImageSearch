import os

from flask import redirect, render_template, session, url_for
from werkzeug.utils import secure_filename

from web import app, db, images, imgs_path
from web.forms import RegForm, LogForm, PublicationForm
from web.models import User, Publication
from web.helper import cur_user, requiresauth


@app.route('/', methods=['GET', 'POST'])
def main():
    user = cur_user()
    publications = Publication.get_all_publications()
    return render_template('main.html', user=user, publications=publications)

@app.route('/reg', methods=['GET', 'POST'])
def reg():
    reg_form = RegForm()

    if reg_form.validate_on_submit():
        user = User(reg_form.login_reg.data, reg_form.password_reg.data)
        session['Login'] = user.login
        return redirect(url_for('main'))

    return render_template('registration.html', reg_form=reg_form, user=cur_user())

@app.route('/login', methods=['GET', 'POST'])
def login():

    log_form = LogForm()
    if log_form.validate_on_submit():
        session['Login'] = log_form.login_log.data
        return redirect(url_for('main'))

    return render_template('login.html', log_form=log_form, user=cur_user())

@app.route('/user/<string:usr>', methods=['GET', 'POST'])
def upload(usr):
    user = cur_user()
    page_owner = User.get(login=usr)
    if page_owner is None:
        return redirect(url_for('main'))

    publication_form = None
    if user == page_owner:
        publication_form = PublicationForm()
        if publication_form.validate_on_submit():
            images_url = []
            for file in publication_form.files.data:
                images_url.append(os.path.join(imgs_path, images.save(file)))
            Publication(page_owner, publication_form.text.data, images_url)

    owner_publications = page_owner.gather_publications()

    return render_template('user.html', user=user, form=publication_form, publications=owner_publications)