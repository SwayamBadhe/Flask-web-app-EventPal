from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
from event_name.models import User

# User registration
class RegistrationForm_User(FlaskForm):
    is_organizer = StringField('Role', validators=[DataRequired()], default='user')
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

# User login
class LoginForm_User(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm_User(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
            
class EventForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    picture = FileField('Image', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    date_of_event = StringField('Date of Event', validators=[DataRequired()])
    submit = SubmitField('Create Event')

class SearchBarForm(FlaskForm):
    content = StringField()
    submit = SubmitField('Search')

# class UpdateAccountForm_Organizer(FlaskForm):
#     org_name = StringField('Organization name', validators=[DataRequired(), Length(min=2, max=20)])
#     org_email = StringField('Organization Email',  validators=[DataRequired(), Email()])
#     address = StringField('Address',  validators=[DataRequired()])
#     city = StringField('City', validators=[DataRequired()])
#     state = StringField('State', validators=[DataRequired()])
#     zip = StringField('Zip', validators=[DataRequired()])
#     picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
#     submit = SubmitField('Update')

#     def validate_org_name(self, org_name):
#         if org_name.data != current_user.org_name:
#             organizer = Organizer.query.filter_by(org_name=org_name.data).first()
#             if organizer:
#                 raise ValidationError('That organization name is taken. Please choose a different one.')

#     def validate_org_email(self, org_email):
#         if org_email.data != current_user.org_email:
#             organizer = Organizer.query.filter_by(org_email=org_email.data).first()
#             if organizer:
#                 raise ValidationError('That email is taken. Please choose a different one.')

    
# Organizer registration
# class RegistrationForm_Organizer(FlaskForm):
#     org_name = StringField('Organization name', validators=[DataRequired(), Length(min=2, max=20)])
#     org_email = StringField('Organization Email', validators=[DataRequired(), Email()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
#     address = StringField('Address',  validators=[DataRequired()])
#     city = StringField('City', validators=[DataRequired()])
#     state = StringField('State', validators=[DataRequired()])
#     zip = StringField('Zip', validators=[DataRequired()])
#     submit = SubmitField('Sign Up')

#     def validate_org_name(self, org_name):
#         organizer = Organizer.query.filter_by(org_name=org_name.data).first()
#         if organizer:
#             raise ValidationError('That organization name is taken. Please choose a different one.')

#     def validate_org_email(self, org_email):
#         organizer = Organizer.query.filter_by(org_email=org_email.data).first()
#         if organizer:
#             raise ValidationError('That email is taken. Please choose a different one.')

# # Form for selecting the state 
# class StateForm(FlaskForm):
#     state = SelectField('State', choices=[
#         ('', 'Choose...'),
#         ('Andhra Pradesh', 'Andhra Pradesh'),
#         ('Arunachal Pradesh', 'Arunachal Pradesh'),
#         ('Assam', 'Assam'),
#         ('Bihar', 'Bihar'),
#         ('Chhattisgarh', 'Chhattisgarh'),
#         ('Goa', 'Goa'),
#         ('Gujarat', 'Gujarat'),
#         ('Haryana', 'Haryana'),
#         ('Himachal Pradesh', 'Himachal Pradesh'),
#         ('Jharkhand', 'Jharkhand'),
#         ('Karnataka', 'Karnataka'),
#         ('Kerala', 'Kerala'),
#         ('Madhya Pradesh', 'Madhya Pradesh'),
#         ('Maharashtra', 'Maharashtra'),
#         ('Manipur', 'Manipur'),
#         ('Meghalaya', 'Meghalaya'),
#         ('Mizoram', 'Mizoram'),
#         ('Nagaland', 'Nagaland'),
#         ('Odisha', 'Odisha'),
#         ('Punjab', 'Punjab'),
#         ('Rajasthan', 'Rajasthan'),
#         ('Sikkim', 'Sikkim'),
#         ('Tamil Nadu', 'Tamil Nadu'),
#         ('Telangana', 'Telangana'),
#         ('Tripura', 'Tripura'),
#         ('Uttar Pradesh', 'Uttar Pradesh'),
#         ('Uttarakhand', 'Uttarakhand'),
#         ('West Bengal', 'West Bengal')
#     ])

# # Organizer login
# class LoginForm_Organizer(FlaskForm):
#     org_email = StringField('Email', validators=[DataRequired(), Email()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     remember = BooleanField('Remember Me')
#     submit = SubmitField('Login')