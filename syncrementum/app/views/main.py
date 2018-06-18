from flask import render_template, redirect, url_for
from flask_login import current_user

from app import app
from app.forms import user as user_forms


@app.route('/index')
@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.access_token:
            return redirect(url_for('userbp.dashboard'))
        else:
            return redirect(url_for('userbp.insta_signin'))
    form = user_forms.Login()

    return render_template('index.html', form=form, title='Home',
                           action_url='/user/signin')


@app.route('/favicon.ico')
def favicon():
    return redirect('/static/img/favicon.ico')


@app.route('/main/download/index/<inv>/<index>')
@app.route('/main/download/index/<inv>')
def redirect_dl_email(inv, index=None):
    return redirect('/user/user_login/login_by_email/%s' % inv)


@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')


@app.route('/robots.txt')
@app.route('/sitemap.xml')
def no_robots():
    msg = "User-agent: * \nDisallow: /"
    return msg
