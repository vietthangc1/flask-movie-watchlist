from flask import current_app, session
from movie_library.models import User


def save_user_to_session():
  session['current_user'] = list(current_app.db.User.find({"email": session.get("email")}))[0]

def check_movie_belong_to_current_user(id):
  check = False
  if id in session.get('current_user').get("movies"):
    check = True
  return check