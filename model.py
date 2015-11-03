"""Models and database functions for the project.
    Based largely on the model.py file written by HB staff. (Thanks, guys!)"""

from flask_sqlalchemy import SQLAlchemy
from datetime import date

# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)
db = SQLAlchemy()

def format_time_from_seconds(sec):
    """return a string in the form D:H:M:S given a number of seconds"""

    if sec < 0:
        raise Exception("Non-negative seconds value expected.")

    time_string = ""
    remaining_seconds = sec

    # calculate and subtract off days
    days = remaining_seconds / 86400
    remaining_seconds = remaining_seconds - days*86400

    # calculate and subtract off hours
    hours = remaining_seconds / 3600
    remaining_seconds = remaining_seconds - hours*3600

    #calculate and subtract off minutes
    minutes = remaining_seconds / 60
    remaining_seconds = remaining_seconds - minutes*60

    #seconds are what remains
    seconds = remaining_seconds

    #create the string, avoiding leading zeros
    if days != 0:
        time_string = time_string + str(days) + ":"
        time_string = time_string + str(hours) + ":"
        time_string = time_string + str(minutes) + ":"
        time_string = time_string + str(seconds)
    elif hours != 0:
        time_string = time_string + str(hours) + ":"
        time_string = time_string + str(minutes) + ":"
        time_string = time_string + str(seconds)
    elif minutes != 0:
        time_string = time_string + str(minutes) + ":"
        time_string = time_string + str(seconds)
    else:
        time_string = ":" + str(seconds)

    #return the string
    return time_string


##############################################################################
# Model definitions

