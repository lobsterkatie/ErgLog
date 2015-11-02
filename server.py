"""I control everything."""

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session
from model import connect_to_db, db, User

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

@app.route("/register-user", methods=["POST"])
def add_new_user():
    """Add new user to the Users and User_stat_lists tables

       Note that all form data is validated before being submitted, so the
       values here should just work"""

    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    gender = request.form.get("gender")
    birthdate = request.form.get("birthdate")
    zipcode = request.form.get("zipcode")
    email = request.form.get("email")
    username = request.form.get("username")
    password = hash(request.form.get("password"))
    timezone = 0 #TODO implement timezones
    weight = request.form.get("weight")

    new_user = User(firstname=firstname, lastname=lastname, gender=gender,
                    birthdate=birthdate, zipcode=zipcode, email=email,
                    username=username, password=password, timezone=timezone,
                    weight=weight)
    db.session.add(new_user)
    db.session.commit()






if __name__ == "__main__":
    """If we run this file from the command line, do this stuff"""

    app.debug = True

    connect_to_db(app)

    app.run()
