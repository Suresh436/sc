import base64
import pickle
import urllib2
from collections import OrderedDict
from datetime import datetime

from flask import (Blueprint, render_template, redirect, url_for,
                   abort, flash, request, current_app, session, g, Response)
from flask_login import (login_user, logout_user, login_required,
                            current_user)
import json

from os import urandom
from sqlalchemy import func
from werkzeug.utils import redirect, escape
from app.tools.InstagramAPI import InstagramAPI
from app import db
from app.forms import user as user_forms
from app.logger_setup import errorlog
from app.tools import misc
from app.models import User, UserDetails, InstaUsers, TargetAccount, TargetAccountFollower, ProxyIp
from app.tools.email import send_email
from app.tools.messages import *
from app.tools.misc import get_insta_object, insta_logout, insta_login, two_factor_login, challenge_req, \
    challenge_security_code, get_states

userbp = Blueprint('userbp', __name__, url_prefix='/user')


@userbp.route('/signup', methods=['GET', 'POST'])
def user_signup():
    """ Function to signup in the application """
    try:
        if current_user.is_authenticated and current_user.user_type == 'user':
            return redirect(url_for('userbp.dashboard'))
        form = user_forms.SignUp()
        if form.validate_on_submit():
            v_email = json.loads(validate_email(form.email.data))
            if v_email['status']:
                flash(v_email['message'], 'danger')

            else:
                res = add_new_user(form)
                if res:
                    if current_user.is_authenticated and current_user.user_type == 'admin':
                        flash('User Added Successfully  ', 'success')
                        return redirect(url_for('userbp.insta_signin', userid=res.id))

                    else:
                        login_user(res)
                    flash(REGISTER_SUCCESS, 'success')
                    return redirect(url_for('userbp.insta_signin'))
                else:
                    flash(REGISTER_ERROR, 'danger')
        return render_template('user/signup.html', form=form)
    except Exception as err:
        errorlog.error('User Signup Error', details=str(err))
        return render_template('error.html', message="Error!")


@userbp.route('/signin', methods=['GET', 'POST'])
def user_signin():
    """ Function to signin in the application """
    try:
        if current_user.is_authenticated:
            if current_user.access_token:
                return redirect(url_for('userbp.dashboard'))
            else:
                return redirect(url_for('userbp.insta_signin'))
        form = user_forms.Login()

        if form.validate_on_submit():
            user = User.load_user(form.username.data)
            if user:
                if user.verify_password(form.password.data):
                    if not user.is_active:
                        flash(ACTIVE_ACCOUNT_ERROR, 'danger')
                        return redirect(url_for('userbp.user_signin'))
                    login_user(user)
                    if current_user.access_token:
                        flash(SIGNIN_SUCCESS, 'success')
                        return redirect(url_for('userbp.dashboard'))
                    else:
                        return redirect(url_for('userbp.insta_signin'))

                else:
                    flash(SIGNIN_ERROR, 'danger')
                    return redirect(url_for('userbp.user_signin'))
            else:
                flash(SIGNIN_ERROR, 'danger')
                return redirect(url_for('userbp.user_signin'))

        return render_template('user/signin.html', form=form, title='Sign in',
                               action_url='/user/signin')
    except Exception as err:
        errorlog.error('Sign in Error', details=str(err))
        return render_template('error.html', message="Error!")


@userbp.route('/sign-out', methods=['GET', 'POST'])
def sign_out():
    """ Function to signout user from the application  """
    try:
        logout_user()
        flash(SIGNOUT_SUCCESS, 'success')
        return redirect(url_for('userbp.user_signin'))
    except Exception as err:
        errorlog.error('Signout Error', details=str(err))
        return render_template('error.html', message="Error!")


@userbp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    """ Function to integrate dashboard in the application """
    try:
        get_uid = request.args.get('userid', default=None, type=int)

        if get_uid is not None and current_user.user_type == 'admin':
            uid = get_uid
            usr_detail = User.by_id(uid)
            get_date = datetime.strptime(
                str(usr_detail.created_at), '%Y-%m-%d %H:%M:%S'
            ).strftime('%Y-%m-%d')

            if not usr_detail.payment_status:
                return redirect(url_for('paymentbp.billing', userid=uid))
            if not usr_detail.access_token:
                return redirect(url_for('userbp.insta_signin', userid=uid))


        else:
            uid = current_user.id
            get_date = datetime.strptime(
                str(current_user.created_at), '%Y-%m-%d %H:%M:%S'
            ).strftime('%Y-%m-%d')
            if not current_user.payment_status:
                return redirect(url_for('paymentbp.billing'))
            if not current_user.access_token:
                return redirect(url_for('userbp.insta_signin'))
        getuserdetails = UserDetails.by_userid(uid)
        initial_count = getuserdetails.user_followed_by
        current_count = InstaUsers.count_current(uid)
        diff = int(current_count.total_followers) - int(initial_count)
        current_following = current_count.total_followings
        post = current_count.total_likes
        best_accounts = TargetAccount.best_account(uid)
        location_accounts = TargetAccount.best_locations(uid)
        hash_accounts = TargetAccount.best_hashtag(uid)

        return render_template('user/dashboard.html',
                               initf=int(initial_count), crdate=get_date,
                               currf=int(current_count.total_followers),
                               curfoll=int(current_following),
                               diff=diff, post=post,
                               best_accounts=best_accounts,
                               location_accounts=location_accounts,
                               hash_accounts=hash_accounts,
                               action="dashboard"
                               )
    except Exception as err:
        errorlog.error('Dashboard Error', details=str(err))
        return render_template('error.html', message="Error!")


@userbp.route('/lets-insta/', methods=['GET', 'POST'])
@userbp.route('/lets-insta/<code_required>', methods=['GET', 'POST'])
@login_required
def insta_signin(code_required=''):
    """ Function to integrate template for instagram configuration """
    try:
        form = user_forms.InstaLogin()
        username = ''
        get_uid = request.args.get('userid', default=None, type=int)
        user_detail = current_user
        dashboard_redirect = url_for('userbp.dashboard')
        if get_uid is not None and current_user.user_type == 'admin':
            user_detail = User.by_id(get_uid)
            dashboard_redirect = url_for('userbp.dashboard', userid=get_uid)

        if code_required != 'code_required':
            code_required = ''

            if user_detail.access_token:
                get_proxy = ProxyIp.get_proxy(user_detail.proxy_ip_id)
                InstaAPI = get_insta_object(user_detail.access_token, get_proxy)
                insta_usr_detail = user_detail.access_token.split('@')
                username = base64.b64decode(insta_usr_detail[0]) if insta_usr_detail[0] else ''
                if isinstance(InstaAPI, InstagramAPI):
                    flash(INSTAGRAM_EXISTS, 'success')
                    return redirect(dashboard_redirect)
        return render_template('user/kickoff.html',
                               form=form, username=username,
                               code_required=code_required, get_uid=get_uid
                               )
    except Exception as err:
        errorlog.error('Isnta signin page Error', details=str(err))
        return render_template('error.html', message="Error!")


@userbp.route('/twofactorwarning')
@login_required
def twofactorwarning():
    """ Function to warn user to disable two factor authentication"""
    try:
        return render_template('user/twofactor.html')
    except Exception as err:
        errorlog.error('Isnta signin page Error', details=str(err))
        return render_template('error.html', message="Error!")


