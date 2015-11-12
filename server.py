"""I control everything."""

from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request, flash, session,
                   jsonify)
from datetime import datetime
from model import connect_to_db, db, User, WorkoutResult
from server_utilities import *

app = Flask(__name__)

app.secret_key = "shhhhhhhhhhh!!! don't tell!"

#keep jinja from failing silently because of undefined variables
app.jinja_env.undefined = StrictUndefined

#define a custom filter for displaying dates in rendered templates
@app.template_filter()
def date_filter(value, format="Mon Jan 1, 2000"):
    """A custom Jinja filter to format dates"""

    if format == "Mon Jan 1, 2000":
        date_string = "{date:%a} {date:%b} {date.day}, {date.year}"
        return date_string.format(date=value)

#add custom date filter to jinja's repertoire
app.jinja_env.filters["date_filter"] = date_filter



##################### ROUTES TO SHOW HOMEPAGE AND LOG PAGE #####################


@app.route("/")
def index():
    """Show the homepage"""

    return render_template("home.html")


@app.route("/log")
def show_log():
    """Show the user their log (if they're logged in; otherwise, show the
       homepage with the login window open.)""" #LOGIN WINDOW OPEN NOT IMPLEMENTED YET

    #existence of a user_id in the session signifies that someone's signed in
    logged_in_user_id = session["logged_in_user_id"]
    if logged_in_user_id:
        user = (db.session.query(User)
                          .filter(User.user_id == logged_in_user_id)
                          .one())
        days_until_HOCR = days_til_HOCR()
        workouts = (db.session.query(WorkoutResult)
                              .filter(WorkoutResult.user_id == logged_in_user_id)
                              .order_by(WorkoutResult.date.desc())
                              .all())
        return render_template("log.html", user=user,
                                           days_til_HOCR=days_until_HOCR,
                                           workouts=workouts)
    else:
        #TODO make login window open when home is rendered
        return render_template("home.html")


@app.route("/get-workout-details/<int:workout_result_id>.json")
def return_workout_details(workout_result_id):
    """Given a workout_result_id, return a jsonified version of the workout
       details, including the workout template, piece templates, workout result,
       piece results, and split results.

       The final jsonified data will have the following structure:
           workout_details = {
                workout_template: {dict}
                workout_result: {dict}
                pieces: {
                    piece 1: {
                        piece_template: {dict}
                        piece_result: {dict}
                        splits: {
                            split 1: {dict}
                            split 2: {dict}
                            ...
                        }
                    piece 2: {
                        ...
                    }
                    ...
                }
            }
    """

    #get the workout_result and workout_template objects associated with the
    #given id and dictionaryify them
    workout_result = (db.session.query(WorkoutResult)
                                .filter(WorkoutResult.workout_result_id ==
                                        workout_result_id)
                                .one())
    workout_template = workout_result.workout_template
    w_result_dict = workout_result.to_dict()
    w_template_dict = workout_template.to_dict()

    #get the piece results for this workout and create a dictionary of
    #piece dictionaries (keyed by ordinal)
    #each piece's dictionary will include dictionary versions of the
    #template object, results object, and a splits dictionary holding
    #dictionary versions of the splits (also keyed by ordinal)
    piece_results = workout_result.piece_results
    pieces_dict = {}
    for p in piece_results:
        #create a dictionary to hold info about this one piece, and add
        #dictionary versions of this piece's template and results to it
        p_dict = {}
        p_dict["template"] = p.piece_template.to_dict()
        p_dict["results"] = p.to_dict()

        #get split results, if any, for this piece
        split_results = p.split_results

        #if there are split results, make a dictionary to hold them and add
        #a dictionary version of each, keyed by its ordinal, then add the whole
        #splits dictionary to the dictionary for this piece
        if split_results:
            splits_dict = {} #to hold information about all this piece's splits
            for s in split_results:
                splits_dict["split " + str(s.ordinal)] = s.to_dict
            p_dict["splits"] = splits_dict

        #otherwise (if there weren't any split results), reflect that in the
        #piece dictionary
        else:
            p_dict["splits"] = None

        #now that the dictionary for this piece is complete, add it to the
        #dictionary holding all the pieces, using its ordinal as a key
        pieces_dict["piece " + str(p.ordinal)] = p_dict

    #add the workout_template, workout_results, and pieces dictionaries to
    #the overall workout_details dictionary, then jsonify and return it
    workout_details_dict = {}
    workout_details_dict["workout_template"] = w_template_dict
    workout_details_dict["workout_results"] = w_result_dict
    workout_details_dict["pieces"] = pieces_dict
    workout_details = jsonify(workout_details_dict)
    return workout_details



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


@app.route("/password-matches-credential")
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


@app.route("/register-user", methods=["POST"])
def add_new_user():
    """Add new user to the users and user_stat_lists tables

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

    #display the user's log page
    return redirect("/log")


@app.route("/login", methods=["POST"])
def log_user_in():
    """Log in the user with the given username or email.

       Notes:
       1) credential validation happens on the front end.
       2) if someone actually goes to the url stuff.com/login, the
          'GET-ness' of the GET request will trigger the login window if
          they're not already logged in """ #NOT IMPLEMENTED YET

    if request.method == 'POST':
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

        #display the user's log page
        return redirect("/log")

    elif request.method == 'GET':
        #TODO implement note 2 above, take off comment, add method to decorator
        pass


@app.route("/logout", methods=["POST"])
def log_user_out():
    """Log user out by clearing the session. Return user to homepage."""

    session.clear()

    return redirect("/")



if __name__ == "__main__":
    """If we run this file from the command line, do this stuff"""

    app.debug = True

    connect_to_db(app)

    app.run()
