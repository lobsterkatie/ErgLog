"""I control everything."""

from jinja2 import StrictUndefined
from flask import (Flask, render_template, redirect, request, flash, session,
                   jsonify)
from datetime import datetime, timedelta
from model import (connect_to_db, db, User, WorkoutResult, WorkoutTemplate,
                   PieceTemplate)
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



@app.route("/save-workout-template.json", methods=["POST"])
def save_workout_template():
    """When user submits form creating a new workout, save it in the database,
       and return the template (jsonified) for further action (like adding
       results) if desired.

       The final jsonified data will have the following structure:
            new_workout_template = {
                workout_template: {dict}
                pieces: {
                    piece 1: {
                        template: {dict}
                    }
                    piece 2: {
                        template: {dict}
                    }
                    ...
                }
            }
    """

    #create a new record in the workout_templates table with the given inputs
    new_w_temp = WorkoutTemplate()
    new_w_temp.user_id = session["logged_in_user_id"]
    new_w_temp.num_pieces = request.form.get("num-pieces", type=int)
    new_w_temp.primary_zone = request.form.get("primary-zone")
    new_w_temp.description = request.form.get("workout-description")
    new_w_temp.warmup_format = request.form.get("warmup-format")
    new_w_temp.warmup_stroke_rates = request.form.get("warmup-sr")
    new_w_temp.warmup_notes = request.form.get("warmup-notes")
    new_w_temp.main_format = request.form.get("main-format")
    new_w_temp.main_stroke_rates = request.form.get("main-sr")
    new_w_temp.main_notes = request.form.get("main-notes")
    new_w_temp.cooldown_format = request.form.get("cooldown-format")
    new_w_temp.cooldown_stroke_rates = request.form.get("cooldown-sr")
    new_w_temp.cooldown_notes = request.form.get("cooldown-notes")
    new_w_temp.date_added = datetime.now()
    db.session.add(new_w_temp)
    db.session.commit()

    #get the newly added workout template record from the database
    added_w_template = (db.session.query(WorkoutTemplate)
                                  .filter(WorkoutTemplate.date_added ==
                                                new_w_temp.date_added)
                                  .one())

    #create a new record in the piece_templates table for each piece template
    num_pieces = new_w_temp.num_pieces
    for i in range(1, num_pieces + 1):
        #stringify i so it can be used in field names
        i = str(i)
        new_p_temp = PieceTemplate()
        new_p_temp.workout_template_id = added_w_template.workout_template_id
        new_p_temp.ordinal = request.form.get("ordinal-piece-" + i, type=int)
        new_p_temp.phase = request.form.get("phase-piece-" + i)
        new_p_temp.piece_type = request.form.get("type-piece-" + i)
        new_p_temp.distance = request.form.get("distance-piece-" + i, type=int)
        new_p_temp.time_seconds = hms_string_to_seconds(
                                    request.form.get("time-piece-" + i))
        new_p_temp.has_splits = request.form.get("split-bool-piece-" + i)
        if new_p_temp.piece_type == "time":
            new_p_temp.default_split_length = hms_string_to_seconds(
                                                    request.form.get(
                                                        "split-length-piece-" +
                                                        i))
        else:
            new_p_temp.default_split_length = request.form.get(
                                                "split-length-piece-" + i,
                                                type=int)
        new_p_temp.rest = request.form.get("rest-piece-" + i)
        new_p_temp.zone = request.form.get("zone-piece-" + i)
        new_p_temp.notes = request.form.get("notes-piece-" + i)
        db.session.add(new_p_temp)
        db.session.commit()

    #create a dictionary version of the new workout template (verbosely, which
    #means it will include the just-added piece templates)
    new_workout_template_dict = added_w_template.to_dict_verbose()

    #jsonify the result and return it
    new_workout_template_json = jsonify(new_workout_template_dict)
    return new_workout_template_json



@app.route("/get-workout-templates.json")
def get_workout_templates():
    """Queries the database for workout templates without results
       (recently-added and less-recently-added), and workout templates with
       results. Returns verbose (including pieces) versions of both.

       The final jsonified data will have the following structure:
            workout_templates = {
                no_results_recent: [
                    {workout_template dict}
                    {workout_template_dict}
                    ...
                ]
                no_results_older: [
                    {workout_template dict}
                    {workout_template_dict}
                    ...
                ]
                with_results: [
                    {workout_template dict}
                    {workout_template_dict}
                    ...
                ]
            }
       """


    #get all workout templates with no results, splitting them into those
    #added in the last week and those added earlier
    a_week_ago = datetime.now() - timedelta(days=7)
    no_results_recent = (db.session.query(WorkoutTemplate)
                                    .outerjoin(WorkoutTemplate.workout_results)
                                    .filter(WorkoutResult.workout_result_id
                                                         .is_(None))
                                    .filter(WorkoutTemplate.date_added >
                                            a_week_ago)
                                    .all())
    no_results_older = (db.session.query(WorkoutTemplate)
                                  .outerjoin(WorkoutTemplate.workout_results)
                                  .filter(WorkoutResult.workout_result_id
                                                       .is_(None))
                                  .filter(WorkoutTemplate.date_added <
                                          a_week_ago)
                                  .all())

    #get workout templates which *have* have results added (in case the user
    #wants to redo a workout)
    with_results = (db.session.query(WorkoutTemplate)
                              .outerjoin(WorkoutTemplate.workout_results)
                              .filter(WorkoutResult.workout_result_id
                                                   .isnot(None))
                              .all())

    #dictionaryify the results in each case
    no_results_recent_dicts = []
    for template in no_results_recent:
        no_results_recent_dicts += template.to_dict_verbose()
    no_results_older_dicts = []
    for template in no_results_older:
        no_results_older_dicts += template.to_dict_verbose()
    with_results_dicts = []
    for template in with_results:
        with_results_dicts += template.to_dict_verbose()

    #add each list to an overall dictionary for jsonification
    workout_templates_dict = {}
    workout_templates_dict["no_results_recent"] = no_results_recent_dicts
    workout_templates_dict["no_results_older"] = no_results_older_dicts
    workout_templates_dict["with_results"] = with_results_dicts

    #jsonify the result and return it
    workout_templates = jsonify(workout_templates_dict)
    return workout_templates




@app.route("/get-workout-details/<int:workout_result_id>.json")
def return_workout_details(workout_result_id):
    """Given a workout_result_id, return a jsonified version of the workout
       details, including the workout template, piece templates, workout
       result, piece results, and split results.

       The final jsonified data will have the following structure:
           workout_details = {
                workout_template: {dict}
                workout_result: {dict}
                pieces: {
                    piece 1: {
                        template: {dict}
                        results: {dict}
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

    #get the workout_result object associated with the given id and
    #dictionaryify it (verbosely, which means it will include the template
    #and the pieces)
    workout_result = (db.session.query(WorkoutResult)
                                .filter(WorkoutResult.workout_result_id ==
                                        workout_result_id)
                                .one())
    workout_details_dict = workout_result.to_dict_verbose()

    #jsonify the result and return it
    workout_details_json = jsonify(workout_details_dict)
    return workout_details_json




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
