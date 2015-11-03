"""I control everything."""

from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request, flash, session,
                   jsonify)
from model import connect_to_db, db, User
from datetime import datetime

app = Flask(__name__)

app.secret_key = "shhhhhhhhhhh!!! don't tell!"

#keep jinja from failing silently because of undefined variables
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Show the homepage"""

    # return "I exist!"

    return render_template("home.html")


#################### LOGIN, LOGOUT, AND REGISTRATION ROUTES ####################

@app.route("/check-email")
def check_email_uniqueness():
    """Checks the given email against the User table. Returns false if found."""

    email = request.args.get("email")
    num_matched = (db.session.query(User)
                             .filter(User.email == email)
                             .count())

    if num_matched == 1:
        return "false"
    else:
        return "true"


@app.route("/check-username")
def check_username_uniqueness():
    """Checks the given username against the User table. Returns false if found."""

    username = request.args.get("username")
    num_matched = (db.session.query(User)
                             .filter(User.username == username)
                             .count())

    if num_matched == 1:
        return "false"
    else:
        return "true"


@app.route("/register-user", methods=["POST"])
def add_new_user():
    """Add new user to the Users and User_stat_lists tables

       Note that all form data is validated before being submitted, so the
       values here should just work"""

    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    gender = request.form.get("gender")
    birthdate = (datetime.strptime(request.form.get("birthdate"), "%b %d, %Y")
                         .date())
    zipcode = request.form.get("zipcode")
    email = request.form.get("email")
    username = request.form.get("username")
    password = hash(request.form.get("password"))
    #TODO implement timezones
    weight = request.form.get("weight")

    new_user = User(firstname=firstname, lastname=lastname, gender=gender,
                    birthdate=birthdate, zipcode=zipcode, email=email,
                    username=username, password=password, weight=weight)
    db.session.add(new_user)
    db.session.commit()

    #HOW DO I GET IT TO GO TO THE LOGIN MODAL? SAME QUESTION FOR LINK
    #WHICH NEEDS TO BE ADDED TO REGISTRATION MODAL





if __name__ == "__main__":
    """If we run this file from the command line, do this stuff"""

    app.debug = True

    connect_to_db(app)

    app.run()
