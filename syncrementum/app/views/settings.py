import json

from flask import (Blueprint, render_template, url_for, flash)
from flask import request
from flask_login import (login_required, current_user)
from sqlalchemy import func
from werkzeug.utils import redirect

from app import db
from app.forms import direct_message as direct_message_form
from app.logger_setup import errorlog
from app.models import Setting, DirectMessage
from app.tools.messages import SAVE_MESSAGE

settingsbp = Blueprint('settingsbp', __name__, url_prefix='/settings')


@settingsbp.route('/direct-message', methods=['GET', 'POST'])
def direct_message():
    """ Function to save direct message content for user in databse """
    try:
        get_uid = request.args.get('userid', default=None, type=int)
        uid = current_user.id
        if get_uid is not None:
            uid = get_uid
        get_message = DirectMessage.byuser_id(uid)
        dform = direct_message_form.direct_message(obj=get_message)
        if not dform.message.data:
            dform.message.data = "Hi {@username}, Thanks for your follow"
        if dform.validate_on_submit():
            if get_message:
                get_message.message = dform.message.data
                get_message.updated_at = func.now()
            else:
                message_obj = DirectMessage(
                    user_id=uid,
                    message=dform.message.data,
                    created_at=func.now(),
                    updated_at=func.now()
                )
                db.session.add(message_obj)
            db.session.commit()
            flash(SAVE_MESSAGE, 'success')
        return render_template('settings/direct_message.html', dform=dform)
    except Exception as err:
        errorlog.error('save direct message.', details=str(err))
        return str(err)

