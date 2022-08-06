from dataclasses import dataclass, field
from datetime import datetime
import json, os
from random import choice
from typing import List
from flask import (
    Blueprint,
    flash, 
    redirect, 
    render_template, 
    url_for, 
    request, 
    session, 
    current_app,
    )
import functools
from flask import (
  current_app
)

@dataclass
class Movie:
  _id: str
  title: str
  director: str
  year: int
  cast: List[str] = field(default_factory=list)
  series: List[str] = field(default_factory=list)
  last_watched: datetime = None
  rating: int = 0
  tags: List[str] = field(default_factory=list)
  description: str = None
  video_link: str = None

@dataclass
class User:
  _id: str
  email: str
  password: str
  movies: List[str] = field(default_factory=list)

def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        _email = session.get("email")
        lst_user = list(current_app.db.User.find({}))
        lst_email = [user['email'] for user in lst_user]
        print(_email)
        print(lst_email)
        if _email not in lst_email:
            return redirect("/login")
        return route(*args, **kwargs)
    return route_wrapper