import time
from datetime import datetime
from math import ceil
from threading import Thread

from flask import (Blueprint, render_template)
from sqlalchemy import func

from app import db
from app.logger_setup import errorlog, activitylog
from app.models import User, InstaUsers, TargetAccount, TargetAccountFollower, \
    ProxyIp, DirectMessage
from app.tools.InstagramAPI import InstagramAPI
from app.tools.email import send_email
from app.tools.messages import *
from app.tools.misc import get_insta_object

cronbp = Blueprint('cronbp', __name__, url_prefix='/cron')


@cronbp.route('/run-cron-save-followers', methods=['GET'])
def run_cron_save_followers():
    try:
        count_users = User.count_users().total_users
        activitylog.info('Save followers cron run')
        user_size = 1000

        # Index of where we are in the slice.
        no_of_threads = int(ceil(float(count_users)/user_size))
        if no_of_threads > 100:
            no_of_threads = 100
            user_size = ceil(float(count_users)/no_of_threads)
        thr = list()
        msg = CRON_TWOFACTOR_ERROR
        html = render_template('email.html', action='cron', msg=msg)
        for i in range(no_of_threads):
            start_id = i
            start, stop = user_size * start_id, user_size * (start_id + 1)
            offset_start = {'start': start, 'stop': stop}
            thr.append(Thread(target=save_followers, args=[offset_start, html]))
            thr[i].start()
        return "True"

    except Exception as err:
        errorlog.error('run cron Failed', details=str(err))

    return 'True'


@cronbp.route('/run-cron-follow-request', methods=['GET'])
def run_cron_follow_request():
    try:
        count_users = User.count_users().total_users
        activitylog.info('follow request cron run')
        user_size = 1000

        # Index of where we are in the slice.
        msg = CRON_TWOFACTOR_ERROR
        html = render_template('email.html', action='cron', msg=msg)
        no_of_threads = int(ceil(float(count_users)/user_size))
        if no_of_threads > 100:
            no_of_threads = 100
            user_size = ceil(float(count_users)/no_of_threads)
        thr = list()
        for i in range(no_of_threads):
            start_id = i
            start, stop = user_size * start_id, user_size * (start_id + 1)
            offset_start = {'start': start, 'stop': stop}
            thr.append(Thread(target=insta_follow_request, args=[offset_start, html]))
            thr[i].start()
        return "True"

    except Exception as err:
        errorlog.error('run cron Failed', details=str(err))

    return 'True'


@cronbp.route('/run-cron-check-followback', methods=['GET'])
def run_cron_check_follow_back():
    try:
        count_users = User.count_users().total_users
        activitylog.info('follow back cron run')
        user_size = 1000
        msg = CRON_TWOFACTOR_ERROR
        html = render_template('email.html', action='cron', msg=msg)
        # Index of where we are in the slice.
        no_of_threads = int(ceil(float(count_users)/user_size))
        if no_of_threads > 100:
            no_of_threads = 100
            user_size = ceil(float(count_users)/no_of_threads)
        thr = list()
        for i in range(no_of_threads):
            start_id = i
            start, stop = user_size * start_id, user_size * (start_id + 1)
            offset_start = {'start': start, 'stop': stop}
            thr.append(Thread(target=check_follow_backs_insta, args=[offset_start, html]))
            thr[i].start()
        return "True"

    except Exception as err:
        errorlog.error('run cron Failed', details=str(err))

    return 'True'


def save_followers(offset_start, html):
    """ Function to followers for profile, location and hash tags """
    try:
        allusers = User.get_all(offset_start)
        for row in allusers:
            if row.User.access_token and row.User.is_active and \
                    row.User.payment_status and row.User.cron_status:
                get_proxy = ProxyIp.get_proxy(row.User.proxy_ip_id)
                InstaAPI = get_insta_object(row.User.access_token, get_proxy, row.User)
                if not isinstance(InstaAPI, InstagramAPI):
                    if InstaAPI == 'code_required':
                        get_user = User.by_id(row.User.id)
                        get_user.cron_status = False
                        subject = TWO_FACTOR_SUBJECT
                        recipient = row.User.email
                        send_email(recipient, subject, html)

                    continue

                followers_list = InstaAPI.getTotalFollowers(row.UserDetails.user_insta_id)
                get_followelist = []
                for flist in followers_list:
                    get_followelist.append(str(flist['pk']))
                following_list = InstaAPI.getTotalFollowings(row.UserDetails.user_insta_id)
                get_followinglist = []
                for flist in following_list:
                    get_followinglist.append(str(flist['pk']))
                save_target_followers(row, InstaAPI, get_followelist, get_followinglist)
                save_location_followers(row, InstaAPI, get_followelist, get_followinglist)
                save_hash_tag_followers(row, InstaAPI, get_followelist, get_followinglist)
                time.sleep(30)
        db.session.commit()
    except Exception as err:
        errorlog.error('save target followers Failed', details=str(err))

    return 'True'