def save_insta_response(data):
    """ Function to save instagram response in the database """

    get_user = User.by_id(data['user_id'])
    get_user.access_token = data['rank_token']

    user_detail = UserDetails.by_userid(data['user_id'])
    if user_detail:
        user_detail.user_follows = data['following_count']
        user_detail.user_followed_by = data['followers_count']
        user_detail.total_media = data['post']
    else:
        user_detail = UserDetails(
            user_id=data['user_id'],
            user_insta_id=data['user_detail']['pk'],
            full_name= data['user_detail']['full_name'],
            username=data['user_detail']['username'],
            profile_picture=data['user_detail']['profile_pic_url'],
            user_follows=data['following_count'],
            user_followed_by=data['followers_count'],
            total_media=data['post'],
            created_at=func.now(),
            updated_at=func.now()
        )
        db.session.add(user_detail)

    instaDetails = InstaUsers(
        total_followers=data['followers_count'],
        total_followings=data['following_count'],
        user_id=data['user_id'],
        total_likes=data['post'],
        created_at=func.now()
    )
    db.session.add(instaDetails)

    db.session.commit()
    return True


@userbp.route('/instalogin', methods=['GET', 'POST'])
def instalogin():
    """ Function to call api to instagram login and check response"""
    try:
        request_param = json.loads(request.data)

        new_token = ''
        get_uid = request.args.get('userid', default=None, type=int)

        if get_uid is not None and current_user.user_type == 'admin':
            user_detail = User.by_id(get_uid)
        else:
            get_uid = current_user.id
            user_detail = current_user
        get_proxy = ProxyIp.get_proxy(user_detail.proxy_ip_id)
        if 'verification_code' in request_param and request_param['verification_code'] != '':
            if 'username' in request_param and request_param['username'] != '':
                new_token = base64.b64encode(request_param['username']) + '@' + \
                            base64.b64encode(request_param['password'])
            InstaApi = two_factor_login(new_token, get_proxy, request_param['verification_code'], user_detail)
            if isinstance(InstaApi, InstagramAPI):
                new_token = base64.b64encode(InstaApi.username) + '@' + \
                            base64.b64encode(InstaApi.password)
        elif 'security_code' in request_param and request_param['security_code'] != '':
            InstaApi = challenge_security_code(request_param['security_code'], user_detail)
            if isinstance(InstaApi, InstagramAPI):
                new_token = base64.b64encode(InstaApi.username) + '@' + \
                            base64.b64encode(InstaApi.password)
        else:
            if user_detail.access_token:
                insta_usr_detail = user_detail.access_token.split('@')
                request_param['username'] = base64.b64decode(insta_usr_detail[0]) if insta_usr_detail[0] else ''
            new_token = base64.b64encode(request_param['username']) + '@' + \
                        base64.b64encode(request_param['password'])
            InstaApi = insta_login(new_token, get_proxy, user_detail)
        if InstaApi == 'error':
            login_resp = dict(msg=INSTAGRAM_SIGNIN_ERROR,
                              status='error', data='')
            return json.dumps(login_resp)
        elif InstaApi == 'code_required':
            login_resp = dict(msg=TWO_STEP_AUTHENTICATION,
                              status='code_required', data='')
            return json.dumps(login_resp)
        elif InstaApi == 'invalid_code':
            login_resp = dict(msg='Invalid code!',
                              status='error', data='')
            return json.dumps(login_resp)
        elif InstaApi == 'invalid_security_code':
            login_resp = dict(msg='Security Code is Invalid!',
                              status='error', data='')
            return json.dumps(login_resp)
        elif not isinstance(InstaApi, InstagramAPI) \
                and ('error_type' in InstaApi
                     and InstaApi['error_type'] == 'checkpoint_challenge_required'):
            login_resp = dict(msg='',
                              status='checkpoint_challenge_required', data='')
            login_resp['msg'] = SUSPICIOUS_LOGIN_ATTEMPT
            login_resp['status'] = 'checkpoint_challenge_required'
            login_resp['data'] = ''
            login_resp['fields'] = get_fields(InstaApi['challenge']['url'])
            return json.dumps(login_resp)

            # db.session.commit()
        InstaApi.getProfileData()
        result = InstaApi.LastJson
        if result['status'] != 'ok':
            login_resp = dict(msg=INSTAGRAM_SIGNIN_ERROR,
                              status='error', data='')
            return json.dumps(login_resp)
        user_id = result['user']['pk']
        get_exist_user = UserDetails.by_instaid(user_id)
        if get_exist_user and get_exist_user.user_id != get_uid:
            flash(INSTAGRAM_USED_BY_OTHER_USER, 'danger')
            login_resp = dict(msg=INSTAGRAM_USED_BY_OTHER_USER,
                              status='exists')
        else:
            followers_list = InstaApi.getTotalFollowers(user_id)
            followers_count = len(followers_list)

            following_list = InstaApi.getTotalFollowings(user_id)
            following_count = len(following_list)

            userpost = InstaApi .getTotalUserFeed(user_id)

            data = dict(
                        rank_token=new_token,
                        user_detail=result['user'],
                        followers_count=followers_count,
                        followers_list=followers_list,
                        following_count=following_count,
                        following_list=following_list,
                        post=len(userpost),
                        user_id=get_uid
                    )
            save_response = save_insta_response(data)
            if save_response:
                login_resp = dict(msg=INSTAGRAM_LOGIN_SUCCESS,
                                  status='success')
            else:
                login_resp = dict(msg=INSTAGRAM_LOGIN_FAILED,
                                status='error')

    except Exception as err:
        login_resp = dict(status='error', msg=INSTAGRAM_SIGNIN_ERROR, data='')
        errorlog.error('Failed to login with Instagram.', details=str(err))

    resp = Response(json.dumps(login_resp), status=200,
                    mimetype='application/json')
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


def get_fields(link):
    """ Function to get fields email and phone no from Instagram site for suspicious login attempt """
    try:
        from bs4 import BeautifulSoup as BS
        request = urllib2.Request(link, headers={"Accept": "text/html"})
        usock = urllib2.urlopen(request)
        data = usock.read()
        usock.close()
        soup = BS(data)
        get_script_data = soup.findAll('script')[3].text
        get_value = get_script_data.split('window._sharedData =')[1][:-1]
        detailed_val = json.loads(get_value)
        data_fields = detailed_val['entry_data']['Challenge'][0]['fields']
        return data_fields
    except Exception as err:
        errorlog.error('Failed to send message.', details=str(err))
        return "error"


@userbp.route('/send_verification', methods=['POST'])
def send_verification():
    """ Function to send verification to email or phone """

    login_resp = dict()
    try:
        get_uid = request.args.get('userid', default=None, type=int)
        user_detail = current_user
        if get_uid is not None and current_user.user_type == 'admin':
            user_detail = User.by_id(get_uid)
        request_param = json.loads(request.data)
        InstaApi = challenge_req(request_param['choice'], user_detail)
        if isinstance(InstaApi, InstagramAPI):
            login_resp['status'] = 'success'
        else:
            login_resp['status'] = 'error'
            login_resp['msg'] = CODE_SEND_ERROR

    except Exception as err:
        errorlog.error('Failed to send message.', details=str(err))
        login_resp['status'] = 'error'
        login_resp['msg'] = CODE_SEND_ERROR
    return json.dumps(login_resp)


def add_new_user(form):
    """ Function to save new user in database """
    import socket
    get_ip = socket.gethostbyname(socket.gethostname())
    get_proxies = ProxyIp.count_proxies()
    count_proxies = int(get_proxies[0][0]) if get_proxies[0][0] else 1
    user = User(
        first_name=form.first_name.data,
        last_name=form.last_name.data,
        email=form.email.data,
        password=misc.create_ra_hash(form.password.data),
        phone=form.phone.data,
        saved_target_accounts=0,
        created_at=func.now(),
        updated_at=func.now(),
        user_ip=get_ip,
        proxy_ip_id=0,
        user_type='user',
        cron_status=True,
        is_active=True
    )
    db.session.add(user)

    db.session.commit()
    proxy_ip_id = int(user.id) % count_proxies if int(user.id) % \
                                                  count_proxies != 0 else 1
    user.proxy_ip_id = int(proxy_ip_id)
    db.session.commit()

    return user


