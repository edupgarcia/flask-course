from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Email,ValidationError

from application.models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=15)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(),  Length(min=6, max=15)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(),Length(min=6, max=15), EqualTo('password')])
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=55)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=55)])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user:
            raise ValidationError('Email is already in use. Pick another one.')