def insta_follow_request(offset_start, html):
    """ Function to send follow request """
    try:
        allusers = User.get_all(offset_start)

        for row in allusers:
            if row.User.access_token and row.User.is_active and \
                    row.User.payment_status and row.User.cron_status:
                get_proxy = ProxyIp.get_proxy(row.User.proxy_ip_id)
                InstaAPI = get_insta_object(row.User.access_token, get_proxy, row.User)
                if not isinstance(InstaAPI, InstagramAPI):
                    if InstaAPI == 'code_required':
                        get_user = User.by_id(row.User.id)
                        get_user.cron_status = False
                        subject = TWO_FACTOR_SUBJECT
                        recipient = row.User.email
                        send_email(recipient, subject, html)
                    continue
                # activitylog.info('send-follow-request cron run for user_id:'+str(row.User.id))
                followers_list = InstaAPI.getTotalFollowers(row.UserDetails.user_insta_id)
                get_followelist = []
                for flist in followers_list:
                    get_followelist.append(flist['pk'])
                send_follow_request(row, InstaAPI)
                time.sleep(30)
        db.session.commit()

    except Exception as err:
        errorlog.error('Send Follow Request Failed', details=str(err))

    return 'True'


def check_follow_backs_insta(offset_start, html):
    """ Function to check follow backs """
    try:
        allusers = User.get_all(offset_start)
        for row in allusers:
            if row.User.access_token and row.User.is_active and \
                    row.User.payment_status and row.User.cron_status:
                get_proxy = ProxyIp.get_proxy(row.User.proxy_ip_id)
                InstaAPI = get_insta_object(row.User.access_token, get_proxy, row.User)
                if not isinstance(InstaAPI, InstagramAPI):
                    if InstaAPI == 'code_required':
                        get_user = User.by_id(row.User.id)
                        get_user.cron_status = False
                        subject = TWO_FACTOR_SUBJECT
                        recipient = row.User.email
                        send_email(recipient, subject, html)
                    continue
                # activitylog.info('cron run for user_id:'+str(row.User.id))
                followers_list = InstaAPI.getTotalFollowers(row.UserDetails.user_insta_id)
                get_followelist = []
                for flist in followers_list:
                    get_followelist.append(flist['pk'])
                check_follow_backs(row, InstaAPI, followers_list, get_followelist)
                time.sleep(30)
        db.session.commit()

    except Exception as err:
        errorlog.error('check_follow_backs Failed', details=str(err))

    return 'True'


def send_follow_request(row, InstaAPI):
    """ Function to get pending list for sending follow request """
    try:

        get_target_accounts = TargetAccount.get_target(row.User.id, 0, None)
        tfollowers = {}
        for tlist in get_target_accounts:
            tfollowers[tlist.insta_id] = TargetAccountFollower.get_pending_list(
                row.User.id, tlist.insta_id
            )
            follow(InstaAPI, row.User.id, tfollowers)

        loca_followers = {}
        get_target_loc_accounts = TargetAccount.get_target(row.User.id, 1, None)
        for tlist in get_target_loc_accounts:
            loca_followers[tlist.insta_id] = \
                TargetAccountFollower.get_pending_list(row.User.id, tlist.insta_id)
            follow(InstaAPI, row.User.id, loca_followers)

        has_followers = {}
        get_target_hash_accounts = TargetAccount.get_target(row.User.id, 2, None)
        for tlist in get_target_hash_accounts:
            has_followers[tlist.insta_id] = \
                TargetAccountFollower.get_pending_list(row.User.id, tlist.insta_id)
            follow(InstaAPI, row.User.id, has_followers)
        db.session.commit()
    except Exception as err:
        errorlog.error('Send Follow Request Failed', details=str(err))

    return 'True'


