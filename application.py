from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, jsonify
# this is used for form validation
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, RadioField
from passlib.hash import sha256_crypt  # this is used to encrypt the passwords
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import datetime
import requests
from send_mail import send_mail

import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# set the database url inside the quotes using this command
# $ export DATABASE_URL=""
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")


app.config['SECRET_KEY'] = "ADD_A_SECRET_KEY"


# this is the default route
@app.route('/')
def index():
    return render_template('index.html')


# we are using wtforms for the registration and this is registration class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message="Passwords do not match")
    ])
    confirm = PasswordField('Confirm Password')


# register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        # hashing the password for security reasons
        password = sha256_crypt.hash(str(form.password.data))
        # checking if username already exists
        if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchall():
            flash("Username already taken", 'danger')
            return render_template('register.html', form=form)
        else:
            # adding the data to the database
            db.execute("INSERT INTO users (name, email, username, password) VALUES (:name, :email , :username, :password)", {
                "name": name, "email": email, "username": username, "password": password})
            db.commit()
            # registration success message
            flash("Registered and you can now login", 'success')
            # redirecting to the login page
            return redirect(url_for('login'))

    # if method is GET else will be executed
    else:
        if 'logged_in' in session:
            flash('already logged in', 'success')
            return redirect(url_for('index'))
        else:
            return render_template('register.html', form=form)


