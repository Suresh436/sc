import json
from decimal import Decimal

from datetime import datetime, timedelta
import paypalrestsdk
from flask import (Blueprint, render_template, url_for,
                   flash, request, session)
from flask_login import (login_user, login_required, current_user)
from paypalrestsdk import BillingPlan, BillingAgreement
from sqlalchemy import func
from werkzeug.utils import redirect

from app import db
from app.config import PAYPAL_MODE, PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET
from app.forms import payment as payment_form
from app.logger_setup import errorlog
from app.models import Subscription, PaymentDetail, Payment, User
from app.tools.messages import *

paymentbp = Blueprint('paymentbp', __name__, url_prefix='/payment')


@paymentbp.route('/create-plan', methods=['GET', 'POST'])
@login_required
def subscriptions_create():
    """ Function to create new subscription plan """
    try:
        if current_user.user_type != 'admin':
            flash('You are not allowed to access this page','danger')
            return redirect(url_for('userbp.dashboard'))
        configure_paypal()
        form = payment_form.create_plan()
        if form.validate_on_submit():
            billing_plan_attributes = {
                "name": request.form['name'],
                "description": request.form['description'],
                "merchant_preferences": {
                    "auto_bill_amount": "yes",
                    "cancel_url": url_for('paymentbp.cancel', _external=True),
                    "initial_fail_amount_action": "continue",
                    "max_fail_attempts": "1",
                    "return_url": url_for('paymentbp.execute', _external=True),
                    "setup_fee": {
                        "currency": 'USD',
                        "value": request.form['setup_fee']
                    }
                },
                "payment_definitions": [
                    {
                        "amount": {
                            "currency": 'USD',
                            "value": request.form['amount']
                        },
                        "cycles": "0",
                        "frequency": request.form['frequency'],
                        "frequency_interval": "1",
                        "name": request.form['payment_definition_name'],
                        "type": 'Regular'
                    }
                ],
                "type": 'INFINITE'
            }
            billing_plan = BillingPlan(billing_plan_attributes)
            if billing_plan.create():
                subs = Subscription(
                    subscription_name=request.form['name'],
                    subscription_price=Decimal(request.form['amount']),
                    subscription_id=billing_plan.id,
                    subscription_details=request.form['description'],
                    created_at=func.now(),
                    updated_at=func.now(),
                    status=False
                )
                db.session.add(subs)
                db.session.commit()
                flash('Plan is Created', 'success')
                return redirect(url_for('paymentbp.subscriptions'))
            else:
                flash('Plan could not Created', 'danger')
                errorlog.error('Subscription Create Error',
                               details=str(billing_plan.error))
        return render_template('payment/create_plan.html', cform=form)
    except Exception as err:
        errorlog.error('Subscription Create Error', details=str(err))
        return render_template('error.html', message="Error!")


@paymentbp.route('/activate-plan', methods=['GET', 'POST'])
@login_required
def activate_plan():
    """ Function to activate plan """
    try:
        if current_user.user_type != 'admin':
            flash('You are not allowed to access this page','danger')
            return redirect(url_for('userbp.dashboard'))
        configure_paypal()
        pid = request.args.get('id', '')
        billing_plan = BillingPlan.find(pid)
        if billing_plan.activate():
            subplan = Subscription.by_planid(pid)
            subplan.status = True
            db.session.commit()
        else:
            errorlog.error('Plan activate Error', details=str(billing_plan.error))
        return redirect(url_for('paymentbp.subscriptions'))
    except Exception as err:
        errorlog.error('Plan activate Error', details=str(err))
        return render_template('error.html', message="Error!")


@paymentbp.route('/subscriptions', methods=['GET', 'POST'])
@login_required
def subscriptions():
    """ Function to get all subscriptions """
    try:
        if current_user.user_type != 'admin':
            flash('You are not allowed to access this page','danger')
            return redirect(url_for('userbp.dashboard'))
        plans = Subscription.all_subscriptions()
        if plans:
            all_plans = plans
        else:
            all_plans = []
        return render_template('payment/subscriptions.html', plans=all_plans)
    except Exception as err:
        errorlog.error('Subscription list Error', details=str(err))
        return render_template('error.html', message="Error!")


