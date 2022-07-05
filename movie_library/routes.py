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
from movie_library.models import Data, Movie, User, login_required, movie_data, user_data
from dataclasses import asdict
from passlib.hash import pbkdf2_sha256
import os 


pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)

@pages.route("/")
def index():
    movie_data.open()
    user_data.open()
    movie_ids = []
    for user in user_data.nd:
        if user['email'] == session.get('email'):
            movie_ids = user['movies']
            break
    list_movie = [Movie(**movie) for movie in movie_data.nd if movie['_id'] in movie_ids]
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

        movie_data.open()
        movie_data.append(asdict(movie))
        movie_data.commit()

        user_data.open()
        lst_user = user_data.nd
        for i in range(len(lst_user)):
            if lst_user[i]['email'] == session.get('email'):
                current_user = lst_user[i]
                break
        current_user['movies'].append(movie._id)

        del lst_user[i]
        lst_user.append(current_user)
        user_data.nd = lst_user
        user_data.commit()


        return redirect(url_for('pages.movie', _id = movie._id))

    return render_template("new_movie.html",
    title="Add movie",
    form = form)

@pages.route("/movie/<string:_id>")
@login_required
def movie(_id):
    movie_data.open()
    list_movie = [movie for movie in movie_data.nd]
    current_movie = None
    for m in list_movie:
        if m['_id'] == _id:
            current_movie = m
            break
    movie = Movie(**current_movie)
    return render_template("movie_details.html", th_movie = movie)

@pages.route("/movie/<string:_id>/rating/<int:rating>")
@login_required
def rating(_id, rating):
    movie_data.open()
    list_movie = [movie for movie in movie_data.nd]
    current_movie = None
    for i in range(len(list_movie)):
        if list_movie[i]['_id'] == _id:
            current_movie = list_movie[i]
            break

    current_movie['rating'] = rating
    del list_movie[i]
    list_movie.append(current_movie)
    movie_data.nd = list_movie
    movie_data.commit()

    return redirect(url_for('pages.movie', _id = current_movie['_id']))

@pages.route("/movie/<string:_id>/watch_date/")
@login_required
def watch_date(_id):
    movie_data.open()
    list_movie = [movie for movie in movie_data.nd]
    current_movie = None
    for i in range(len(list_movie)):
        if list_movie[i]['_id'] == _id:
            current_movie = list_movie[i]
            break

    current_movie['last_watched'] = datetime.today().strftime("%b %d %Y")
    del list_movie[i]
    list_movie.append(current_movie)
    movie_data.nd = list_movie
    movie_data.commit()
    
    return redirect(url_for('pages.movie', _id = current_movie['_id']))

@pages.route("/edit/<string:_id>/", methods = ["GET", "POST"])
@login_required
def edit_movie(_id):
    movie_data.open()
    list_movie = [movie for movie in movie_data.nd]
    current_movie = None
    for i in range(len(list_movie)):
        if list_movie[i]['_id'] == _id:
            current_movie = list_movie[i]
            break
    movie = Movie(**current_movie)
    form = ExtendedMovieForm(obj = movie)


    if form.validate_on_submit():
        movie = dict(
            _id = movie._id,
            title = form.title.data,
            director = form.director.data,
            year = form.year.data,
            cast = form.cast.data,
            series = form.series.data,
            tags = form.tags.data,
            description = form.description.data,
            video_link = form.video_link.data,
        )

        del list_movie[i]
        list_movie.append(movie)
        movie_data.nd = list_movie
        movie_data.commit()

        return redirect(url_for('pages.movie', _id = movie['_id']))

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
        user_data.open()
        lst_email = [acc['email'] for acc in user_data.nd]
        if user.email in lst_email:
            flash("This email had been registerd already. Use another email!", "danger")
            return redirect("/register")
        user_data.append(asdict(user))
        user_data.commit()

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

        user_data.open()
        lst_user = user_data.nd
        for user in lst_user:
            if user['email'] == login_dic['email'] and pbkdf2_sha256.verify(login_dic['password'], user['password']):
                session['email'] = user['email']
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