@userbp.route('/validate_email/<email>')
def validate_email(email, uid=None):
    """ Function to validate email if exist in database or not """
    user_detail = User.load_user(email)
    msg = {}
    if user_detail and uid is None:
        msg['status'] = 'True'
        msg['message'] = EMAIL_EXISTS
    elif user_detail and str(uid) != str(user_detail.id):
        msg['status'] = 'True'
        msg['message'] = EMAIL_EXISTS
    else:
        msg['status'] = False
    return json.dumps(msg)


@userbp.route('/search_users', methods=['GET', 'POST'])
def search_users():
    """API to autocomplete search_users info"""
    res = dict()
    try:
        qry = request.args.get('q', default=None, type=str)
        get_uid = request.args.get('userid', default=None, type=int)
        user_detail = current_user
        if get_uid is not None and current_user.user_type == 'admin':
            user_detail = User.by_id(get_uid)
        user_result = []
        if user_detail.access_token:
            get_proxy = ProxyIp.get_proxy(user_detail.proxy_ip_id)
            InstaAPI = get_insta_object(user_detail.access_token, get_proxy)
            if not isinstance(InstaAPI, InstagramAPI):
                res['status'] = 'error',
                res['data'] = []
                return json.dumps(res)
        else:
            res['status'] = 'error',
            res['data'] = []
            return json.dumps(res)
        InstaAPI.searchUsers(qry)
        userlist = InstaAPI.LastJson.get('users')
        for row in userlist:
            if qry.upper() in row['username'].upper():
                newdata = {}
                newdata['username'] = row['username']
                newdata['profile_pic'] = row['profile_pic_url']
                newdata['pk'] = row['pk']

                user_result.append(newdata)

        res['status'] = 'success',
        res['list'] = user_result
        return json.dumps(res)

    except Exception as err:
        errorlog.error('Failed to search user request.', details=str(err))
        res['status'] = 'error',
        res['list'] = []
        return json.dumps(res)


@userbp.route('/launch_target', methods=['GET', 'POST'])
def launch_target():
    """save target accounts in db"""
    try:
        request_param = json.loads(request.data)
        get_uid = request.args.get('userid', default=None, type=int)
        user_detail = current_user
        if get_uid is not None and current_user.user_type == 'admin':
            user_detail = User.by_id(get_uid)
        for acc in request_param['target_user']:
            get_exist = TargetAccount.by_username(acc['username'], 0, user_detail.id)
            if get_exist:
                continue
            tgt_account = TargetAccount(
                user_id=user_detail.id,
                insta_id=acc['insta_id'],
                user_name=acc['username'],
                created_at=func.now(),
                updated_at=func.now(),
                actions=0,
                followbacks=0,
                next_max_id=None,
                type=0,
                is_added=0,
                profile_image=acc['profile_image'],
            )
            db.session.add(tgt_account)
            db.session.flush()

        for acc in request_param['target_hash']:
            get_exist = TargetAccount.by_username(acc['username'], 2, user_detail.id)
            if get_exist:
                continue
            tgt_account = TargetAccount(
                user_id=user_detail.id,
                insta_id=acc['insta_id'],
                user_name=acc['username'],
                created_at=func.now(),
                updated_at=func.now(),
                actions=0,
                followbacks=0,
                next_max_id=None,
                type=2,
                is_added=0,
                profile_image=''
            )
            db.session.add(tgt_account)
            db.session.flush()

        for acc in request_param['target_loc']:
            get_exist = TargetAccount.by_username(acc['username'], 1, user_detail.id)
            if get_exist:
                continue
            tgt_account = TargetAccount(
                user_id=user_detail.id,
                insta_id=acc['insta_id'],
                user_name=acc['username'],
                created_at=func.now(),
                updated_at=func.now(),
                actions=0,
                followbacks=0,
                next_max_id=None,
                type=1,
                is_added=0,
                profile_image=''
            )
            db.session.add(tgt_account)
            db.session.flush()

        curr = User.load_user(user_detail.email)
        curr.saved_target_accounts = 1
        db.session.commit()

        return json.dumps({'status':'success'})

    except Exception as err:
        errorlog.error('Failed to lauch target.', details=str(err))
        user_result = [{'status': 'error'}]
        return json.dumps(user_result)


@userbp.route('/search_location', methods=['GET', 'POST'])
def search_location():
    """API to autocomplete sear_users info"""
    res = dict()
    try:
        qry = request.args.get('q', default=None, type=str)
        get_uid = request.args.get('userid', default=None, type=int)
        user_detail = current_user
        if get_uid is not None and current_user.user_type == 'admin':
            user_detail = User.by_id(get_uid)

        if user_detail.access_token:
            get_proxy = ProxyIp.get_proxy(user_detail.proxy_ip_id)
            InstaAPI = get_insta_object(user_detail.access_token, get_proxy)
            if not isinstance(InstaAPI, InstagramAPI):
                res['status'] = 'error',
                res['data'] = []
                return json.dumps(res)
        else:
            res['status'] = 'error',
            res['data'] = []
            return json.dumps(res)
        InstaAPI.searchLocation(qry)
        userlist = InstaAPI.LastJson.get('items')
        user_result = []

        if userlist:
            for row in userlist:
                if qry.upper() in row['title'].upper():
                    newdata = dict()
                    newdata['location_name'] = row['location']['name']
                    newdata['profile_pic'] = None
                    newdata['pk'] = row['location']['pk']

                    user_result.append(newdata)
        res['status'] = 'success',
        res['list'] = user_result
        return json.dumps(res)

    except Exception as err:
        errorlog.error('Failed to search location request.', details=str(err))
        res['status'] = 'error',
        res['list'] = []
        return json.dumps(res)


@userbp.route('/search_hash', methods=['GET', 'POST'])
def search_hash():
    """API to autocomplete sear_users info"""
    res = dict()
    try:
        qry = request.args.get('q', default=None, type=str)
        get_uid = request.args.get('userid', default=None, type=int)
        user_detail = current_user
        if get_uid is not None and current_user.user_type == 'admin':
            user_detail = User.by_id(get_uid)

        if user_detail.access_token:
            get_proxy = ProxyIp.get_proxy(user_detail.proxy_ip_id)
            InstaAPI = get_insta_object(user_detail.access_token, get_proxy)

            if not isinstance(InstaAPI, InstagramAPI):
                res['status'] = 'error',
                res['data'] = []
                return json.dumps(res)
        else:
            res['status'] = 'error',
            res['data'] = []
            return json.dumps(res)
        InstaAPI.searchTags(qry)
        hashlist = InstaAPI.LastJson.get('results')
        user_result = []

        if hashlist:
            for row in hashlist:
                if qry.upper() in row['name'].upper():
                    newdata = {}
                    newdata['hash_name'] = row['name']
                    newdata['hash_profile_pic'] = row['profile_pic_url']
                    newdata['pk'] = row['id']

                    user_result.append(newdata)

        res['status'] = 'success',
        res['list'] = user_result
        return json.dumps(res)

    except Exception as err:
        errorlog.error('Failed to search hashtag request.', details=str(err))
        res['status'] = 'error',
        res['list'] = []
        return json.dumps(res)


