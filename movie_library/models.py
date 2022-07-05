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


class Data:
  def __init__(self, path):
    self.path = path
  
  def open(self):
    self.f = open(self.path, 'r', encoding='utf-8')
    self.nd = json.load(self.f)
    self.f.close()
  
  def append(self, dic):
    self.nd.append(dic)

  def delete(self, blog_id):
    delete_blog = None
    for blog in self.nd:
      if blog['_id'] == blog_id:
        delete_blog = blog
        break
    
    self.nd.remove(delete_blog)
  
  def commit(self):
    self.f = open(self.path, 'w', encoding='utf-8')
    json.dump(self.nd, self.f)
    self.f.close()

movies_path = os.path.dirname(os.path.realpath(__file__)) + '/static/data/movies.json'
users_path = os.path.dirname(os.path.realpath(__file__)) + '/static/data/users.json'
movie_data = Data(movies_path)
user_data = Data(users_path)

def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        _email = session.get("email")
        user_data.open()
        lst_email = [user['email'] for user in user_data.nd]
        print(_email)
        print(lst_email)
        if _email not in lst_email:
            return redirect("/login")
        return route(*args, **kwargs)
    return route_wrapper