from flask_wtf import Form
from wtforms import (PasswordField, StringField, SelectField, HiddenField)
from wtforms.validators import (Email, DataRequired, EqualTo, Length)


class create_plan(Form):
    """Create Plan Form."""
    name = StringField(validators=[DataRequired()],
                           description='')
    description = StringField(validators=[DataRequired()],
                             description='')
    payment_definition_name = StringField(validators=[DataRequired()],
                              description='')
    frequency = SelectField(choices=[('MONTH',"MONTH"),
                                        ('WEEK','WEEK'),
                                        ('DAY','DAY'),
                                        ('YEAR','YEAR'),
                                        ])
    amount = StringField(validators=[DataRequired()],
                              description='')
    setup_fee = StringField(validators=[DataRequired()],
                               description='')
    # tax = StringField(validators=[DataRequired()],
    #                           description='')
    # shipping = StringField(validators=[DataRequired()],
    #                           description='')


class credit_card(Form):
    """Credit Card Form."""
    card_number = StringField(validators=[DataRequired()],
                           description='', render_kw={'placeholder':'Card Number', 'class':'form-control'})
    expiry_date = StringField(validators=[DataRequired()],
                             description='', render_kw={'placeholder':'mm/yyyy', 'class':'form-control'})
    cvv = StringField(validators=[DataRequired()],
                              description='', render_kw={'placeholder':'CVV', 'class':'form-control'})
    type = SelectField(choices=[('visa',"VISA"),
                                        ('mastercard','Mastercard'),
                                        ('amex','American Express'),
                                        ('discover','Discover'),
                                        ('jcb','JCB'),
                                        ],render_kw={'class':'form-control'})
    first_name = StringField(validators=[DataRequired()],
                              description='', render_kw={'placeholder':'First Name', 'class':'form-control'})
    last_name = StringField(validators=[DataRequired()],
                              description='', render_kw={'placeholder':'Last Name', 'class':'form-control'})
    payment_token = HiddenField(validators=[DataRequired()],
                            description='')