@userbp.route('/save_iasdps', methods=['GET', 'POST'])
def save_ips():
    """ Function to save static IPs in db"""
    pids ={"ip":"104.171.146.2","port":"60000","country":"US"},{"ip":"104.171.146.3","port":"60000","country":"US"},{"ip":"104.171.146.4","port":"60000","country":"US"},{"ip":"104.171.146.5","port":"60000","country":"US"},{"ip":"104.171.146.6","port":"60000","country":"US"},{"ip":"104.171.146.7","port":"60000","country":"US"},{"ip":"104.171.146.8","port":"60000","country":"US"},{"ip":"104.171.146.9","port":"60000","country":"US"},{"ip":"104.171.146.10","port":"60000","country":"US"},{"ip":"104.171.146.11","port":"60000","country":"US"},{"ip":"104.171.146.12","port":"60000","country":"US"},{"ip":"104.171.146.13","port":"60000","country":"US"},{"ip":"104.171.146.14","port":"60000","country":"US"},{"ip":"104.171.146.15","port":"60000","country":"US"},{"ip":"104.171.146.16","port":"60000","country":"US"},{"ip":"104.171.146.17","port":"60000","country":"US"},{"ip":"104.171.146.18","port":"60000","country":"US"},{"ip":"104.171.146.19","port":"60000","country":"US"},{"ip":"104.171.146.20","port":"60000","country":"US"},{"ip":"104.171.146.21","port":"60000","country":"US"},{"ip":"104.171.146.22","port":"60000","country":"US"},{"ip":"104.171.146.23","port":"60000","country":"US"},{"ip":"104.171.146.24","port":"60000","country":"US"},{"ip":"104.171.146.25","port":"60000","country":"US"},{"ip":"104.171.146.26","port":"60000","country":"US"},{"ip":"104.171.146.27","port":"60000","country":"US"},{"ip":"104.171.146.28","port":"60000","country":"US"},{"ip":"104.171.146.29","port":"60000","country":"US"},{"ip":"104.171.146.30","port":"60000","country":"US"},{"ip":"104.171.146.31","port":"60000","country":"US"},{"ip":"104.171.146.32","port":"60000","country":"US"},{"ip":"104.171.146.33","port":"60000","country":"US"},{"ip":"104.171.146.34","port":"60000","country":"US"},{"ip":"104.171.146.35","port":"60000","country":"US"},{"ip":"104.171.146.36","port":"60000","country":"US"},{"ip":"104.171.146.37","port":"60000","country":"US"},{"ip":"104.171.146.38","port":"60000","country":"US"},{"ip":"104.171.146.39","port":"60000","country":"US"},{"ip":"104.171.146.40","port":"60000","country":"US"},{"ip":"104.171.146.41","port":"60000","country":"US"},{"ip":"104.171.146.42","port":"60000","country":"US"},{"ip":"104.171.146.43","port":"60000","country":"US"},{"ip":"104.171.146.44","port":"60000","country":"US"},{"ip":"104.171.146.45","port":"60000","country":"US"},{"ip":"104.171.146.46","port":"60000","country":"US"},{"ip":"104.171.146.47","port":"60000","country":"US"},{"ip":"104.171.146.48","port":"60000","country":"US"},{"ip":"104.171.146.49","port":"60000","country":"US"},{"ip":"104.171.146.50","port":"60000","country":"US"},{"ip":"104.171.146.51","port":"60000","country":"US"},{"ip":"104.171.146.52","port":"60000","country":"US"},{"ip":"104.171.146.53","port":"60000","country":"US"},{"ip":"104.171.146.54","port":"60000","country":"US"},{"ip":"104.171.146.55","port":"60000","country":"US"},{"ip":"104.171.146.56","port":"60000","country":"US"},{"ip":"104.171.146.57","port":"60000","country":"US"},{"ip":"104.171.146.58","port":"60000","country":"US"},{"ip":"104.171.146.59","port":"60000","country":"US"},{"ip":"104.171.146.60","port":"60000","country":"US"},{"ip":"104.171.146.61","port":"60000","country":"US"},{"ip":"104.171.146.62","port":"60000","country":"US"},{"ip":"104.171.146.63","port":"60000","country":"US"},{"ip":"104.171.146.64","port":"60000","country":"US"},{"ip":"104.171.146.65","port":"60000","country":"US"},{"ip":"104.171.146.66","port":"60000","country":"US"},{"ip":"104.171.146.67","port":"60000","country":"US"},{"ip":"104.171.146.68","port":"60000","country":"US"},{"ip":"104.171.146.69","port":"60000","country":"US"},{"ip":"104.171.146.70","port":"60000","country":"US"},{"ip":"104.171.146.71","port":"60000","country":"US"},{"ip":"104.171.146.72","port":"60000","country":"US"},{"ip":"104.171.146.73","port":"60000","country":"US"},{"ip":"104.171.146.74","port":"60000","country":"US"},{"ip":"104.171.146.75","port":"60000","country":"US"},{"ip":"104.171.146.76","port":"60000","country":"US"},{"ip":"104.171.146.77","port":"60000","country":"US"},{"ip":"104.171.146.78","port":"60000","country":"US"},{"ip":"104.171.146.79","port":"60000","country":"US"},{"ip":"104.171.146.80","port":"60000","country":"US"},{"ip":"104.171.146.81","port":"60000","country":"US"},{"ip":"104.171.146.82","port":"60000","country":"US"},{"ip":"104.171.146.83","port":"60000","country":"US"},{"ip":"104.171.146.84","port":"60000","country":"US"},{"ip":"104.171.146.85","port":"60000","country":"US"},{"ip":"104.171.146.86","port":"60000","country":"US"},{"ip":"104.171.146.87","port":"60000","country":"US"},{"ip":"104.171.146.88","port":"60000","country":"US"},{"ip":"104.171.146.89","port":"60000","country":"US"},{"ip":"104.171.146.90","port":"60000","country":"US"},{"ip":"104.171.146.91","port":"60000","country":"US"},{"ip":"104.171.146.92","port":"60000","country":"US"},{"ip":"104.171.146.93","port":"60000","country":"US"},{"ip":"104.171.146.94","port":"60000","country":"US"},{"ip":"104.171.146.95","port":"60000","country":"US"},{"ip":"104.171.146.96","port":"60000","country":"US"},{"ip":"104.171.146.97","port":"60000","country":"US"},{"ip":"104.171.146.98","port":"60000","country":"US"},{"ip":"104.171.146.99","port":"60000","country":"US"},{"ip":"104.171.146.100","port":"60000","country":"US"},{"ip":"104.171.146.101","port":"60000","country":"US"},{"ip":"104.171.146.102","port":"60000","country":"US"},{"ip":"104.171.146.103","port":"60000","country":"US"},{"ip":"104.171.146.104","port":"60000","country":"US"},{"ip":"104.171.146.105","port":"60000","country":"US"},{"ip":"104.171.146.106","port":"60000","country":"US"},{"ip":"104.171.146.107","port":"60000","country":"US"},{"ip":"104.171.146.108","port":"60000","country":"US"},{"ip":"104.171.146.109","port":"60000","country":"US"},{"ip":"104.171.146.110","port":"60000","country":"US"},{"ip":"104.171.146.111","port":"60000","country":"US"},{"ip":"104.171.146.112","port":"60000","country":"US"},{"ip":"104.171.146.113","port":"60000","country":"US"},{"ip":"104.171.146.114","port":"60000","country":"US"},{"ip":"104.171.146.115","port":"60000","country":"US"},{"ip":"104.171.146.116","port":"60000","country":"US"},{"ip":"104.171.146.117","port":"60000","country":"US"},{"ip":"104.171.146.118","port":"60000","country":"US"},{"ip":"104.171.146.119","port":"60000","country":"US"},{"ip":"104.171.146.120","port":"60000","country":"US"},{"ip":"104.171.146.121","port":"60000","country":"US"},{"ip":"104.171.146.122","port":"60000","country":"US"},{"ip":"104.171.146.123","port":"60000","country":"US"},{"ip":"104.171.146.124","port":"60000","country":"US"},{"ip":"104.171.146.125","port":"60000","country":"US"},{"ip":"104.171.146.126","port":"60000","country":"US"},{"ip":"104.171.146.127","port":"60000","country":"US"},{"ip":"104.171.146.128","port":"60000","country":"US"},{"ip":"104.171.146.129","port":"60000","country":"US"},{"ip":"104.171.146.130","port":"60000","country":"US"},{"ip":"104.171.146.131","port":"60000","country":"US"},{"ip":"104.171.146.132","port":"60000","country":"US"},{"ip":"104.171.146.133","port":"60000","country":"US"},{"ip":"104.171.146.134","port":"60000","country":"US"},{"ip":"104.171.146.135","port":"60000","country":"US"},{"ip":"104.171.146.136","port":"60000","country":"US"},{"ip":"104.171.146.137","port":"60000","country":"US"},{"ip":"104.171.146.138","port":"60000","country":"US"},{"ip":"104.171.146.139","port":"60000","country":"US"},{"ip":"104.171.146.140","port":"60000","country":"US"},{"ip":"104.171.146.141","port":"60000","country":"US"},{"ip":"104.171.146.142","port":"60000","country":"US"},{"ip":"104.171.146.143","port":"60000","country":"US"},{"ip":"104.171.146.144","port":"60000","country":"US"},{"ip":"104.171.146.145","port":"60000","country":"US"},{"ip":"104.171.146.146","port":"60000","country":"US"},{"ip":"104.171.146.147","port":"60000","country":"US"},{"ip":"104.171.146.148","port":"60000","country":"US"},{"ip":"104.171.146.149","port":"60000","country":"US"},{"ip":"104.171.146.150","port":"60000","country":"US"},{"ip":"104.171.146.151","port":"60000","country":"US"},{"ip":"104.171.146.152","port":"60000","country":"US"},{"ip":"104.171.146.153","port":"60000","country":"US"},{"ip":"104.171.146.154","port":"60000","country":"US"},{"ip":"104.171.146.155","port":"60000","country":"US"},{"ip":"104.171.146.156","port":"60000","country":"US"},{"ip":"104.171.146.157","port":"60000","country":"US"},{"ip":"104.171.146.158","port":"60000","country":"US"},{"ip":"104.171.146.159","port":"60000","country":"US"},{"ip":"104.171.146.160","port":"60000","country":"US"},{"ip":"104.171.146.161","port":"60000","country":"US"},{"ip":"104.171.146.162","port":"60000","country":"US"},{"ip":"104.171.146.163","port":"60000","country":"US"},{"ip":"104.171.146.164","port":"60000","country":"US"},{"ip":"104.171.146.165","port":"60000","country":"US"},{"ip":"104.171.146.166","port":"60000","country":"US"},{"ip":"104.171.146.167","port":"60000","country":"US"},{"ip":"104.171.146.168","port":"60000","country":"US"},{"ip":"104.171.146.170","port":"60000","country":"US"},{"ip":"104.171.146.171","port":"60000","country":"US"},{"ip":"104.171.146.172","port":"60000","country":"US"},{"ip":"104.171.146.173","port":"60000","country":"US"},{"ip":"104.171.146.174","port":"60000","country":"US"},{"ip":"104.171.146.175","port":"60000","country":"US"},{"ip":"104.171.146.176","port":"60000","country":"US"},{"ip":"104.171.146.177","port":"60000","country":"US"},{"ip":"104.171.146.178","port":"60000","country":"US"},{"ip":"104.171.146.179","port":"60000","country":"US"},{"ip":"104.171.146.180","port":"60000","country":"US"},{"ip":"104.171.146.181","port":"60000","country":"US"},{"ip":"104.171.146.182","port":"60000","country":"US"},{"ip":"104.171.146.183","port":"60000","country":"US"},{"ip":"104.171.146.184","port":"60000","country":"US"},{"ip":"104.171.146.185","port":"60000","country":"US"},{"ip":"104.171.146.186","port":"60000","country":"US"},{"ip":"104.171.146.187","port":"60000","country":"US"},{"ip":"104.171.146.188","port":"60000","country":"US"},{"ip":"104.171.146.189","port":"60000","country":"US"},{"ip":"104.171.146.190","port":"60000","country":"US"},{"ip":"104.171.146.191","port":"60000","country":"US"},{"ip":"104.171.146.192","port":"60000","country":"US"},{"ip":"104.171.146.193","port":"60000","country":"US"},{"ip":"104.171.146.194","port":"60000","country":"US"},{"ip":"104.171.146.195","port":"60000","country":"US"},{"ip":"104.171.146.196","port":"60000","country":"US"},{"ip":"104.171.146.197","port":"60000","country":"US"},{"ip":"104.171.146.198","port":"60000","country":"US"},{"ip":"104.171.146.199","port":"60000","country":"US"},{"ip":"104.171.146.200","port":"60000","country":"US"},{"ip":"104.171.146.202","port":"60000","country":"US"},{"ip":"104.171.146.203","port":"60000","country":"US"}
    #pids ={"ip":"104.171.146.204","port":"60000","country":"US"},
    # {"ip":"104.171.146.205","port":"60000","country":"US"},{"ip":"104.171.146.206","port":"60000","country":"US"},{"ip":"104.171.146.207","port":"60000","country":"US"},{"ip":"104.171.146.208","port":"60000","country":"US"},{"ip":"104.171.146.209","port":"60000","country":"US"},{"ip":"104.171.146.210","port":"60000","country":"US"},{"ip":"104.171.146.211","port":"60000","country":"US"},{"ip":"104.171.146.212","port":"60000","country":"US"},{"ip":"104.171.146.213","port":"60000","country":"US"},{"ip":"104.171.146.214","port":"60000","country":"US"},{"ip":"104.171.146.215","port":"60000","country":"US"},{"ip":"104.171.146.216","port":"60000","country":"US"},{"ip":"104.171.146.217","port":"60000","country":"US"},{"ip":"104.171.146.218","port":"60000","country":"US"},{"ip":"104.171.146.219","port":"60000","country":"US"},{"ip":"104.171.146.220","port":"60000","country":"US"},{"ip":"104.171.146.221","port":"60000","country":"US"},{"ip":"104.171.146.222","port":"60000","country":"US"},{"ip":"104.171.146.223","port":"60000","country":"US"},{"ip":"104.171.146.224","port":"60000","country":"US"},{"ip":"104.171.146.225","port":"60000","country":"US"},{"ip":"104.171.146.226","port":"60000","country":"US"},{"ip":"104.171.146.227","port":"60000","country":"US"},{"ip":"104.171.146.228","port":"60000","country":"US"},{"ip":"104.171.146.229","port":"60000","country":"US"},{"ip":"104.171.146.230","port":"60000","country":"US"},{"ip":"104.171.146.231","port":"60000","country":"US"},{"ip":"104.171.146.232","port":"60000","country":"US"},{"ip":"104.171.146.234","port":"60000","country":"US"},{"ip":"104.171.146.235","port":"60000","country":"US"},{"ip":"104.171.146.236","port":"60000","country":"US"},{"ip":"104.171.146.237","port":"60000","country":"US"},{"ip":"104.171.146.238","port":"60000","country":"US"},{"ip":"104.171.146.239","port":"60000","country":"US"},{"ip":"104.171.146.240","port":"60000","country":"US"},{"ip":"104.171.146.241","port":"60000","country":"US"},{"ip":"104.171.146.242","port":"60000","country":"US"},{"ip":"104.171.146.243","port":"60000","country":"US"},{"ip":"104.171.146.244","port":"60000","country":"US"},{"ip":"104.171.146.245","port":"60000","country":"US"},{"ip":"104.171.146.246","port":"60000","country":"US"},{"ip":"104.171.146.247","port":"60000","country":"US"},{"ip":"104.171.146.248","port":"60000","country":"US"},{"ip":"104.171.146.249","port":"60000","country":"US"},{"ip":"104.171.146.250","port":"60000","country":"US"},{"ip":"104.171.146.251","port":"60000","country":"US"},{"ip":"104.171.146.252","port":"60000","country":"US"},{"ip":"104.171.146.253","port":"60000","country":"US"},{"ip":"104.171.146.254","port":"60000","country":"US"},{"ip":"104.171.154.2","port":"60000","country":"US"},{"ip":"104.171.154.3","port":"60000","country":"US"},{"ip":"104.171.154.4","port":"60000","country":"US"},{"ip":"104.171.154.5","port":"60000","country":"US"},{"ip":"104.171.154.6","port":"60000","country":"US"},{"ip":"104.171.154.7","port":"60000","country":"US"},{"ip":"104.171.154.8","port":"60000","country":"US"},{"ip":"104.171.154.9","port":"60000","country":"US"},{"ip":"104.171.154.10","port":"60000","country":"US"},{"ip":"104.171.154.11","port":"60000","country":"US"},{"ip":"104.171.154.12","port":"60000","country":"US"},{"ip":"104.171.154.13","port":"60000","country":"US"},{"ip":"104.171.154.14","port":"60000","country":"US"},{"ip":"104.171.154.15","port":"60000","country":"US"},{"ip":"104.171.154.16","port":"60000","country":"US"},{"ip":"104.171.154.17","port":"60000","country":"US"},{"ip":"104.171.154.18","port":"60000","country":"US"},{"ip":"104.171.154.19","port":"60000","country":"US"},{"ip":"104.171.154.20","port":"60000","country":"US"},{"ip":"104.171.154.21","port":"60000","country":"US"},{"ip":"104.171.154.22","port":"60000","country":"US"},{"ip":"104.171.154.23","port":"60000","country":"US"},{"ip":"104.171.154.24","port":"60000","country":"US"},{"ip":"104.171.154.25","port":"60000","country":"US"},{"ip":"104.171.154.26","port":"60000","country":"US"},{"ip":"104.171.154.27","port":"60000","country":"US"},{"ip":"104.171.154.28","port":"60000","country":"US"},{"ip":"104.171.154.29","port":"60000","country":"US"},{"ip":"104.171.154.30","port":"60000","country":"US"},{"ip":"104.171.154.31","port":"60000","country":"US"},{"ip":"104.171.154.32","port":"60000","country":"US"},{"ip":"104.171.154.33","port":"60000","country":"US"},{"ip":"104.171.154.34","port":"60000","country":"US"},{"ip":"104.171.154.35","port":"60000","country":"US"},{"ip":"104.171.154.36","port":"60000","country":"US"},{"ip":"104.171.154.37","port":"60000","country":"US"},{"ip":"104.171.154.38","port":"60000","country":"US"},{"ip":"104.171.154.39","port":"60000","country":"US"},{"ip":"104.171.154.40","port":"60000","country":"US"},{"ip":"104.171.154.41","port":"60000","country":"US"},{"ip":"104.171.154.42","port":"60000","country":"US"},{"ip":"104.171.154.43","port":"60000","country":"US"},{"ip":"104.171.154.44","port":"60000","country":"US"},{"ip":"104.171.154.45","port":"60000","country":"US"},{"ip":"104.171.154.46","port":"60000","country":"US"},{"ip":"104.171.154.47","port":"60000","country":"US"},{"ip":"104.171.154.48","port":"60000","country":"US"},{"ip":"104.171.154.49","port":"60000","country":"US"},{"ip":"104.171.154.50","port":"60000","country":"US"},{"ip":"104.171.154.51","port":"60000","country":"US"},{"ip":"104.171.154.52","port":"60000","country":"US"},{"ip":"104.171.154.53","port":"60000","country":"US"},{"ip":"104.171.154.54","port":"60000","country":"US"},{"ip":"104.171.154.55","port":"60000","country":"US"},{"ip":"104.171.154.56","port":"60000","country":"US"},{"ip":"104.171.154.57","port":"60000","country":"US"},{"ip":"104.171.154.58","port":"60000","country":"US"},{"ip":"104.171.154.59","port":"60000","country":"US"},{"ip":"104.171.154.60","port":"60000","country":"US"},{"ip":"104.171.154.61","port":"60000","country":"US"},{"ip":"104.171.154.62","port":"60000","country":"US"},{"ip":"104.171.154.63","port":"60000","country":"US"},{"ip":"104.171.154.64","port":"60000","country":"US"},{"ip":"104.171.154.65","port":"60000","country":"US"},{"ip":"104.171.154.66","port":"60000","country":"US"},{"ip":"104.171.154.67","port":"60000","country":"US"},{"ip":"104.171.154.68","port":"60000","country":"US"},{"ip":"104.171.154.69","port":"60000","country":"US"},{"ip":"104.171.154.70","port":"60000","country":"US"},{"ip":"104.171.154.71","port":"60000","country":"US"},{"ip":"104.171.154.72","port":"60000","country":"US"},{"ip":"104.171.154.73","port":"60000","country":"US"},{"ip":"104.171.154.74","port":"60000","country":"US"},{"ip":"104.171.154.75","port":"60000","country":"US"},{"ip":"104.171.154.76","port":"60000","country":"US"},{"ip":"104.171.154.77","port":"60000","country":"US"},{"ip":"104.171.154.78","port":"60000","country":"US"},{"ip":"104.171.154.79","port":"60000","country":"US"},{"ip":"104.171.154.80","port":"60000","country":"US"},{"ip":"104.171.154.81","port":"60000","country":"US"},{"ip":"104.171.154.82","port":"60000","country":"US"},{"ip":"104.171.154.83","port":"60000","country":"US"},{"ip":"104.171.154.84","port":"60000","country":"US"},{"ip":"104.171.154.85","port":"60000","country":"US"},{"ip":"104.171.154.86","port":"60000","country":"US"},{"ip":"104.171.154.87","port":"60000","country":"US"},{"ip":"104.171.154.88","port":"60000","country":"US"},{"ip":"104.171.154.89","port":"60000","country":"US"},{"ip":"104.171.154.90","port":"60000","country":"US"},{"ip":"104.171.154.91","port":"60000","country":"US"},{"ip":"104.171.154.92","port":"60000","country":"US"},{"ip":"104.171.154.93","port":"60000","country":"US"},{"ip":"104.171.154.94","port":"60000","country":"US"},{"ip":"104.171.154.95","port":"60000","country":"US"},{"ip":"104.171.154.96","port":"60000","country":"US"},{"ip":"104.171.154.97","port":"60000","country":"US"},{"ip":"104.171.154.98","port":"60000","country":"US"},{"ip":"104.171.154.99","port":"60000","country":"US"},{"ip":"104.171.154.100","port":"60000","country":"US"},{"ip":"104.171.154.101","port":"60000","country":"US"},{"ip":"104.171.154.102","port":"60000","country":"US"},{"ip":"104.171.154.103","port":"60000","country":"US"},{"ip":"104.171.154.104","port":"60000","country":"US"},{"ip":"104.171.154.105","port":"60000","country":"US"},{"ip":"104.171.154.106","port":"60000","country":"US"},{"ip":"104.171.154.107","port":"60000","country":"US"},{"ip":"104.171.154.108","port":"60000","country":"US"},{"ip":"104.171.154.109","port":"60000","country":"US"},{"ip":"104.171.154.110","port":"60000","country":"US"},{"ip":"104.171.154.111","port":"60000","country":"US"},{"ip":"104.171.154.112","port":"60000","country":"US"},{"ip":"104.171.154.113","port":"60000","country":"US"},{"ip":"104.171.154.114","port":"60000","country":"US"},{"ip":"104.171.154.115","port":"60000","country":"US"},{"ip":"104.171.154.116","port":"60000","country":"US"},{"ip":"104.171.154.117","port":"60000","country":"US"},{"ip":"104.171.154.118","port":"60000","country":"US"},{"ip":"104.171.154.119","port":"60000","country":"US"},{"ip":"104.171.154.120","port":"60000","country":"US"},{"ip":"104.171.154.121","port":"60000","country":"US"},{"ip":"104.171.154.122","port":"60000","country":"US"},{"ip":"104.171.154.123","port":"60000","country":"US"},{"ip":"104.171.154.124","port":"60000","country":"US"},{"ip":"104.171.154.125","port":"60000","country":"US"},{"ip":"104.171.154.126","port":"60000","country":"US"},{"ip":"104.171.154.127","port":"60000","country":"US"},{"ip":"104.171.154.128","port":"60000","country":"US"},{"ip":"104.171.154.129","port":"60000","country":"US"},{"ip":"104.171.154.130","port":"60000","country":"US"},{"ip":"104.171.154.131","port":"60000","country":"US"},{"ip":"104.171.154.132","port":"60000","country":"US"},{"ip":"104.171.154.133","port":"60000","country":"US"},{"ip":"104.171.154.134","port":"60000","country":"US"},{"ip":"104.171.154.135","port":"60000","country":"US"},{"ip":"104.171.154.136","port":"60000","country":"US"},{"ip":"104.171.154.137","port":"60000","country":"US"},{"ip":"104.171.154.138","port":"60000","country":"US"},{"ip":"104.171.154.139","port":"60000","country":"US"},{"ip":"104.171.154.140","port":"60000","country":"US"},{"ip":"104.171.154.141","port":"60000","country":"US"},{"ip":"104.171.154.142","port":"60000","country":"US"},{"ip":"104.171.154.143","port":"60000","country":"US"},{"ip":"104.171.154.144","port":"60000","country":"US"},{"ip":"104.171.154.145","port":"60000","country":"US"},{"ip":"104.171.154.146","port":"60000","country":"US"},{"ip":"104.171.154.147","port":"60000","country":"US"},{"ip":"104.171.154.148","port":"60000","country":"US"},{"ip":"104.171.154.149","port":"60000","country":"US"},{"ip":"104.171.154.150","port":"60000","country":"US"},{"ip":"104.171.154.151","port":"60000","country":"US"},{"ip":"104.171.154.152","port":"60000","country":"US"},{"ip":"104.171.154.153","port":"60000","country":"US"},{"ip":"104.171.154.154","port":"60000","country":"US"},{"ip":"104.171.154.155","port":"60000","country":"US"},{"ip":"104.171.154.156","port":"60000","country":"US"},{"ip":"104.171.154.157","port":"60000","country":"US"},{"ip":"104.171.154.158","port":"60000","country":"US"},{"ip":"104.171.154.159","port":"60000","country":"US"},{"ip":"104.171.154.160","port":"60000","country":"US"},{"ip":"104.171.154.161","port":"60000","country":"US"},{"ip":"104.171.154.162","port":"60000","country":"US"},{"ip":"104.171.154.163","port":"60000","country":"US"},{"ip":"104.171.154.164","port":"60000","country":"US"},{"ip":"104.171.154.165","port":"60000","country":"US"},{"ip":"104.171.154.166","port":"60000","country":"US"},{"ip":"104.171.154.167","port":"60000","country":"US"},{"ip":"104.171.154.168","port":"60000","country":"US"},{"ip":"104.171.154.169","port":"60000","country":"US"},{"ip":"104.171.154.170","port":"60000","country":"US"},{"ip":"104.171.154.171","port":"60000","country":"US"},{"ip":"104.171.154.172","port":"60000","country":"US"},{"ip":"104.171.154.173","port":"60000","country":"US"},{"ip":"104.171.154.174","port":"60000","country":"US"},{"ip":"104.171.154.175","port":"60000","country":"US"},{"ip":"104.171.154.176","port":"60000","country":"US"},{"ip":"104.171.154.177","port":"60000","country":"US"},{"ip":"104.171.154.178","port":"60000","country":"US"},{"ip":"104.171.154.179","port":"60000","country":"US"},{"ip":"104.171.154.180","port":"60000","country":"US"},{"ip":"104.171.154.181","port":"60000","country":"US"},{"ip":"104.171.154.182","port":"60000","country":"US"},{"ip":"104.171.154.183","port":"60000","country":"US"},{"ip":"104.171.154.184","port":"60000","country":"US"},{"ip":"104.171.154.185","port":"60000","country":"US"},{"ip":"104.171.154.186","port":"60000","country":"US"},{"ip":"104.171.154.187","port":"60000","country":"US"},{"ip":"104.171.154.188","port":"60000","country":"US"},{"ip":"104.171.154.189","port":"60000","country":"US"},{"ip":"104.171.154.190","port":"60000","country":"US"},{"ip":"104.171.154.191","port":"60000","country":"US"},{"ip":"104.171.154.192","port":"60000","country":"US"},{"ip":"104.171.154.193","port":"60000","country":"US"},{"ip":"104.171.154.194","port":"60000","country":"US"},{"ip":"104.171.154.195","port":"60000","country":"US"},{"ip":"104.171.154.196","port":"60000","country":"US"},{"ip":"104.171.154.197","port":"60000","country":"US"},{"ip":"104.171.154.198","port":"60000","country":"US"},{"ip":"104.171.154.199","port":"60000","country":"US"},{"ip":"104.171.154.200","port":"60000","country":"US"},{"ip":"104.171.154.201","port":"60000","country":"US"},{"ip":"104.171.154.202","port":"60000","country":"US"},{"ip":"104.171.154.203","port":"60000","country":"US"},{"ip":"104.171.154.204","port":"60000","country":"US"},{"ip":"104.171.154.205","port":"60000","country":"US"},{"ip":"104.171.154.206","port":"60000","country":"US"},{"ip":"104.171.154.207","port":"60000","country":"US"},{"ip":"104.171.154.208","port":"60000","country":"US"},{"ip":"104.171.154.209","port":"60000","country":"US"},{"ip":"104.171.154.210","port":"60000","country":"US"},{"ip":"104.171.154.211","port":"60000","country":"US"},{"ip":"104.171.154.212","port":"60000","country":"US"},{"ip":"104.171.154.213","port":"60000","country":"US"},{"ip":"104.171.154.214","port":"60000","country":"US"},{"ip":"104.171.154.215","port":"60000","country":"US"},{"ip":"104.171.154.216","port":"60000","country":"US"},{"ip":"104.171.154.217","port":"60000","country":"US"},{"ip":"104.171.154.218","port":"60000","country":"US"},{"ip":"104.171.154.219","port":"60000","country":"US"},{"ip":"104.171.154.220","port":"60000","country":"US"},{"ip":"104.171.154.221","port":"60000","country":"US"},{"ip":"104.171.154.222","port":"60000","country":"US"},{"ip":"104.171.154.223","port":"60000","country":"US"},{"ip":"104.171.154.224","port":"60000","country":"US"},{"ip":"104.171.154.225","port":"60000","country":"US"},{"ip":"104.171.154.226","port":"60000","country":"US"},{"ip":"104.171.154.227","port":"60000","country":"US"},{"ip":"104.171.154.228","port":"60000","country":"US"},{"ip":"104.171.154.229","port":"60000","country":"US"},{"ip":"104.171.154.230","port":"60000","country":"US"},{"ip":"104.171.154.231","port":"60000","country":"US"},{"ip":"104.171.154.232","port":"60000","country":"US"},{"ip":"104.171.154.233","port":"60000","country":"US"},{"ip":"104.171.154.234","port":"60000","country":"US"},{"ip":"104.171.154.235","port":"60000","country":"US"},{"ip":"104.171.154.236","port":"60000","country":"US"},{"ip":"104.171.154.237","port":"60000","country":"US"},{"ip":"104.171.154.238","port":"60000","country":"US"},{"ip":"104.171.154.239","port":"60000","country":"US"},{"ip":"104.171.154.240","port":"60000","country":"US"},{"ip":"104.171.154.241","port":"60000","country":"US"},{"ip":"104.171.154.242","port":"60000","country":"US"},{"ip":"104.171.154.243","port":"60000","country":"US"},{"ip":"104.171.154.244","port":"60000","country":"US"},{"ip":"104.171.154.245","port":"60000","country":"US"},{"ip":"104.171.154.246","port":"60000","country":"US"},{"ip":"104.171.154.247","port":"60000","country":"US"},{"ip":"104.171.154.248","port":"60000","country":"US"},{"ip":"104.171.154.249","port":"60000","country":"US"},{"ip":"104.171.154.250","port":"60000","country":"US"},{"ip":"104.171.154.251","port":"60000","country":"US"}
    i = 1
    for ip in pids:
        proxy_ip = ProxyIp(
            id=i,
            ip_address=ip['ip'],
            port=ip['port'],
            country=ip['country'],
            username='wolfgramm',
            password='rN7rdcnx5W',
        )
        db.session.add(proxy_ip)
        i += 1
    db.session.commit()
    return "True"