# login route
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # getting form fields
        username = request.form['username']
        password_entered = request.form['password']

        found = db.execute(
            "SELECT * FROM users WHERE username = :username", {"username": username}).fetchall()
        print(found)
        # checking if user is present
        if found:
            # getting the stored hash value
            password = found[0][4]
            # comparing the 2 passwords
            if sha256_crypt.verify(password_entered, password):
                # passwords matched so we create a session for the user
                session['logged_in'] = True
                session['username'] = username
                found = db.execute(
                    "SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
                if found:
                    email = found[2]
                    name = found[1]
                    session['email'] = email
                    session['name'] = name

                # Flashing the success message
                flash("You are now logged in", 'success')
                return redirect(url_for('index'))
            else:
                # passwords didnt match
                error = "Wrong Password"
                return render_template('login.html', error=error)
        else:
            error = "Username not found"
            return render_template('login.html', error=error)
    # if method is GET else will be executed
    else:
        if 'logged_in' in session:
            flash('already logged in', 'success')
            return redirect(url_for('index'))
        else:
            return render_template('login.html')


# if user is accessing sites by typing in urlbar we have to check
# if he is logged in or not before giving access
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please Login first', 'danger')
            return redirect(url_for('login'))
    return wrap


# this route is for library
@app.route('/library', methods=['GET', 'POST'])
# access to this route is given only if the user is logged in
# using python decorator
@is_logged_in
def library():
    if request.method == 'POST':
        # getting form fields
        searchby = request.form['searchby']
        keyword = request.form['keyword']
        # if keyword is isbn
        # notFound is used to know if books with that keyword are present or not
        # tablePrint is used to print the table only after user click search
        if searchby == 'isbn':
            result = db.execute(
                " SELECT * FROM books WHERE isbn LIKE '%"+keyword+"%' ;").fetchall()
            print(result)
            if not result:
                return render_template('library.html', notFound=True, tablePrint=False)
            else:
                return render_template('library.html', records=result, notFound=False, tablePrint=True)
        # if keyword is title
        elif searchby == 'title':
            result = db.execute(
                " SELECT * FROM books WHERE title LIKE '%"+keyword+"%' ;").fetchall()
            if not result:
                return render_template('library.html', notFound=True, tablePrint=False)
            else:
                return render_template('library.html', records=result, notFound=False, tablePrint=True)
        # if keyword is author
        elif searchby == 'author':
            result = db.execute(
                " SELECT * FROM books WHERE author LIKE '%"+keyword+"%' ;").fetchall()
            print(result)
            if not result:
                return render_template('library.html', notFound=True, tablePrint=False)
            else:
                return render_template('library.html', records=result, notFound=False, tablePrint=True)
        # if keyword is year
        else:
            result = db.execute(
                " SELECT * FROM books WHERE year = :year ;", {'year': keyword}).fetchall()
            print(result)
            if not result:
                return render_template('library.html', notFound=True, tablePrint=False)
            else:
                return render_template('library.html', records=result, notFound=False, tablePrint=True)
    # if method is GET
    return render_template('library.html', tablePrint=False)


# this route is for book
@app.route('/book/<isbn>', methods=['GET', 'POST'])
# access to this route is given only if the user is logged in
@is_logged_in
def book(isbn):
    # checking if ISBN is valid or not
    valid = db.execute("SELECT * FROM books WHERE isbn = :isbn ;",
                       {'isbn': isbn}).fetchall()
    if not valid:
        return render_template('404.html')
    # if the isbn value is valid
    else:
        res = requests.get("https://www.goodreads.com/book/review_counts.json",
                           params={"key": "PLACE_YOUR_KEY_HERE", "isbns": isbn})
        apidata = res.json()
        dbdata = db.execute(
            " SELECT * FROM books WHERE isbn = :isbn ;", {'isbn': isbn}).fetchone()
        print(dbdata)

        reviewdata = db.execute(
            " SELECT * FROM reviews WHERE isbn = :isbn ;", {'isbn': isbn}).fetchall()

        reviewsfound = False
        if reviewdata:
            reviewsfound = True

        title = dbdata[2]
        author = dbdata[3]
        year = dbdata[4]
        isbn = dbdata[1]
        ratings_count = apidata['books'][0]['ratings_count']
        average_rating = apidata['books'][0]['average_rating']
        print(apidata)
        print(reviewdata)
        # if the method is POST, when user is submiting review
        if request.method == "POST":
            username = session['username']
            already = db.execute(
                " SELECT * FROM reviews WHERE username = :username and isbn = :isbn ;", {'username': username, 'isbn': isbn}).fetchone()
            # checking if the review is already added
            if already:
                flash("Review already added", 'danger')
                return render_template('book.html', isbn=isbn, title=title, author=author, year=year, ratings_count=ratings_count, average_rating=average_rating, reviews=reviewdata, reviewsfound=reviewsfound)
            # user didn't review, therefore we are adding in the database
            else:
                rating = request.form['rating']
                comment = request.form['comment']
                # inserting into database
                db.execute("INSERT INTO reviews (username, rating, comment, isbn) VALUES (:username, :rating , :comment, :isbn)", {
                    "username": username, "rating": rating, "comment": comment, "isbn": isbn})
                db.commit()
                # flashing message
                flash("Review added", 'success')
                return render_template('book.html', isbn=isbn, title=title, author=author, year=year, ratings_count=ratings_count, average_rating=average_rating, reviews=reviewdata, reviewsfound=reviewsfound)
        # if the method is GET
        else:
            return render_template('book.html', isbn=isbn, title=title, author=author, year=year, ratings_count=ratings_count, average_rating=average_rating, reviews=reviewdata, reviewsfound=reviewsfound)


# to get api data
@app.route('/api/<isbn>', methods=['GET', 'POST'])
# access to this route is given only if the user is logged in
@is_logged_in
def api(isbn):
    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": "PLACE_YOUR_KEY_HERE", "isbns": isbn})
    apidata = res.json()

    dbdata = db.execute(
        " SELECT * FROM books WHERE isbn = :isbn ;", {'isbn': isbn}).fetchone()

    title = dbdata[2]
    author = dbdata[3]
    year = dbdata[4]
    isbn = dbdata[1]
    ratings_count = apidata['books'][0]['ratings_count']
    average_rating = apidata['books'][0]['average_rating']
    review_count = apidata['books'][0]['reviews_count']

    output = {
        "title": title,
        "author": author,
        "year": year,
        "isbn": isbn,
        "ratings_count": ratings_count,
        "average_rating": average_rating,
        "review_count": review_count
    }
    return jsonify(output)


# for contact form
class ContactForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    body = TextAreaField('Body', [validators.Length(min=10)])


# route for contact
@app.route('/contact', methods=['GET', 'POST'])
# access to this route is given only if the user is logged in
@is_logged_in
def contact():
    form = ContactForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        body = form.body.data
        if username != session['username'] or email != session['email']:
            flash('Enter correct username and email', 'danger')
            return render_template('contact.html', form=form)
        else:
            # TODO need to connect to mail service
            send_mail(username, email, body)
            flash('Message Sent!', 'success')
            return redirect(url_for('index'))
    return render_template('contact.html', form=form)


# this route is for dashboard
@app.route('/dashboard')
# access to this route is given only if the user is logged in
@is_logged_in
def dashboard():
    username = session['username']
    email = session['email']
    name = session['name']

    reviewdata = db.execute(
        " SELECT * FROM reviews WHERE username = :username ;", {'username': username}).fetchall()

    reviewsfound = False
    if reviewdata:
        reviewsfound = True

    return render_template('dashboard.html', username=username, email=email, name=name, reviews=reviewdata, reviewsfound=reviewsfound)


# route to logout
@app.route('/logout')
# access to this route is given only if the user is logged in
@is_logged_in
def logout():
    session.clear()
    flash("You are now logged out", 'success')
    return redirect(url_for('index'))


# if user goes into some route that does not exist then this route will be used
@app.errorhandler(404)
# inbuilt function that takes
def page_not_found(e):
    return render_template('404.html')  # , 404


if __name__ == '__main__':
    app.debug = True
    app.run()
