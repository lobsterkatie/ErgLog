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


#################### ROUTES TO SHOW HOMEPAGE AND DASHBOARD ####################


@app.route("/")
def index():
    """Show the homepage"""

    return render_template("home.html")


@app.route("/<string:username>")
def show_dashboard(username):
    pass


######### HELPER FUNCTIONS FOR LOGIN, LOGOUT, AND REGISTRATION ROUTES #########
def email_in_database(email):
    """Returns true if the given email is found in the Users table."""

    #count how many users in the database have the given email (should be 1 or 0)
    num_matched = (db.session.query(User)
                             .filter(User.email == email)
                             .count())

    #if there's a user with that email, return true; otherwise, return false
    if num_matched == 1:
        return True
    else:
        return False


def username_in_database(username):
    """Returns true if the given username is found in the Users table."""

    #count how many users in the database have the given username (should be 1 or 0)
    num_matched = (db.session.query(User)
                             .filter(User.username == username)
                             .count())

    #if there's a user with that username, return true; otherwise, return false
    if num_matched == 1:
        return True
    else:
        return False

def table_record_object_to_dict(record_object):
    """Takes an object representing a record from the database and creates
       a dictionary out of its values (as strings)"""

    pass

    # record_dict = {}

    # #add each of the object's attributes, excluding dunder attributes
    # #(because we don't care about them) and the user_id (because we've
    #     #already got it)...
    #     for attr, value in self.__dict__.items():
    #         # print attr, type(attr)
    #         # print value, type(value)
    #         if attr.startswith(("_", "password")):

    #             #pop it from the dictionary


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


@app.route("/login/<int:user_id>")
def log_user_in(user_id):
    pass



if __name__ == "__main__":
    """If we run this file from the command line, do this stuff"""

    app.debug = True

    connect_to_db(app)

    app.run()
