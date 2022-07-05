from flask_wtf import FlaskForm
from wtforms import (
  IntegerField, 
  StringField, 
  SubmitField, 
  TextAreaField, 
  URLField, 
  EmailField,
  PasswordField)
from wtforms.validators import InputRequired, NumberRange, Email, EqualTo, Length

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