@paymentbp.route('/billing', methods=['GET', 'POST'])
@login_required
def billing():
    """ Function to integrate the billing page """
    try:
        plan = Subscription.get_all(True)
        get_uid = request.args.get('userid', default=None, type=int)
        paypalaction = url_for('paymentbp.subscribe_paypal',
                               payment_id=plan.subscription_id)
        if get_uid is not None:
            if current_user.user_type == 'admin':
                uid = get_uid
                usr_detail = User.by_id(uid)
                paypalaction = url_for('paymentbp.subscribe_paypal',
                                       payment_id=plan.subscription_id,
                                       userid=get_uid)
                if usr_detail.payment_status:
                    flash(ALREADY_SUBSCRIBED, 'danger')
                    return redirect(url_for('userbp.dashboard'))
            else:
                if current_user.payment_status:
                    flash(ALREADY_SUBSCRIBED, 'danger')
                    return redirect(url_for('userbp.dashboard'))
        else:
            if current_user.payment_status:
                flash(ALREADY_SUBSCRIBED, 'danger')
                return redirect(url_for('userbp.dashboard'))
        credit_card_form = payment_form.credit_card()

        credit_card_form.payment_token.data = plan.subscription_id
        if credit_card_form.validate_on_submit():
            res = subscribe(credit_card_form.payment_token.data, credit_card_form)
            if res is True:
                flash(PLAN_SUBSCRIBED, 'success')
                return redirect(url_for('userbp.dashboard'))
        return render_template('payment/billing.html', action='billing',
                               paypalaction=paypalaction, plan=plan,
                               ccform=credit_card_form)
    except Exception as err:
        errorlog.error('Billing Error', details=str(err))
        return render_template('error.html', message="Error!")


@paymentbp.route('/subscribe-paypal/<payment_id>', methods=['GET', 'POST'])
@login_required
def subscribe_paypal(payment_id):
    """ Function to redirect user to paypal site for customer agreement """
    try:
        get_uid = request.args.get('userid', default=None, type=int)
        configure_paypal()
        approval_url = subscribe(payment_id, get_uid)
        if approval_url:
            return redirect(approval_url)
        else:
            flash(PAYPAL_REDIRECT_ERROR, 'danger')
            return redirect(url_for('paymentbp.billing'))
    except Exception as err:
        errorlog.error('Subscribe Error', details=str(err))
        return render_template('error.html', message="Error!")


def save_credit_card_response(billing_agreement_response, payment_id):
    """ Function to save credit card response """
    try:
        payment_token = payment_id
        plans = Subscription.get_all()
        if 'id' in billing_agreement_response:
            pdobj = PaymentDetail(
                amount=plans.subscription_price,
                subscription_id=plans.id,
                payment_status='Success',
                payment_date=func.now(),
                billing_aggrement_id=billing_agreement_response.id,
                payment_token=payment_token,
                payment_mode='credit_card'
            )
            db.session.add(pdobj)
            db.session.commit()

            pobj = Payment(
                user_id=current_user.id,
                payment_detail_id=pdobj.id,
                created_at=func.now(),
                updated_at=func.now()
            )
            db.session.add(pobj)

            current_user.payment_status = True
            db.session.commit()
            return True

    except Exception as err:
        errorlog.error('Credit Card response Error', details=str(err))
        return render_template('error.html', message="Error!")