@userbp.route('/reset_password/<user_id>/<reset_token>', methods=['GET', 'POST'])
def reset_password(user_id, reset_token):
    """ Function to reset password in the application """
    try:
        form = user_forms.resetpassword()
        if form.validate_on_submit():
            user = User.by_id(user_id)
            if user:
                if user.remember_token == reset_token:
                    user.password = misc.create_ra_hash(form.new_password.data)
                    user.remember_token = ''
                    db.session.commit()
                    flash(RESET_PASSWORD, 'success')
                    return redirect(url_for('userbp.user_signin'))
                else:
                    flash(RESET_PASSWORD_ERROR, 'danger')
                    return redirect(url_for('userbp.forgot_password'))
            else:
                flash(USER_NOT_EXISTS, 'danger')

        return render_template('user/reset_password.html', form=form)
    except Exception as err:
        errorlog.error('Reset Password Error', details=str(err))
        return render_template('error.html', message="Error!")


@userbp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """ Function to integrate forgot password functionality in the application """
    try:
        form = user_forms.forgotpassword()
        if form.validate_on_submit():
            recipient = form.email.data
            user = User.load_user(recipient)
            if user:
                random_string = urandom(15).encode('hex')
                user.remember_token = random_string
                db.session.commit()
                user_id = user.id
                subject = RESET_PASSWORD_EMAIL_SUBJECT
                body = '<a href = "'+url_for('userbp.reset_password',user_id=str(user_id), reset_token=random_string, _external=True)+'">Click Here</a> to reset your password'
                send_email(recipient, subject, body)
                flash(RESET_PASSWORD_LINK, 'success')
                return redirect(url_for('userbp.user_signin'))
            else:
                flash(EMAIL_NOT_EXISTS, 'danger')

        return render_template('user/forgot_password.html', form=form)
    except Exception as err:
        errorlog.error('Forgot Password Error', details=str(err))
        return render_template('error.html', message="Error!")