def follow(InstaAPI, user_id, tfollowers):
    """ Function to call Insta API to send follow request """
    try:
        for insta_id, followers_id in tfollowers.items():

            for i_id in followers_id:

                followres = InstaAPI.follow(str(i_id.follower_id))
                if followres:
                    tf = TargetAccountFollower.get_target_follower(
                        user_id, i_id.follower_id)
                    tf.request_sent = True
                    get_target_account = \
                        TargetAccount.by_instauserid(user_id, insta_id)
                    get_target_account.actions = \
                        int(get_target_account.actions) + 1

    except Exception as err:
        errorlog.error('Failed to send follow request.', details=str(err))


def save_target_followers(users, InstaAPI, get_followelist, get_followinglist):
    """ Function to save target profile account followers """
    try:
        get_user_list = TargetAccount.get_userlist(users.User.id)
        for user in get_user_list:
            profile_followers = get_target_followers(InstaAPI, user.insta_id, user.next_max_id)
            gettarget = TargetAccount.by_instaid(user.insta_id)
            if gettarget.next_max_id == profile_followers['next_max_id']:
                gettarget.is_added = 1
            gettarget.next_max_id = profile_followers['next_max_id']
            for flist in profile_followers['list']:
                if str(flist['pk']) in get_followelist:
                    continue
                if str(flist['pk']) in get_followinglist:
                    continue
                get_exist_follower = TargetAccountFollower.get_target_follower(
                    users.User.id, str(flist['pk']))
                if get_exist_follower:
                    continue

                target_followers = TargetAccountFollower(
                    user_id=users.User.id,
                    target_account_id=user.insta_id,
                    follower_id=str(flist['pk']),
                    username=str(flist['username']),
                    created_at=datetime.now().strftime('%Y-%m-%d'),
                    updated_at=datetime.now().strftime('%Y-%m-%d'),
                    request_sent=False,
                    followback=False
                )
                db.session.add(target_followers)
        db.session.commit()
    except Exception as err:
        errorlog.error('Save Target Followers Failed', details=str(err))
    return "True"


def save_location_followers(users, InstaAPI, get_followelist,get_followinglist):
    """ Function to save target location followers """
    try:
        get_loca_list = TargetAccount.get_location_list(users.User.id)
        for user in get_loca_list:
            tag_followers = get_location_followers(InstaAPI, user.insta_id)
            gettarget = TargetAccount.by_instaid(user.insta_id)
            if gettarget.next_max_id == tag_followers['next_max_id']:
                gettarget.is_added = 1
            gettarget.next_max_id = tag_followers['next_max_id']
            for flist in tag_followers['list']:
                if str(flist['user']['pk']) in get_followelist:
                    continue
                if str(flist['user']['pk']) in get_followinglist:
                    continue
                get_exist_follower = TargetAccountFollower.get_target_follower(
                    users.User.id, str(flist['user']['pk']))
                if get_exist_follower:
                    continue

                target_followers = TargetAccountFollower(
                    user_id=users.User.id,
                    target_account_id=user.insta_id,
                    follower_id=str(flist['user']['pk']),
                    username=str(flist['user']['username']),
                    created_at=datetime.now().strftime('%Y-%m-%d'),
                    updated_at=datetime.now().strftime('%Y-%m-%d'),
                    request_sent=False,
                    followback=False
                )
                db.session.add(target_followers)
        db.session.commit()
    except Exception as err:
        errorlog.error('Save Location Followers Failed', details=str(err))

    return "True"


