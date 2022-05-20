import os

from flask import redirect, render_template, session, url_for, request
from web import app, images, imgs_path
from web.forms import RegForm, LogForm, PublicationForm, CommentForm, SearchForm
from web.models import User, Publication, Comment
from web.helper import cur_user, extract_pub_id, gather_comments_and_forms, get_str_date

PUBS_NUM_ON_PAGE = 30

@app.route('/', methods=['GET', 'POST'])
def main():
    user = cur_user()
    search_form = SearchForm()

    if search_form.validate_on_submit():
        query = search_form.text.data
        publications = Publication.full_text_search(query)
        comments, comment_forms = gather_comments_and_forms(publications)
        return render_template('main.html', user=user, pubs_coms_forms=zip(publications, comments, comment_forms),
                               search_form=search_form, get_str_date=get_str_date)

    if request.method == 'POST':
        pub_id = extract_pub_id(request)
        if not pub_id is None:
            comment_form = CommentForm(request.form, prefix=str(pub_id))
            if comment_form.validate():
                Comment(comment_form.text.data, publication_id=pub_id, user_id=user.id)
        redirect(url_for('main'))

    page = request.args.get('p', default=0, type=int)

    publications = Publication.get_all_publications(offset=page * PUBS_NUM_ON_PAGE,
                                                    limit=PUBS_NUM_ON_PAGE)

    comments, comment_forms = gather_comments_and_forms(publications)
    return render_template('main.html', user=user, pubs_coms_forms=zip(publications, comments, comment_forms),
                           search_form=search_form, get_str_date=get_str_date)

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
                if file.filename:
                    images_url.append(os.path.join(imgs_path, images.save(file)))
            Publication(page_owner.id, publication_form.text.data, images_url)

    owner_publications = page_owner.publications

    return render_template('user.html', user=user, form=publication_form, publications=owner_publications)