@userbp.route('/profile', methods=['GET', 'POST'])
def profile():
    """ Function to display profile in the application """
    try:
        get_uid = request.args.get('userid', default=None, type=int)
        uid = current_user.id
        if get_uid is not None and current_user.user_type == 'admin':
            uid = get_uid
        user_detail = User.by_id(uid)
        return render_template('user/profile.html', user_detail=user_detail)
    except Exception as err:
        errorlog.error('Forgot Password Error', details=str(err))
        return render_template('error.html', message="Error!")


@userbp.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    """ Function to integrate option to edit profile in the application """
    try:
        get_uid = request.args.get('userid', default=None, type=int)
        uid = current_user.id
        profile_redirect = url_for('userbp.profile')
        if get_uid is not None and current_user.user_type == 'admin':
            uid = get_uid
            profile_redirect = url_for('userbp.profile', userid=uid)
        user_obj = User.by_id(uid)
        profile_form = user_forms.profile(obj=user_obj)
        state_list = get_states()
        profile_form.state.choices = [(k, v) for k,v in state_list.items()]
        if profile_form.validate_on_submit():
            v_email = json.loads(validate_email(profile_form.email.data, uid))
            if v_email['status']:
                flash(v_email['message'], 'danger')

            else:
                user_obj.first_name = profile_form.first_name.data
                user_obj.last_name = profile_form.last_name.data
                user_obj.city = profile_form.city.data
                user_obj.state = profile_form.state.data
                user_obj.email = profile_form.email.data
                user_obj.phone = profile_form.phone.data
                user_obj.zipcode = profile_form.zipcode.data
                user_obj.address1 = profile_form.address1.data
                user_obj.address2 = profile_form.address2.data
                db.session.commit()

                flash(PROFILE_UPDATE_SUCCESS, 'success')
                return redirect(profile_redirect)
        return render_template('user/edit_profile.html', pform=profile_form)
    except Exception as err:
        errorlog.error('edit_profile  Error', details=str(err))
        return render_template('error.html', message="Error!")


