"""I control everything."""

from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request, flash, session,
                   jsonify)
from datetime import datetime
from model import connect_to_db, db, User
from server-utilities import *

app = Flask(__name__)

app.secret_key = "shhhhhhhhhhh!!! don't tell!"

#keep jinja from failing silently because of undefined variables
app.jinja_env.undefined = StrictUndefined


#################### ROUTES TO SHOW HOMEPAGE AND DASHBOARD ####################


@app.route("/")
def index():
    """Show the homepage"""

    return render_template("home.html")


@app.route("/<string:username>")
def show_dashboard(username):
    """Show the dashboard of user with given username"""

    #get the user with the given username (if any)
    dash_owner = (db.session.query(User)
                            .filter(User.username == username)
                            .first())

    #if given username isn't valid (not in database), redirect to a
    #user-not-found page
    if dash_owner is None:
        return render_template("user-not-found.html")

    #otherwise, determine if the user is logged in and asking to view their
    #own dashboard
    viewing_own_dash = user_is_logged_in(username=username)

    #show the dashboard
    return render_template("dashboard.html",
                           dash_owner=dash_owner,
                           viewing_own_dash=viewing_own_dash)


######### HELPER FUNCTIONS FOR LOGIN, LOGOUT, AND REGISTRATION ROUTES #########



#################### LOGIN, LOGOUT, AND REGISTRATION ROUTES ####################

@app.route("/email-not-found")
def email_not_found():
    """Called by form validator. Returns false if given email found in
       the database."""

    if email_in_database(request.args.get("email")):
        return "false"
    else:
        return "true"


@app.route("/username-not-found")
def username_not_found():
    """Called by form validator. Returns false if given username found in
       the database."""

    if username_in_database(request.args.get("username")):
        return "false"
    else:
        return "true"


@app.route("/username-or-email-found")
def username_or_email_found():
    """Called by form validator. Returns true if given username or email found
       in the database."""

    credential = request.args.get("username_or_email")

    #assume that the presence of an @ symbol means it's an email
    if "@" in credential:
        found = email_in_database(credential)
    else:
        found = username_in_database(credential)

    #return the results as a string
    if found:
        return "true"
    else:
        return "false"


@app.route("/register-user", methods=["POST"])
def add_new_user():
    """Add new user to the Users and User_stat_lists tables

       Note that all form data is validated before being submitted, so the
       values here should just work"""

    #get data from the form
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

    #create the new user and add them to the database
    print "\n\ncreating new user: ", username, " ", password
    new_user = User(firstname=firstname, lastname=lastname, gender=gender,
                    birthdate=birthdate, zipcode=zipcode, email=email,
                    username=username, password=password, weight=weight)
    db.session.add(new_user)
    db.session.commit()

    #pull the new user's id from the database
    id_of_added_user = (db.session.query(User.user_id)
                          .filter(User.username == username)
                          .one())

    #add that id to the session for easy grabbing and to signify thier
    #logged-in state
    session["logged_in_user_id"] = id_of_added_user

    #display the user's dashboard page, in logged-in state
    return redirect("/" + username)


@app.route("/password-matches")
def check_password():
    """Called by the form validator. Returns true if password matches given
       email or username."""

    credential = request.args.get("credential")
    password = request.args.get("password")
    print "got " + credential + password

    if password_is_correct(credential, password):
        return "true"
    else:
        return "false"


@app.route("/login", methods=["POST"])
def log_user_in():
    """Log the user with the given username or email in.

       Note that credential validation happens on the front end."""

    credential = request.form.get("username_or_email")

    #look up the user in the database
    #the presence of an @ symbol means the credential is an email
    if "@" in credential:
        user = db.session.query(User).filter(User.email == credential).one()
    #otherwise, assume it's a username
    else:
        user = db.session.query(User).filter(User.username == credential).one()

    #add the user's id to the session for easy grabbing and to signify thier
    #logged-in state
    session["logged_in_user_id"] = user.user_id

    #display the user's dashboard page, in logged-in state
    return redirect("/" + user.username)


@app.route("/logout", methods=["POST"])
def log_user_out():
    """Log user out by clearing the session. Return user to whatever page
       they were on."""

    session.clear()

    return render_template("home.html")



if __name__ == "__main__":
    """If we run this file from the command line, do this stuff"""

    app.debug = True

    connect_to_db(app)

    app.run()
