from datetime import datetime, date
import uuid
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
from movie_library.forms import LoginForm, MovieForm, ExtendedMovieForm, PasswordForm, RegisterForm, UserForm
from movie_library.models import Movie, User, login_required
from dataclasses import asdict
from passlib.hash import pbkdf2_sha256
import os

from movie_library.modules import check_movie_belong_to_current_user, save_user_to_session 


pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)

## Homepage (show list movie)
@pages.route("/")
def index():
    user = session.get("current_user")
    if user != None:
        movie_ids = user['movies']
    else:
        movie_ids = []
    list_movie = [Movie(**movie) for movie in current_app.db.Movie.find({"_id": {"$in" : movie_ids}})]
    return render_template(
        "index.html",
        title="Movies Watchlist",
        th_movie_data = list_movie
    )

## Account (show and edit profile, password)
@pages.route("/profile", methods = ["GET", "POST"])
@login_required
def profile():
    current_user = session.get("current_user")
    _id = current_user['_id']
    form = UserForm(obj = User(**current_user))

    lst_movies = list(current_app.db.Movie.find({"_id":{"$in": current_user['movies']}}))
    lst_movie_names = [movie['title'] for movie in lst_movies]
    form.movies_names.data = lst_movie_names
    if form.validate_on_submit():
        user = dict(
            name = form.name.data,
            dob = form.dob.data,
            nationality = form.nationality.data,
        )
        current_app.db.User.update_one({"_id": _id}, {"$set": user})
        save_user_to_session()
        return redirect(url_for('pages.index'))

    return render_template("edit_user.html",
    title="My profile",
    form = form)

@pages.route("/change_password", methods = ["GET", "POST"])
@login_required
def change_password():
    current_user = session.get("current_user")
    _id = current_user['_id']
    form = PasswordForm()

    if form.validate_on_submit():
        form_data = {
            'old': form.old.data,
            'new1': form.new1.data,
            'new2': form.new2.data
        }
        if pbkdf2_sha256.verify(form_data['old'], current_user['password']):
            current_app.db.User.update_one({"_id": _id}, {"$set": {"password": pbkdf2_sha256.hash(form_data['new1'])}})
            save_user_to_session()
            flash("Password changed.", "success")
            return redirect(url_for('pages.index'))
        else:
            flash("Wrong current password. Try again!", "danger")
            return redirect(url_for('pages.change_password'))

    return render_template("edit_password.html",
    title="Change password",
    form = form)

## Add movie
@pages.route("/add", methods = ["GET", "POST"])
@login_required
def add_movie():
    form = MovieForm()
    if form.validate_on_submit():
        movie = Movie(
            _id = uuid.uuid4().hex,
            title = form.title.data,
            director = form.director.data,
            year = form.year.data
        )
        current_app.db.Movie.insert_one(asdict(movie))
        current_app.db.User.update_one({"email": session.get("email")}, {"$push": {"movies": movie._id}})
        save_user_to_session()
        return redirect(url_for('pages.movie', _id = movie._id))

    return render_template("new_movie.html",
    title="Add movie",
    form = form)

## Show movie, edit movie information
@pages.route("/movie/<string:_id>")
@login_required
def movie(_id):
    check = check_movie_belong_to_current_user(_id)
    current_movie = list(current_app.db.Movie.find({"_id": _id}))[0]
    movie = Movie(**current_movie)
    return render_template("movie_details.html", th_movie = movie, th_check = check)

@pages.route("/movie/<string:_id>/rating/<int:rating>")
@login_required
def rating(_id, rating):
    check = check_movie_belong_to_current_user(_id)
    if not check:
        return redirect(url_for('pages.movie', _id = _id))
    current_app.db.Movie.update_one({"_id": _id}, {"$set": {"rating": rating}})
    return redirect(url_for('pages.movie', _id = _id))

@pages.route("/movie/<string:_id>/watch_date/")
@login_required
def watch_date(_id):
    check = check_movie_belong_to_current_user(_id)
    if not check:
        return redirect(url_for('pages.movie', _id = _id))
    current_app.db.Movie.update_one({"_id": _id}, {"$set": {"last_watched": datetime.today().strftime("%b %d %Y")}})    
    return redirect(url_for('pages.movie', _id = _id))

@pages.route("/edit/<string:_id>/", methods = ["GET", "POST"])
@login_required
def edit_movie(_id):
    check = check_movie_belong_to_current_user(_id)
    if not check:
        return redirect(url_for('pages.movie', _id = _id))

    current_movie = list(current_app.db.Movie.find({"_id": _id}))[0]
    movie = Movie(**current_movie)
    form = ExtendedMovieForm(obj = movie)

    if form.validate_on_submit():
        movie = dict(
            title = form.title.data,
            director = form.director.data,
            year = form.year.data,
            cast = form.cast.data,
            series = form.series.data,
            tags = form.tags.data,
            description = form.description.data,
            video_link = form.video_link.data,
        )

        current_app.db.Movie.update_one({"_id": _id}, {"$set": movie})
        return redirect(url_for('pages.movie', _id = _id))

    return render_template("edit_movie.html",
    title=movie.title,
    th_movie = movie,
    form = form)

## Register and Login/Logout account
@pages.route("/register", methods = ['GET','POST'])
def register():
    if session.get("email"):
        return redirect("/")
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            _id = uuid.uuid4().hex,
            email = form.email.data,
            password = pbkdf2_sha256.hash(form.password.data)
        )
        lst_email = [u['email'] for u in list(current_app.db.User.find({}, {"email": 1}))]
        if user.email in lst_email:
            flash("This email had been registerd already. Use another email!", "danger")
            return redirect("/register")
        current_app.db.User.insert_one(asdict(user))
        flash("Registered Successfully!", "success")
        return redirect("/login")
    return render_template('register.html', th_form = form, title="Register")

@pages.route("/login", methods = ['GET','POST'])
def login():
    if session.get("email"):
        if session.get("url_bf_login") != None:
            url = session.get("url_bf_login")
            session["url_bf_login"] = None
            return redirect(url)
        return redirect("/")

    form = LoginForm()
    if form.validate_on_submit():
        login_dic = {
            'email' : form.email.data,
            'password': form.password.data
        }
        user = list(current_app.db.User.find({"email": login_dic['email']}))
        if len(user) > 0:
            if pbkdf2_sha256.verify(login_dic['password'], user[0]['password']):
                session['email'] = login_dic['email']
                save_user_to_session()
                return redirect(request.path)
        flash("Wrong email or password!", "danger")
    return render_template('login.html', th_form = form, title="Log in")

@pages.route("/logout")
def logout():
    session['email'] = None
    session['current_user'] = None
    return redirect("/")

# Switch light/dark mode
@pages.route("/toggle-theme")
def toggle_theme():
    current_theme = session.get("theme")
    if current_theme == 'dark':
        current_theme = 'light'
    else:
        current_theme = 'dark'
    session['theme'] = current_theme

    return redirect(request.args.get("current_page"))