def subscribe(payment_id, user_id=None, ccform=None):
    """ Function to create billing agreement using credit card and paypal """
    try:
        configure_paypal()
        user_detail = current_user
        if user_id is not None:
            user_detail = User.by_id(user_id)
            session['app_user_id'] = user_id

        if ccform is not None:
            exp_detail = ccform.expiry_date.data.split('/')
            exp_month = exp_detail[0] if exp_detail[0] else 0
            exp_year = exp_detail[1] if exp_detail[1] else 0
            payer_info = {"payer": {
                "payment_method": "credit_card",
                "funding_instruments": [{
                    "credit_card": {
                        "type": str(ccform.type.data),
                        "number": str(ccform.card_number.data),
                        "expire_month": str(exp_month),
                        "expire_year": str(exp_year),
                        "cvv2": str(ccform.cvv.data),
                        "first_name": str(ccform.first_name.data),
                        "last_name": str(ccform.last_name.data),
                        "billing_address": {
                            "line1": str(current_user.address1),
                            "line2": str(current_user.address2),
                            "city": str(current_user.city),
                            "state": str(current_user.state),
                            "postal_code": str(current_user.zipcode),
                            "country_code": "US"
                        }

                    },

                }]

            }}
        else:
            payer_info = {"payer": {
                "payment_method": "paypal",
                "funding_option_id": user_detail.id,
                "payer_info": {
                    "email": user_detail.email,
                    "first_name": user_detail.first_name,
                    "last_name": user_detail.last_name,

                }
            }}
        plan = Subscription.by_planid(payment_id)
        billing_agreement = BillingAgreement({
            "name": plan.subscription_name,
            "description": "Agreement for the recurring payment for the plan "
                           + plan.subscription_name
                           + ". The cost of this plan is $"
                           + str('%.2f' % plan.subscription_price)+" /month.",
            "start_date": (datetime.now() +
                           timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "plan": {
                "id": str(payment_id)
            },

            "payer": payer_info['payer'],
        })
        if billing_agreement.create():
            if ccform is not None:
                billing_agreement_response = BillingAgreement.execute(billing_agreement.id)
                return save_credit_card_response(billing_agreement, payment_id)
            for link in billing_agreement.links:

                if link.rel == "approval_url":
                    approval_url = link.href
                    return approval_url
            return False
        else:
            errorlog.error('Subscribe Error', details=str(billing_agreement.error))
            flash(SUBSCRIPTION_ERROR, 'danger')
        return False

    except Exception as err:
        errorlog.error('Subscribe Error', details=str(err))
        flash(SUBSCRIPTION_ERROR, 'danger')
        return redirect(url_for('paymentbp.billing'))


@paymentbp.route('/execute', methods=['GET', 'POST'])
@login_required
def execute():
    """ Function to execute plan after redirecting from paypal site after
    customer agreement """
    try:
        configure_paypal()
        payment_token = request.args.get('token', '')
        billing_agreement_response = BillingAgreement.execute(payment_token)
        plans = Subscription.get_all()
        action = url_for('userbp.dashboard')
        billing_action = url_for('paymentbp.billing')
        if 'id' in billing_agreement_response:
            pdobj = PaymentDetail(
                amount=plans.subscription_price,
                subscription_id=plans.id,
                payment_status='Success',
                payment_date=func.now(),
                billing_aggrement_id=billing_agreement_response.id,
                payment_token=payment_token,
                payment_mode='paypal'
            )
            db.session.add(pdobj)
            db.session.commit()
            user_id = current_user.id

            if 'app_user_id' in session:
                user_id = session['app_user_id']
                session.pop('app_user_id')
                action = url_for('userbp.dashboard', userid=user_id)
                billing_action = url_for('paymentbp.billing', userid=user_id)
            pobj = Payment(
                user_id=user_id,
                payment_detail_id=pdobj.id,
                created_at=func.now(),
                updated_at=func.now()
            )
            db.session.add(pobj)
            get_user = User.by_id(int(user_id))
            get_user.payment_status = True
            db.session.commit()
            flash(PLAN_EXECUTED, 'success')
            return redirect(action)
        else:
            flash(PLAN_EXECUTED_ERROR, 'danger')
            return redirect(billing_action)
    except Exception as err:
        errorlog.error('Subscribe Error', details=str(err))
        return render_template('error.html', message="Error!")


@paymentbp.route('/cancel', methods=['GET', 'POST'])
def cancel():
    """ Function to to redirect billing page after cancelling paypal payment
    by user on paypal site """
    flash(PAYPAL_CANCEL_SUBSCRIPTION, 'danger')
    return redirect(url_for('paymentbp.billing'))


def configure_paypal():
    """ Function to configure the paypal client id and secret """
    try:
        paypalrestsdk.configure({
            "mode": PAYPAL_MODE,  # sandbox or live
            "client_id": PAYPAL_CLIENT_ID,
            "client_secret": PAYPAL_CLIENT_SECRET
        })

    except Exception as err:
        errorlog.error('Configure Error', details=str(err))


@paymentbp.route("/my-account")
def my_account():
    """ Function to view my account having info abount subscription and payment history """
    try:
        get_uid = request.args.get('userid', default=None, type=int)
        uid = current_user.id
        if get_uid is not None and current_user.user_type == 'admin':
            uid = get_uid
        userinfo = User.by_id(uid)
        trans_list = None
        billing_agreement = None
        account_detail = None
        if userinfo.payment_status == 1:
            account_detail = Payment.byuser_id(userinfo.id)
            get_date = datetime.strptime(
                str(userinfo.created_at), '%Y-%m-%d %H:%M:%S'
            ) - timedelta(days=1)
            start_date, end_date = get_date.strftime('%Y-%m-%d'), \
                                   datetime.now().strftime("%Y-%m-%d")
            account_detail = Payment.byuser_id(userinfo.id)
            configure_paypal()
            billing_agreement = BillingAgreement.find(
                account_detail.PaymentDetail.billing_aggrement_id
            )
            transactions = billing_agreement.search_transactions(start_date, end_date)
            trans_list = transactions.agreement_transaction_list
        if trans_list is None:
            trans_list = []
        credit_card_form = payment_form.credit_card()
        plan = Subscription.get_all(True)
        credit_card_form.payment_token.data = plan.subscription_id
        return render_template('payment/my_account.html',
                               account_detail=account_detail,
                               transactions=trans_list,
                               agreement=billing_agreement,
                               userinfo=userinfo,
                               plan=plan, ccform=credit_card_form)
    except Exception as err:
        errorlog.error('My Account Error', details=str(err))
        return render_template('error.html', message="Error!")


@paymentbp.route("/cancel-current-plan")
def cancel_current_plan():
    """ Function to cancel the current plan """
    try:
        get_uid = request.args.get('userid', default=None, type=int)
        uid = current_user.id
        profile_redirect = url_for('userbp.profile')
        dashboard_redirect = url_for('userbp.dashboard')
        if get_uid is not None and current_user.user_type == 'admin':
            uid = get_uid
            profile_redirect = url_for('userbp.profile', userid=uid)
            dashboard_redirect = url_for('userbp.dashboard', userid=uid)
        userinfo = User.by_id(uid)
        if userinfo.payment_status != 1:
            flash(PLAN_SUBSCRIPTION_ERROR, 'danger')
            return redirect(profile_redirect)
        configure_paypal()
        pay_info = Payment.byuser_id(uid)
        billing_agreement_detail = BillingAgreement.find(
            pay_info.PaymentDetail.billing_aggrement_id
        )
        cancel_note = {"note": "Canceling the agreement"}
        cancel_states = ['Active', 'Suspended']
        if billing_agreement_detail.state in cancel_states:
            if billing_agreement_detail.cancel(cancel_note):
                userinfo.payment_status = 0
                db.session.commit()
                flash(CANCEL_PLAN, 'success')
                return redirect(dashboard_redirect)

            else:
                errorlog.error('Cancel Current Plan Error',
                               details=str(billing_agreement_detail.error))
                flash(CANCEL_PLAN_ERROR, 'danger')
        else:
            flash(PLAN_NOT_ACTIVE, 'danger')

    except Exception as err:
        errorlog.error('Cancel Current Plan Error', details=str(err))
        flash(CANCEL_PLAN_ERROR, 'danger')

    return redirect(profile_redirect)


@paymentbp.route('/free_subscription/<uid>', methods=['GET', 'POST'])
def free_subscription(uid):
    """ Function to make free sunscription for user"""
    user_detail = User.by_id(uid)
    dash_redirect = url_for('userbp.dashboard')
    if int(uid) != int(current_user.id):
        dash_redirect = url_for('userbp.customers')
    if user_detail.payment_status == 1:
        configure_paypal()
        pay_info = Payment.byuser_id(uid)
        billing_agreement_detail = BillingAgreement.find(
            pay_info.PaymentDetail.billing_aggrement_id
        )
        cancel_note = {"note": "Canceling the agreement"}
        cancel_states = ['Active', 'Suspended']
        if billing_agreement_detail.state in cancel_states:
            if billing_agreement_detail.cancel(cancel_note):
                user_detail.payment_status = 2
                flash(MAKE_FREE_USER, 'success')
                flash(CANCEL_PLAN, 'success')

            else:
                errorlog.error('Cancel Current Plan Error',
                               details=str(billing_agreement_detail.error))
                flash(CANCEL_PLAN_ERROR, 'danger')
        else:
            errorlog.error('Cancel Current Plan Error',
                           details=str(billing_agreement_detail.error))
            flash(PLAN_NOT_ACTIVE, 'danger')
    else:
        user_detail.payment_status = 2
        flash(MAKE_FREE_USER, 'success')
    db.session.commit()

    return redirect(dash_redirect)
