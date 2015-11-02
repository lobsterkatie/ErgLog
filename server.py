"""I control everything."""

from jinja2 import StrictUndefined
from flask import Flask, render_template, redirect, request, flash, session
from model import connect_to_db, db

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
    """Add new user to the Users and User_stat_lists tables"""

    pass






if __name__ == "__main__":
    """If we run this file from the command line, do this stuff"""

    app.debug = True

    connect_to_db(app)

    app.run()
