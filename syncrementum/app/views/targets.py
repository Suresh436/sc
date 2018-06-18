import base64
import pickle
from datetime import datetime
from random import randint

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
from app.logger_setup import errorlog, activitylog
from app.tools import misc
from app.models import User, UserDetails, InstaUsers, TargetAccount, TargetAccountFollower, ProxyIp, DirectMessage
from app.tools.messages import *
from app.tools.misc import get_insta_object, insta_logout, insta_login

targetsbp = Blueprint('targetsbp', __name__, url_prefix='/targets')


@targetsbp.route('/', methods=['GET', 'POST'])
@targetsbp.route('/profile_target', methods=['GET', 'POST'])
@login_required
def profile_target():
    """ Function to show profile targets """
    try:
        qry = request.args.get('q', default=None, type=str)
        get_uid = request.args.get('userid', default=None, type=int)
        uid = current_user.id
        if get_uid is not None and current_user.user_type == 'admin':
            uid = get_uid

        pf = TargetAccount.get_target(uid, 0, qry)
        if qry is not None:
            res = dict()
            res['status'] = 'success'
            res['account'] = render_template('targets/query_common.html',
                                             pf=pf, getpage='profile')
            return json.dumps(res)
        get_message = DirectMessage.byuser_id(uid)
        if get_message:
            message = get_message.message
        else:
            message = DIRECT_MESSAGE_DEFAULT
        qry_template = render_template('targets/query_common.html', pf=pf,
                                       getpage='profile')
        return render_template('targets/common.html', pf=pf,
                               account_class="active", get_page='profile_target',
                               message=message, qry_template=qry_template,
                               btn_content='Add Target',
                               input_id='search-target-users', action="targets"
                               )
    except Exception as err:
        errorlog.error('Profile Target Error', details=str(err))
        return render_template('error.html', message="Error!")


@targetsbp.route('/location_target', methods=['GET', 'POST'])
@login_required
def location_target():
    """ Function to cshow location targets """
    try:
        qry = request.args.get('q', default=None, type=str)
        get_uid = request.args.get('userid', default=None, type=int)
        uid = current_user.id
        if get_uid is not None and current_user.user_type == 'admin':
            uid = get_uid
        loc_targets = TargetAccount.get_target(uid, 1, qry)
        if qry is not None:
            res = dict()
            res['status'] = 'success'
            res['account'] = render_template('targets/query_common.html',
                                             loc_targets=loc_targets,
                                             getpage='location')
            return json.dumps(res)
        qry_template = render_template('targets/query_common.html',
                                       loc_targets=loc_targets,
                                       getpage='location')
        return render_template('targets/common.html', loc_targets=loc_targets,
                               location_class="active", get_page='location_target',
                               qry_template=qry_template, btn_content='Add Location',
                               input_id='search-target-location', message='',
                               action="targets"
                               )
    except Exception as err:
        errorlog.error('Location Target Error', details=str(err))
        return render_template('error.html', message="Error!")


@targetsbp.route('/hash_target', methods=['GET', 'POST'])
@login_required
def hash_target():
    """ Function to show hash_targets """
    try:
        qry = request.args.get('q', default=None, type=str)
        get_uid = request.args.get('userid', default=None, type=int)
        uid = current_user.id
        if get_uid is not None and current_user.user_type == 'admin':
            uid = get_uid
        hash_targets = TargetAccount.get_target(uid, 2, qry)
        if qry is not None:
            res = dict()
            res['status'] = 'success'
            res['account'] = render_template('targets/query_common.html',
                                             hash_targets=hash_targets,
                                             getpage='hashtag')
            return json.dumps(res)
        qry_template = render_template('targets/query_common.html',
                                       hash_targets=hash_targets,
                                       getpage='hashtag')
        return render_template('targets/common.html',
                               hash_targets=hash_targets,
                               hash_class='active', action="targets", message='',
                               get_page='hash_target', qry_template=qry_template,
                               btn_content='Add Hashtag',
                               input_id='search-target-hash')
    except Exception as err:
        errorlog.error('Hash Target Error', details=str(err))
        return render_template('error.html', message="Error!")


@targetsbp.route('/delete_target', methods=['GET', 'POST'])
def delete_target():
    """ Function to delete selected target """
    res = dict()
    try:
        qry = request.args.get('item', default=None, type=str)
        t_type = request.args.get('type', default=None, type=int)
        get_uid = request.args.get('userid', default=None, type=int)
        uid = current_user.id
        if get_uid is not None and current_user.user_type == 'admin':
            uid = get_uid
        hash_targets = TargetAccount.by_iduserid(uid, t_type, qry)
        if hash_targets:
            db.session.delete(hash_targets)
            db.session.commit()

        res['status'] = 'success'
        return json.dumps(res)
    except Exception as err:
        errorlog.error('Delete Target Error', details=str(err))
        res['status'] = 'error'
        return json.dumps(res)


@targetsbp.route('/send_message', methods=['GET', 'POST'])
def send_message():
    """ Function to send direct message """
    res = dict()
    try:
        request_param = json.loads(request.data)
        get_uid = request.args.get('userid', default=None, type=int)
        user_detail = current_user
        if get_uid is not None:
            user_detail = User.by_id(get_uid)
        if user_detail.access_token:
            get_proxy = ProxyIp.get_proxy(current_user.proxy_ip_id)
            InstaAPI = insta_login(user_detail.access_token, get_proxy)
            if not isinstance(InstaAPI, InstagramAPI):
                res['status'] = 'error',
                res['data'] = []
                return json.dumps(res)
        else:
            res['status'] = 'error',
            res['data'] = []
            return json.dumps(res)
        msgres = InstaAPI.direct_message(request_param['message'],
                                         request_param['insta_id'])
        if msgres:
            res['status'] = 'success'
        else:
            res['status'] = 'error'
        return json.dumps(res)
    except Exception as err:
        errorlog.error('send messageError', details=str(err))
        res['status'] = 'error'
        return json.dumps(res)




