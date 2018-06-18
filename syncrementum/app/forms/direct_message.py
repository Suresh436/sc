from flask_wtf import Form
from wtforms import (StringField, TextAreaField)
from wtforms.validators import (DataRequired)


class direct_message(Form):
    """Direct Message Form."""
    message = TextAreaField(validators=[DataRequired()],
                           description='', render_kw={'class': 'direct-message-width'})


