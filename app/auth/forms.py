from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import Required,Email,EqualTo,Length
from ..models import User
from wtforms import ValidationError


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators = [Required(), Length(min = 3, max =20)])
    email = StringField('Email Address', validators = [Required(), Email()])
    password = PasswordField('Password', validators = [Required(),EqualTo('password_confirm', message = 'Passwords must match!')])
    password_confirm = PasswordField('Confirm Password', validators = [Required()])
    submit = SubmitField('Sign Up')

    def validate_email(self,data_field):
        if User.query.filter_by(email = data_field.data).first():
            raise ValidationError('An account with that email already exists')

    def validate_username(self,data_field):
        if User.query.filter_by(username = data_field.data).first():
            raise ValidationError('That username is already taken')



class LoginForm(FlaskForm):
    email = StringField('Your Email Address',validators=[Required(),Email()])
    password = PasswordField('Password',validators =[Required()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')
