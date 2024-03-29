import email
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import (
  IntegerField, 
  StringField, 
  SubmitField, 
  TextAreaField, 
  URLField, 
  EmailField,
  PasswordField,
  DateTimeField
  )
from wtforms.validators import InputRequired, NumberRange, Email, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed

class MovieForm(FlaskForm):
  title = StringField("Title", validators=[InputRequired()])
  director = StringField("Director")
  year = IntegerField("Year", validators=[NumberRange(1500,2022,"Input valid year please!")])
  submit = SubmitField("Add movie")

class StringListField(TextAreaField):
  def _value(self):
    if self.data:
      return "\n".join(self.data)
    else:
      return ""

  def process_formdata(self, valuelist):
    if valuelist and valuelist[0]:
      self.data = [line.strip() for line in valuelist[0].split("\n")]
    else:
      self.data = []

class ExtendedMovieForm(MovieForm):
  cast = StringListField("Cast")
  series = StringListField("Series")
  tags = StringListField("Tags")
  description = TextAreaField("Description")
  video_link = URLField("Movie URL")

  submit = SubmitField("Submit")


class RegisterForm(FlaskForm):
  email = EmailField("Email", validators=[InputRequired(),Email()]) 
  password = PasswordField("Password", validators=[
    InputRequired(),
    Length(min=4)
  ])
  confirm_password = PasswordField("Confirm password", validators=[
    InputRequired(),
    EqualTo("password")
  ])
  submit = SubmitField("Register")

class LoginForm(FlaskForm):
  email = EmailField("Email", validators=[InputRequired(),Email()]) 
  password = PasswordField("Password", validators=[
    InputRequired(),
    Length(min=4)
  ])
  submit = SubmitField("Login")

class UserForm(FlaskForm):
  name = StringField("Name")
  email = EmailField("Email", render_kw={'disabled': ''})
  dob = DateTimeField("Date of Birth (YYYY-MM-DD)", format='%Y-%m-%d')
  nationality = StringField("Nationality")
  movies_names = StringListField("Movies", render_kw={'disabled': ''})
  avatar_file = FileField("Profile photo", validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
  submit = SubmitField("Submit")

class PasswordForm(FlaskForm):
  old = PasswordField("Current Password", validators=[InputRequired()])
  new1 = PasswordField("New Password", validators=[
    InputRequired(),
    Length(min=4)
  ])
  new2 = PasswordField("Confirm New Password", validators=[
    InputRequired(),
    EqualTo("new1", message="New and Confirm New Password must be the same!")
  ])
  submit = SubmitField("Submit")