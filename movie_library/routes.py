from datetime import datetime
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
from movie_library.forms import LoginForm, MovieForm, ExtendedMovieForm, RegisterForm
from movie_library.models import Movie, User, login_required
from dataclasses import asdict
from passlib.hash import pbkdf2_sha256
import os 


pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)

@pages.route("/")
def index():
    user = list(current_app.db.User.find({"email": session.get("email")}))
    if len(user) > 0:
        movie_ids = list(current_app.db.User.find({"email": session.get("email")}))[0]["movies"]
    else:
        movie_ids = []
    list_movie = [Movie(**movie) for movie in current_app.db.Movie.find({"_id": {"$in" : movie_ids}})]
    return render_template(
        "index.html",
        title="Movies Watchlist",
        th_movie_data = list_movie
    )

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

        return redirect(url_for('pages.movie', _id = movie._id))

    return render_template("new_movie.html",
    title="Add movie",
    form = form)

@pages.route("/movie/<string:_id>")
@login_required
def movie(_id):
    current_movie = list(current_app.db.Movie.find({"_id": _id}))[0]
    movie = Movie(**current_movie)
    return render_template("movie_details.html", th_movie = movie)

@pages.route("/movie/<string:_id>/rating/<int:rating>")
@login_required
def rating(_id, rating):
    current_app.db.Movie.update_one({"_id": _id}, {"$set": {"rating": rating}})
    return redirect(url_for('pages.movie', _id = _id))

@pages.route("/movie/<string:_id>/watch_date/")
@login_required
def watch_date(_id):
    current_app.db.Movie.update_one({"_id": _id}, {"$set": {"last_watched": datetime.today().strftime("%b %d %Y")}})    
    return redirect(url_for('pages.movie', _id = _id))

@pages.route("/edit/<string:_id>/", methods = ["GET", "POST"])
@login_required
def edit_movie(_id):
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
                return redirect("/")
        flash("Wrong email or password!", "danger")
        return redirect("/login")
    return render_template('login.html', th_form = form, title="Log in")

@pages.route("/logout")
def logout():
    session['email'] = None
    return redirect("/")

@pages.route("/toggle-theme")
def toggle_theme():
    current_theme = session.get("theme")
    if current_theme == 'dark':
        current_theme = 'light'
    else:
        current_theme = 'dark'
    session['theme'] = current_theme

    return redirect(request.args.get("current_page"))