import ast
from random import randint

from flask_login import UserMixin
from sqlalchemy import (or_, and_)
from sqlalchemy.sql import func

from app import db
from tools import misc


def setup_ordering(oby):
    direction = oby.split('_')[-1]
    order_by = oby.split('_')[:-1]
    m = __import__('app.models')
    m = getattr(m.models, order_by[0].title())
    m = getattr(m, order_by[1])

    if direction == 'asc':
        return m.asc()
    elif direction == 'desc':
        return m.desc()


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'syncrementum'}
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String)
    password = db.Column(db.String)
    access_token = db.Column(db.String)
    client_id = db.Column(db.String)
    remember_token = db.Column(db.String)
    saved_target_accounts = db.Column(db.Boolean)
    phone = db.Column(db.String)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    user_ip = db.Column(db.String)
    proxy_ip_id = db.Column(db.Integer)
    payment_status = db.Column(db.Integer)
    address1 = db.Column(db.String)
    address2 = db.Column(db.String)
    city = db.Column(db.String)
    state = db.Column(db.String)
    zipcode = db.Column(db.Integer)
    cron_status = db.Column(db.Boolean)
    user_type = db.Column(db.String)
    is_active = db.Column(db.Boolean)

    def verify_password(self, password):
        res = misc.check_ra_pwd(password, self.password)
        if res == "1":
            return True
        else:
            return False

    @property
    def user_name(self):
        return self.name

    @classmethod
    def load_user(cls, email):
        return db.session.query(
            User
        ).select_from(User
        ).filter(User.email == email
        ).first()

    @classmethod
    def by_id(cls, uid):
        return db.session.query(
            User,
        ).select_from(User
        ).filter(User.id == uid
        ).first()

    @classmethod
    def get_all(cls, offsetval=None):
        start = stop = None
        if offsetval is not None:
            start = offsetval['start']
            stop = offsetval['stop']
        return db.session.query(
            User,
            UserDetails,
        ).select_from(User
        ).join(UserDetails, UserDetails.user_id == User.id
        ).filter(cls.cron_status == 1
        ).filter(or_(cls.payment_status == 1, cls.payment_status == 2)
        ).slice(start, stop
        ).all()

    @classmethod
    def all_users(cls, offsetval=None, oby=None, searchvar=None):
        start = stop = None
        try:
            if oby is not None:
                direction = oby.split('_')[-1]
                attr = oby.rsplit('_', 1)[0]
                m = __import__('app.models')
                m = getattr(m.models, 'User')
                m = getattr(m, attr)
                if direction == 'asc':
                    ob = m.asc()
                else:
                    ob = m.desc()
            else:
                ob = cls.id.asc()
        except Exception as ee:
            print str(ee)
            ob = cls.id.asc()
        if offsetval is not None:
            start = offsetval['start']
            stop = offsetval['stop']
        if searchvar and searchvar != 'None':
            fn = ln = em = ''
            if searchvar['first_name'] is not None:
                fn = cls.first_name.like('%'+searchvar['first_name']+'%')
            if searchvar['last_name'] is not None:
                ln = cls.last_name.like('%'+searchvar['last_name']+'%')
            if searchvar['email'] is not None:
                em = cls.email.like('%'+searchvar['email']+'%')
            ss = and_(fn, ln, em)
        else:
            ss = ''
        return db.session.query(
            User
        ).select_from(User
        ).filter(cls.user_type != 'admin'
        ).filter(ss
        ).order_by(ob
        ).slice(start, stop
        ).all()

    @classmethod
    def count_users(cls):

        return db.session.query(
            func.count(cls.id).label('total_users'),
        ).select_from(User
        ).join(UserDetails, UserDetails.user_id == User.id
        ).filter(cls.cron_status == 1
        ).filter(or_(cls.payment_status == 1, cls.payment_status == 2)
        ).first()


class InstaUsers(db.Model, UserMixin):
    __tablename__ = 'insta_user_contact'
    __table_args__ = {'schema': 'syncrementum'}
    id = db.Column(db.Integer, primary_key=True)
    total_followers = db.Column(db.Integer)
    total_followings = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    total_likes = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)

    @classmethod
    def count_current(cls, uid):
        return db.session.query(
            cls
        ).select_from(cls
        ).filter(cls.user_id == uid
        ).order_by(cls.id.desc()
        ).first()