@userbp.route('/customers', methods=['GET', 'POST'])
def customers():
    """ Function to view customers """
    if current_user.user_type != 'admin':
        flash(ADMIN_ACCESS_ERROR, 'danger')
        return redirect(url_for('userbp.dashboard'))
    user_size = 10

    start_id = 0
    sf = OrderedDict()
    page_no = request.args.get('page', default=None, type=int)
    order_by = request.args.get('order_by', default=None, type=str)
    sf['first_name'] = request.args.get('first_name', default=None, type=str)
    sf['last_name'] = request.args.get('last_name', default=None, type=str)
    sf['email'] = request.args.get('email', default=None, type=str)
    sf_list = []
    for k, v in sf.items():
        if v not in ['None', 0, '0', None, ' ', '']:
            sf_list.append('%s=%s' % (k, v))
    sfl = "&".join(sf_list)
    if page_no is not None:
        start_id = page_no

    start, stop = user_size * start_id, user_size * (start_id + 1)
    offset_start = {'start': start, 'stop': stop}

    customers = User.all_users(offset_start, order_by, sf)
    nextid, previd = get_prev_next(customers, start_id, user_size)
    return render_template('user/customers.html', customers=customers,
                           nextid=nextid, previd=previd, action='customer',
                           sfl=sfl, sf=sf
                           )


def get_prev_next(obj,widx,wsize):
    """Function to get previous and next page no"""
    # Setup pagination variables.
    if obj is None:
        next_id = None
        prev_id = None

    if widx == 0:
        prev_id = None
    else:
        prev_id = widx - 1

    if len(obj) < wsize:
        next_id = None
    else:
        next_id = widx + 1
    return next_id, prev_id


@userbp.route('/change_status/<uid>/<status>', methods=['GET', 'POST'])
def change_status(uid, status):
    """Function to change users status """
    user_detail = User.by_id(uid)
    user_detail.is_active = int(status)
    db.session.commit()
    if status == '0':
        flash(DEACTIVATE_USER_SUCCESS, 'success')
    else:
        flash(ACTIVATE_USER_SUCCESS, 'success')
    return redirect(url_for('userbp.customers'))



