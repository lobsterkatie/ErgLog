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



#################### LOGIN, LOGOUT, AND REGISTRATION ROUTES ####################

@app.route("/email-not-found")
def email_not_found():
    """Called by form validator. Returns false if given email found."""

    if email_in_database(request.args.get("email")):
        return "false"
    else:
        return "true"


@app.route("/username-not-found")
def username_not_found():
    """Called by form validator. Returns false if given username found."""

    if username_in_database(request.args.get("username")):
        return "false"
    else:
        return "true"


    # @app.route("/username-or-email-not-found")
    # def username_or_email_not_found():
    # """Checks the given username or email against the User table. Returns 
    #     false if found."""

    # value = request.args.get("username_or_email")
    # if "@" in value:
    #     return 


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

    #pull the user from the database (where they should now be), so that
    #the user object contains the auto-assigned values as well (which the
    #new_user object we created above doesn't)
    added_user = (db.session.query(User)
                            .filter(User.username == username)
                            .one())

    #add the user to the session for easy grabbing and to signify thier
    #logged-in state
    session["user"] = added_user

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