class UserDetails(db.Model, UserMixin):
    __tablename__ = 'user_details'
    __table_args__ = {'schema': 'syncrementum'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    user_insta_id = db.Column(db.Integer)
    full_name = db.Column(db.String)
    username = db.Column(db.String)
    profile_picture = db.Column(db.String)
    user_follows = db.Column(db.Integer)
    user_followed_by = db.Column(db.Integer)
    total_media = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    @classmethod
    def by_instaid(cls, instaid):
        return db.session.query(
            cls,
        ).select_from(cls
        ).filter(cls.user_insta_id == instaid
        ).first()

    @classmethod
    def by_userid(cls, uid):
        return db.session.query(
            cls,
        ).select_from(cls
        ).filter(cls.user_id == uid
        ).first()


class TargetAccount(db.Model, UserMixin):
    __tablename__ = 'target_accounts'
    __table_args__ = {'schema': 'syncrementum'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    insta_id = db.Column(db.Integer)
    user_name = db.Column(db.String)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    actions = db.Column(db.Integer)
    followbacks = db.Column(db.Integer)
    next_max_id = db.Column(db.String)
    type = db.Column(db.Integer)
    is_added = db.Column(db.Integer)
    profile_image = db.Column(db.String)

    @classmethod
    def by_instaid(cls, instaid):
        return db.session.query(
            cls,
        ).select_from(cls
        ).filter(cls.insta_id == instaid
        ).first()

    @classmethod
    def by_iduserid(cls, uid, type, tid):
        return db.session.query(
            cls,
        ).select_from(cls
        ).filter(cls.id == tid
        ).filter(cls.user_id == uid
        ).filter(cls.type == type
        ).first()

    @classmethod
    def by_username(cls, usr_name, type, uid):
        return db.session.query(
            cls,
        ).select_from(cls
        ).filter(cls.type == type
        ).filter(cls.user_name == usr_name
        ).filter(cls.user_id == uid
        ).first()

    @classmethod
    def by_instauserid(cls, uid,  instaid):
        return db.session.query(
            cls,
        ).select_from(cls
        ).filter(cls.insta_id == instaid
        ).filter(cls.user_id == uid
        # ).filter(cls.type == 0
        ).first()

    @classmethod
    def get_list(cls, uid):
        return db.session.query(
            cls,
        ).select_from(cls
        ).filter(cls.user_id == uid
        ).all()

    @classmethod
    def get_hash_list(cls, uid):
        return db.session.query(
            cls,
        ).select_from(cls
        ).filter(cls.user_id == uid
        ).filter(cls.is_added == 0
        ).filter(cls.type == 2
        ).all()

    @classmethod
    def get_userlist(cls, uid):
        return db.session.query(
            cls,
        ).select_from(cls
        ).filter(cls.user_id == uid
        ).filter(cls.is_added == 0
        ).filter(cls.type == 0
        ).all()

    @classmethod
    def get_location_list(cls, uid):
        return db.session.query(
            cls,
        ).select_from(cls
        ).filter(cls.user_id == uid
        ).filter(cls.type == 1
        ).filter(cls.is_added == 0
        ).all()

    @classmethod
    def get_target(cls, uid, type, qry):
        search_filter = ''
        if qry is not None:
            search_filter = cls.user_name.like("%"+qry+"%")

        return db.session.query(
            cls,
        ).select_from(cls
        ).filter(cls.user_id == uid
        ).filter(cls.type == type
        ).filter(search_filter
        ).all()

    @classmethod
    def best_locations(cls, uid):
        return db.session.query(
            cls,
        ).select_from(cls
        ).filter(cls.user_id == uid
        ).filter(cls.type == 1
        ).order_by(cls.followbacks.desc()
        ).limit(5
        ).all()

    @classmethod
    def best_account(cls, uid):
        return db.session.query(
            cls,
        ).select_from(cls
        ).filter(cls.user_id == uid
        ).filter(cls.type == 0
        ).order_by(cls.followbacks.desc()
        ).limit(5
        ).all()

    @classmethod
    def best_hashtag(cls, uid):
        return db.session.query(
            cls,
        ).select_from(cls
        ).filter(cls.user_id == uid
        ).filter(cls.type == 2
        ).order_by(cls.followbacks.desc()
        ).limit(5
        ).all()

    @classmethod
    def worst_account(cls, uid):
        return db.session.query(
            cls,
        ).select_from(cls
        ).filter(cls.user_id == uid
        ).filter(cls.type == 0
        ).order_by(cls.followbacks.asc()
        ).limit(5
        ).all()


class TargetAccountFollower(db.Model, UserMixin):
    __tablename__ = 'target_account_followers'
    __table_args__ = {'schema': 'syncrementum'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    target_account_id = db.Column(db.Integer)
    follower_id = db.Column(db.Integer)
    username = db.Column(db.String)
    request_sent = db.Column(db.Boolean)
    followback = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    @classmethod
    def get_list(cls, uid, tid):
        return db.session.query(
            cls,
        ).select_from(cls
        ).filter(cls.user_id == uid
        ).filter(cls.target_account_id == tid
        ).order_by(cls.followbacks.desc()
        ).limit(randint(1,2)
        ).all()

    @classmethod
    def user_followers(cls, uid):
        return db.session.query(
            cls
        ).select_from(cls
        ).filter(cls.request_sent == True
        ).filter(cls.user_id == uid
        ).all()

    @classmethod
    def get_pending_list(cls, uid, tid):
        return db.session.query(
            cls.follower_id,
        ).select_from(cls
        ).filter(cls.user_id == uid
        ).filter(cls.target_account_id == tid
        ).filter(cls.request_sent == False
        ).order_by(cls.user_id.desc()
        ).limit(randint(1,2)
        ).all()

    @classmethod
    def get_target_follower(cls, uid,fid):
        return db.session.query(
            cls,
        ).select_from(cls
        ).filter(cls.user_id == uid
        ).filter(cls.follower_id == fid
        ).first()


class ProxyIp(db.Model, UserMixin):
    __tablename__ = 'proxy_ips'
    __table_args__ = {'schema': 'socialconversion'}
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String)
    port = db.Column(db.Integer)
    username = db.Column(db.String)
    password = db.Column(db.String)
    country = db.Column(db.String)

    @classmethod
    def count_proxies(cls):
        return db.session.query(
            func.count()
        ).select_from(cls
        ).all()

    @classmethod
    def get_proxy(cls, pid):
        return db.session.query(
            cls
        ).select_from(cls
        ).filter(cls.id == pid
        ).first()


class Subscription(db.Model, UserMixin):
    __tablename__ = 'subscriptions'
    __table_args__ = {'schema': 'syncrementum'}
    id = db.Column(db.Integer, primary_key=True)
    subscription_name = db.Column(db.String)
    subscription_price = db.Column(db.Numeric)
    subscription_id = db.Column(db.String)
    subscription_details = db.Column(db.String)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    status = db.Column(db.Boolean)

    @classmethod
    def by_planid(cls, pid):
        return db.session.query(
            cls
        ).select_from(cls
        ).filter(cls.subscription_id == pid
        ).first()

    @classmethod
    def get_all(cls, status=None):
        active_plans = ''
        if status is not None:
            active_plans = cls.status == True
        return db.session.query(
            cls
        ).select_from(cls
        ).filter(active_plans
        ).order_by(cls.id.desc()
        ).first()

    @classmethod
    def all_subscriptions(cls, status=None):
        active_plans = ''
        if status is not None:
            active_plans = cls.status == True
        return db.session.query(
            cls
        ).select_from(cls
        ).filter(active_plans
        ).all()


class Payment(db.Model, UserMixin):
    __tablename__ = 'payments'
    __table_args__ = {'schema': 'syncrementum'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    payment_detail_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    @classmethod
    def byuser_id(cls, uid):
        return db.session.query(
            cls,
            PaymentDetail,
            Subscription
        ).select_from(cls
        ).join(PaymentDetail, PaymentDetail.id == Payment.payment_detail_id
        ).join(Subscription, Subscription.id == PaymentDetail.subscription_id
        ).filter(cls.user_id == uid
        ).order_by(cls.id.desc()
        ).first()

    @classmethod
    def by_payment_detail_id(cls, pid):
        return db.session.query(
            cls
        ).select_from(cls
        ).filter(cls.payment_detail_id == pid
        ).first()


class PaymentDetail(db.Model, UserMixin):
    __tablename__ = 'payment_details'
    __table_args__ = {'schema': 'syncrementum'}
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric)
    subscription_id = db.Column(db.Integer)
    billing_aggrement_id = db.Column(db.String)
    payment_token = db.Column(db.String)
    payment_status = db.Column(db.String)
    payment_date = db.Column(db.DateTime)
    payment_mode = db.Column(db.String)

    @classmethod
    def byuser_id(cls, uid):
        return db.session.query(
            cls
        ).select_from(cls
        ).filter(cls.user_id == uid
        ).first()


class DirectMessage(db.Model, UserMixin):
    __tablename__ = 'direct_messages'
    __table_args__ = {'schema': 'syncrementum'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    message = db.Column(db.String)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    @classmethod
    def byuser_id(cls, uid):
        return db.session.query(
            cls
        ).select_from(cls
        ).filter(cls.user_id == uid
        ).first()


class Setting(db.Model, UserMixin):
    __tablename__ = 'settings'
    __table_args__ = {'schema': 'syncrementum'}
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    speed = db.Column(db.String)
    follow_limit = db.Column(db.String)
    follow_private_accounts = db.Column(db.String)
    has_profile_pictures = db.Column(db.String)
    only_bussiness_accounts = db.Column(db.String)
    min_post_limits = db.Column(db.String)
    max_post_limits = db.Column(db.String)
    min_following_limits = db.Column(db.String)
    max_following_limits = db.Column(db.String)
    min_follower_limits = db.Column(db.String)
    max_follower_limits = db.Column(db.String)
    unfollow_speed = db.Column(db.String)
    unfollow_limit = db.Column(db.String)
    unfollow_source = db.Column(db.String)
    engagement_speed = db.Column(db.String)
    engagement_source = db.Column(db.String)
    engagement_min_like_limits = db.Column(db.String)
    engagement_max_like_limits = db.Column(db.String)
    sleep_only_business_accounts = db.Column(db.String)
    sleep_start_time = db.Column(db.String)
    sleep_duration = db.Column(db.String)


    @classmethod
    def get_setting(cls, sid):
        return db.session.query(
            cls
        ).select_from(cls
        ).filter(cls.user_id == sid
        ).first()