def save_hash_tag_followers(users, InstaAPI, get_followelist, get_followinglist):
    """ Function to save target hashtag followers """
    try:
        get_user_has_list = TargetAccount.get_hash_list(users.User.id)
        for user in get_user_has_list:
            tag_followers = get_hash_tag_followers(InstaAPI, user.user_name)
            gettarget = TargetAccount.by_instaid(user.insta_id)
            if gettarget.next_max_id == tag_followers['next_max_id']:
                gettarget.is_added = 1
            gettarget.next_max_id = tag_followers['next_max_id']
            for flist in tag_followers['list']:
                if str(flist['user']['pk']) in get_followelist:
                    continue
                if str(flist['user']['pk']) in get_followinglist:
                    continue
                get_exist_follower = TargetAccountFollower.get_target_follower(
                    users.User.id, str(flist['user']['pk']))
                if get_exist_follower:
                    continue

                target_followers = TargetAccountFollower(
                    user_id=users.User.id,
                    target_account_id=user.insta_id,
                    follower_id=str(flist['user']['pk']),
                    username=str(flist['user']['username']),
                    created_at=datetime.now().strftime('%Y-%m-%d'),
                    updated_at=datetime.now().strftime('%Y-%m-%d'),
                    request_sent=False,
                    followback=False
                )
                db.session.add(target_followers)
        db.session.commit()
    except Exception as err:
        errorlog.error('Save Hashtag Followers Failed', details=str(err))
    return "True"


def get_target_followers(InstaAPI, target_id, next_id=None):
    """ Function to call Insta API to save target profile account followers """
    if next_id is None:
        next_id = ''
    InstaAPI.getUserFollowers(target_id, maxid=next_id)
    next_max_id = InstaAPI.LastJson.get('next_max_id', '')
    total_followers = []
    if 'users' in InstaAPI.LastJson:
        total_followers = InstaAPI.LastJson['users']
    data = dict(count=len(total_followers),
                list=total_followers,
                next_max_id=next_max_id)

    return data


def get_hash_tag_followers(InstaAPI, target_id, next_id=None):
    """ Function to call Insta API to save target hash tag followers """
    InstaAPI.getHashtagFeed(target_id, maxid=next_id)
    next_max_id = None
    tag_followers = []
    if 'story' in InstaAPI.LastJson:
        tag_followers = InstaAPI.LastJson['story']['items']
        next_max_id = InstaAPI.LastJson.get('next_max_id', '')
    data = dict(count=len(tag_followers),
                list=tag_followers,
                next_max_id=next_max_id)

    return data


def get_location_followers(InstaAPI, target_id, next_id=None):
    """ Function to call Insta API to save target location followers """
    loc = InstaAPI.getLocationFeed(target_id, maxid='')
    next_max_id = None
    tag_followers = []
    if 'story' in InstaAPI.LastJson:
        tag_followers = InstaAPI.LastJson['story']['items']
        next_max_id = InstaAPI.LastJson.get('next_max_id', '')
    data = dict(count=len(tag_followers),
                list=tag_followers,
                next_max_id=next_max_id)

    return data


def check_follow_backs(row, InstaAPI, followers_list, get_followelist):
    """ Function to call Insta API to check if user follows back """
    try:

        existing_followers = TargetAccountFollower.user_followers(row.User.id)
        following_list = InstaAPI.getTotalFollowings(row.UserDetails.user_insta_id)
        userpost = InstaAPI.getTotalUserFeed(row.UserDetails.user_insta_id)
        instaDetails = InstaUsers(
            total_followers=len(followers_list),
            total_followings=len(following_list),
            user_id=row.User.id,
            total_likes=len(userpost),
            created_at=func.now()
        )
        db.session.add(instaDetails)
        for efoll in existing_followers:
            if efoll.follower_id in get_followelist:
                tf = TargetAccountFollower.get_target_follower(
                    row.User.id, efoll.follower_id)
                if tf.followback == 1:
                    continue
                tf.followback = 1

                tget_acc = TargetAccount.by_instaid(tf.target_account_id)
                fbacks = int(tget_acc.followbacks)
                tget_acc.followbacks = fbacks + 1
                get_message = DirectMessage.byuser_id(row.User.id)
                if get_message:
                    msg = get_message.message.replace("{@username}", str(efoll.username))
                else:
                    msg = DIRECT_MESSAGE_DEFAULT.replace("{@username}", str(efoll.username))
                msgres = InstaAPI.direct_message(msg, efoll.follower_id)

        db.session.commit()
    except Exception as err:
        errorlog.error('Check follow backs Failed', details=str(err))

    return 'True'