class User(db.Model):
    """Logbook user (one-to-one with user stat lists, one-to-many with both
       workout results and workout templates)"""

    __tablename__ = "Users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.Unicode(64), nullable=False)
    lastname = db.Column(db.Unicode(64), nullable=False)
    gender = db.Column(db.Enum("F", "M", "Other", name="Genders"), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    #I GUESS THAT MEANS ONLY THE US FOR THE MOMENT
    zipcode = db.Column(db.Numeric(5, 0), nullable=False)
    email = db.Column(db.String(64), nullable=False, unique=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    #ASK ABOUT DEFAULT TODAY
    date_joined = db.Column(db.Date, nullable=False, default=date.today())
    #WOULD LIKE TO CALCULATE THIS FROM ZIPCODE EVENTUALLY
    # in hours ahead or behind UTC
    timezone = db.Column(db.Integer, nullable=True, default=0)
    weight = db.Column(db.Numeric(4, 1), nullable=False)


    def __repr__(self):
        """Output the object's values when it's printed"""

        repr_string = "<User id: {id}, name: {firstname} {lastname}, email: {email}>"
        return repr_string.format(id=self.user_id, firstname=self.firstname,
                                  lastname=self.lastname, email=self.email)



class User_stat_list(db.Model):
    """Stats for a given user, mostly PR's (one-to-one with Users)"""

    __tablename__ = "User_stat_lists"

    user_id = db.Column(db.Integer, db.ForeignKey("Users.user_id"),
                        primary_key=True)
    lifetime_meters = db.Column(db.Integer, nullable=False, default=0)
    # time-based PR's are in number of meters
    one_min_PR_dist = db.Column(db.Integer, nullable=True)
    half_hour_PR_dist = db.Column(db.Integer, nullable=True)
    hour_PR_dist = db.Column(db.Integer, nullable=True)
    # distance-based PR's are in number of seconds
    half_K_PR_time = db.Column(db.Numeric(6, 1), nullable=True)
    one_K_PR_time = db.Column(db.Numeric(6, 1), nullable=True)
    two_K_PR_time = db.Column(db.Numeric(6, 1), nullable=True)
    five_K_PR_time = db.Column(db.Numeric(6, 1), nullable=True)
    six_K_PR_time = db.Column(db.Numeric(6, 1), nullable=True)
    ten_K_PR_time = db.Column(db.Numeric(6, 1), nullable=True)
    half_marathon_PR_time = db.Column(db.Numeric(6, 1), nullable=True)
    marathon_PR_time = db.Column(db.Numeric(6, 1), nullable=True)

    #one (user) to one (stats)
    user = db.relationship("User", backref="stat_list", uselist=False)


    def __repr__(self):
        """Output the object's values when it's printed"""

        #start the string with the user_id
        repr_string = "<User_stat_list user_id: {id} ".format(id=self.user_id)

        #for each of the object's attributes, excluding dunder attributes
        #(because we don't care about them) and the user_id (because we've
        #already got it)...
        for attr, value in self.__dict__.items():
            # print attr, type(attr)
            # print value, type(value)
            if not attr.startswith(("_", "user_id")):

                #format the values
                if attr.endswith("time"):
                    value = format_time_from_seconds(value)
                else:
                    value = str(value) + " m"

                #add the stat to the string
                repr_string += ", {stat}: {value}".format(stat=attr,
                                                          value=value)

        #close out the string and return it
        repr_string += ">"
        return repr_string



class Workout_result(db.Model):
    """The data/results of a workout (one-to-many with piece results,
       many-to-one with both users and workout templates)"""

    __tablename__ = "Workout_results"

    workout_result_id = db.Column(db.Integer,
                                  primary_key=True,
                                  autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    time_of_day = db.Column(db.Time, nullable=True)
    #TODO SHOULD BE FILLED IN WHEN PIECES ARE ADDED (ONUPDATE BELT ETC?)
    total_meters = db.Column(db.Integer, nullable=False, default=0)
    avg_HR = db.Column(db.Integer, nullable=True)
    calories = db.Column(db.Integer, nullable=True)
    comments = db.Column(db.UnicodeText, nullable=True)
    public = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey("Users.user_id"),
                        nullable=False)
    workout_template_id = db.Column(db.Integer,
                                    db.ForeignKey("Workout_templates.workout_template_id"),
                                    nullable=False)

    #one (user) to many (workout results)
    user = db.relationship("User", backref="workout_results")
    #one (workout template) to many (workout results)
    workout_template = db.relationship("Workout_template",
                                       backref="workout_results")


    def __repr__(self):
        """Output the object's values when it's printed"""

        repr_string = ("<Workout_result id: {id}, template_id: {template_id}" +
                       "user_id: {user_id}, date: {date}, time: {time}>")
        return repr_string.format(id=self.workout_result_id,
                                  template_id=self.workout_template_id,
                                  user_id=self.user_id,
                                  date=self.date,
                                  time=self.time_of_day)


class Piece_result(db.Model):
    """Piece results (many-to-one with workout_results, one-to-many with
       piece templates)"""

    __tablename__ = "Piece_results"

    piece_result_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    total_time_seconds = db.Column(db.Integer, nullable=False)
    total_meters = db.Column(db.Integer, nullable=False)
    avg_split_seconds = db.Column(db.Integer, nullable=False)
    avg_SR = db.Column(db.Integer, nullable=False)
    avg_watts = db.Column(db.Integer, nullable=True)
    avg_HR = db.Column(db.Integer, nullable=True)
    drag_factor = db.Column(db.Integer, nullable=True)
    comments = db.Column(db.UnicodeText, nullable=True)
    workout_result_id = db.Column(db.Integer,
                                  db.ForeignKey("Workout_results.workout_result_id"),
                                  nullable=False)
    piece_template_id = db.Column(db.Integer,
                                  db.ForeignKey("Piece_templates.piece_template_id"),
                                  nullable=False)

    #one (workout result) to many (piece results)
    workout_result = db.relationship("Workout_result", backref="piece_results")

    #one (piece template) to many (piece results)
    piece_template = db.relationship("Piece_template", backref="piece_results")


    def __repr__(self):
        """Output the object's values when it's printed"""

        repr_string = ("<Piece_result id: {id}, " +
                       "workout_result_id: {workout_result_id}, " +
                       "piece_template_id: {piece_template_id}>")
        return repr_string.format(id=self.piece_result_id,
                                  workout_result_id=self.workout_result_id,
                                  piece_template_id=self.piece_template_id)



class Split_result(db.Model):
    """Split results (many-to-one with piece_results)"""

    __tablename__ = "Split_results"

    split_result_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ordinal = db.Column(db.Integer, nullable=False)
    label = db.Column(db.String(64), nullable=True)
    time_seconds = db.Column(db.Integer, nullable=False)
    meters = db.Column(db.Integer, nullable=False)
    avg_split_seconds = db.Column(db.Integer, nullable=False)
    avg_SR = db.Column(db.Integer, nullable=False)
    avg_watts = db.Column(db.Integer, nullable=True)
    avg_HR = db.Column(db.Integer, nullable=True)
    comments = db.Column(db.UnicodeText, nullable=True)
    piece_result_id = db.Column(db.Integer,
                                db.ForeignKey("Piece_results.piece_result_id"),
                                nullable=False)

    #one (piece result) to many (split results)
    piece_result = db.relationship("Piece_result", backref="split_results")


    def __repr__(self):
        """Output the object's values when it's printed"""

        repr_string = ("<Split_result id: {id}, " +
                       "piece_result_id:{piece_result_id}>" +
                       "(split # {ordinal})>")
        return repr_string.format(id=self.split_result_id,
                                  piece_result_id=self.piece_result_id,
                                  ordinal=self.ordinal)


class Workout_template(db.Model):
    """Workout templates (many-to-many with piece templates via the
        wtemlate-ptemplate_pairing class/table, many-to-one with users)"""

    __tablename__ = "Workout_templates"

    workout_template_id = db.Column(db.Integer,
                                    primary_key=True,
                                    autoincrement=True)
    description = db.Column(db.Unicode(256), nullable=False)
    primary_zone = db.Column(db.String(8), nullable=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey("Users.user_id"),
                        nullable=False)

    #one (user) to many (workout templtates)
    user = db.relationship("User", backref="workout_templates")

    #many (piece templates) to many (workout templates)
    piece_templates = db.relationship("Piece_template",
                                      secondary="Wtemplate_ptemplate_pairings",
                                      primaryjoin="Workout_template.workout_template_id == Wtemplate_ptemplate_pairing.workout_template_id",
                                      secondaryjoin="Piece_template.piece_template_id == Wtemplate_ptemplate_pairing.piece_template_id",
                                      viewonly=True)


    def __repr__(self):
        """Output the object's values when it's printed"""

        repr_string = "<Workout_template id: {id}, user_id: {user_id}>"
        return repr_string.format(id=self.workout_template_id,
                                  user_id=self.user_id)


class Wtemplate_ptemplate_pairing(db.Model):
    """Not quite a true association table (because it has ordinal data)
       between workout templates and piece templates (one-to-many with
       both)"""

    __tablename__ = "Wtemplate_ptemplate_pairings"

    wtemplate_ptemplate_pairing_id = db.Column(db.Integer,
                                               primary_key=True,
                                               autoincrement=True)
    ordinal = db.Column(db.Integer, nullable=False)
    workout_template_id = db.Column(db.Integer,
                                    db.ForeignKey("Workout_templates.workout_template_id"),
                                    nullable=False)
    piece_template_id = db.Column(db.Integer,
                                  db.ForeignKey("Piece_templates.piece_template_id"),
                                  nullable=False)

    #one (workout template) to many (wtemlate-ptemplate pairings)
    workout_template = db.relationship("Workout_template",
                                       backref="wtemplate_ptemplate_pairings")

    #one (piece template) to many (wtemlate-ptemplate pairings)
    piece_template = db.relationship("Piece_template",
                                     backref="wtemplate_ptemplate_pairings")

    #TODO DO I NEED A __REPR__ METHOD?


class Piece_template(db.Model):
    """Templates for pices (many-to-many with workout templates, via the
        wtemlate-ptemplate_pairing class/table)"""

    __tablename__ = "Piece_templates"

    piece_template_id = db.Column(db.Integer,
                                  primary_key=True,
                                  autoincrement=True)
    piece_type = db.Column(db.Enum("time", "distance", name="Piece_types"),
                           nullable=False)
    distance = db.Column(db.Integer, nullable=True)
    time_seconds = db.Column(db.Integer, nullable=True)
    goal_split_seconds = db.Column(db.Integer, nullable=True)
    goal_SR = db.Column(db.Integer, nullable=True)
    phase = db.Column(db.Enum("warmup", "workout body", "cooldown",
                              name="Workout_phases"), nullable=False)
    zone = db.Column(db.String(8), nullable=True)
    description = db.Column(db.UnicodeText(), nullable=False)
    split_length = db.Column(db.Integer, nullable=True)


    def __repr__(self):
        """Output the object's values when it's printed"""

        repr_string = "<Piece_template id: {id} ({description})>"
        return repr_string.format(id=self.piece_template_id,
                                  description=self.description)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///workoutlog'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
