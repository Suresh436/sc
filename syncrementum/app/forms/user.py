from flask_wtf import Form
from wtforms import (PasswordField, StringField, SelectField)
from wtforms.validators import (Email, DataRequired, EqualTo, Length)


class Login(Form):
    """User login form."""
    username = StringField(validators=[DataRequired(), Email()],
                           description='', render_kw={
            'onkeyup': 'this.setAttribute("value", this.value);'})
    password = PasswordField(validators=[DataRequired()],
                             description='', render_kw={
            'onkeyup': 'this.setAttribute("value", this.value);'})


class SignUp(Form):
    """User signup form."""
    first_name = StringField(validators=[DataRequired()],
                             description='First Name', label="First Name")
    last_name = StringField(validators=[DataRequired()],
                            description='')
    email = StringField(validators=[DataRequired(), Email()],
                        description='', render_kw={'onblur': 'validate_email()'})
    password = PasswordField(validators=[
        DataRequired(),
        EqualTo('confirm_password', message='Passwords must match.')
    ], description='')
    confirm_password = PasswordField(validators=[DataRequired()], description='')
    phone = StringField(validators=[DataRequired()],
                        description='')


class InstaLogin(Form):
    """User login form."""
    username = StringField(validators=[DataRequired()],
                           description='', render_kw={
            'onkeyup': 'this.setAttribute("value", this.value);'})
    password = PasswordField(validators=[DataRequired()],
                             description='', render_kw={
            'onkeyup': 'this.setAttribute("value", this.value);'})
    verification_code = StringField(validators=[DataRequired()],
                                    description='', render_kw={
            'onkeyup': 'this.setAttribute("value", this.value);'})


class forgotpassword(Form):
    """User forgot password form."""
    email = StringField(validators=[DataRequired(), Email()],
                        description='')


class resetpassword(Form):
    """User reset password form."""
    new_password = PasswordField(validators=[
        DataRequired(),
        EqualTo('confirm_new_password', message='Passwords must match.')
    ], description='')
    confirm_new_password = PasswordField(validators=[DataRequired()], description='')


class profile(Form):
    """User reset password form."""
    first_name = StringField(validators=[DataRequired()],
                             render_kw={'placeholder':'First Name', 'class':'form-control'})
    last_name = StringField(validators=[DataRequired()],
                            description='', render_kw={'placeholder':'Last Name', 'class':'form-control'})
    email = StringField(validators=[DataRequired(), Email()],
                        description='', render_kw={'placeholder':'Email', 'class':'form-control'})
    phone = StringField(validators=[DataRequired()],
                        description='', render_kw={'placeholder':'Phone', 'class':'form-control'})
    address1 = StringField(validators=[DataRequired()],
                           description='', render_kw={'placeholder':'Address1', 'class':'form-control'})
    address2 = StringField(description='', render_kw={'placeholder':'Address2', 'class':'form-control'})
    city = StringField(validators=[DataRequired()],
                       description='', render_kw={'placeholder':'City', 'class':'form-control'})
    state = SelectField(choices=[('0',"None")],render_kw={'class':'form-control'})
    zipcode = StringField(validators=[DataRequired(), Length(min=5, max=5)],
                          description='', render_kw={"onkeypress": "return IsNumeric(event);", 'placeholder':'Zipcode', 'class':'form-control'})
