from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField, SelectMultipleField, SelectField, IntegerRangeField, RadioField, TimeField
from wtforms.validators import DataRequired, NumberRange
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User, Location, Space, meetingHistory, upcomingMeeting, reviews, Tech, TechToSpace


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    fullName = StringField('Full name', validators=[DataRequired()])
    guest = RadioField('Looking to search or post meeting spaces?',
                       coerce=bool,
                       validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class HomeSearch(FlaskForm):
    zipcode = StringField('Zipcode', validators=[DataRequired()])
    date = DateField('Date', format='%Y-%m-%d')
    time = StringField('Time', validators=[DataRequired()])
    price = RadioField('Price', choices=[(0, 'Free'), (1, '$$$')], validators=[DataRequired()])
    submit = SubmitField('Search')

    def validate_zipcode(self, zipcode):
        if len(zipcode) != 5:
            raise ValidationError("Please enter a 5 digit zipcode.")


class FullSearch(FlaskForm):
    zipcode = StringField('Zipcode', validators=[DataRequired(), Length(5,5,"Please enter a 5 digit zipcode")])
    date = DateField('Date', format='%Y-%m-%d')
    #time = TimeField('Time', validators=[DataRequired()])
    price = RadioField('Paid or free space?', validators=[DataRequired()])
    tech = SelectMultipleField('Technology', coerce=int, choices=[])
    groupSize = IntegerRangeField('Group Size', [NumberRange(min=1, max=100)])
    submit = SubmitField('Search')


class Booking(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d')
    space = SelectField('Space', validators=[DataRequired()])
    #time = TimeField('Time', validators=[DataRequired()])
    tech = SelectMultipleField('Technology', coerce=int, choices=[])
    groupSize = IntegerRangeField('Group Size', [NumberRange(min=1, max=100)])
    submit = SubmitField('Book')
