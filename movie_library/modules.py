from flask import current_app, session
from movie_library.models import User



def save_user_to_session():
  session['current_user'] = list(current_app.db.User.find({"email": session.get("email")}))[0]