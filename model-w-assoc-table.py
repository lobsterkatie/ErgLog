"""Models and database functions for the project.
    Based largely on the model.py file written by HB staff. (Thanks, guys!)"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import schema
from datetime import date

# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)
db = SQLAlchemy()

##############################################################################
# Helper functions, ToDict mixin

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


class ToDictMixin(object):
    """Provides a method to return a dictionary version of a model class."""

    def to_dict(self):
        """Returns a dictionary representing the object"""

        dict_of_obj = {}

        #iterate through the table's columns, adding the value in each
        #to the dictionary
        for column_name in self.__mapper__.column_attrs.keys():
            value = getattr(self, column_name, None)
            dict_of_obj[column_name] = value

        #return the completed dictionary
        return dict_of_obj


##############################################################################
# Model definitions

class User(db.Model, ToDictMixin):
    """Logbook user (one-to-one with user stat lists, one-to-many with both
       workout results and workout templates)"""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    firstname = db.Column(db.Unicode(64))
    lastname = db.Column(db.Unicode(64))
    gender = db.Column(db.Enum("F", "M", "Other", name="genders"))
    birthdate = db.Column(db.Date)
    weight = db.Column(db.Numeric(4, 1))
    date_joined = db.Column(db.Date, default=date.today())
    zipcode = db.Column(db.Numeric(5, 0))
    # in hours ahead or behind UTC
    timezone = db.Column(db.Integer, default=0)
    #TODO calculate timezone from zipcode or OS

    #one (stat list) to one (user)
    stat_list = db.relationship("UserStatList",
                                backref="user",
                                uselist=False)

    #many (workout results) to one (user)
    workout_results = db.relationship("WorkoutResult", backref="user")

    #many (workout templates) to one (user)
    workout_templates = db.relationship("WorkoutTemplate", backref="user")


    def __repr__(self):
        """Output the object's values when it's printed"""

        repr_string = "<User id: {id}, name: {firstname} {lastname}, email: {email}>"
        return repr_string.format(id=self.user_id, firstname=self.firstname,
                                  lastname=self.lastname, email=self.email)



class UserStatList(db.Model, ToDictMixin):
    """Stats for a given user, mostly PR's (one-to-one with Users)"""

    __tablename__ = "user_stat_lists"

    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"),
                        primary_key=True)
    lifetime_meters = db.Column(db.Integer, nullable=False, default=0)
    #flag to track if there's a new PR
    new_pr = db.Column(db.Boolean, nullable=False, default=False)
    # time-based PR's are in number of meters
    one_min_pr_dist = db.Column(db.Integer)
    half_hour_pr_dist = db.Column(db.Integer)
    hour_pr_dist = db.Column(db.Integer)
    # distance-based PR's are in number of seconds
    half_k_pr_time = db.Column(db.Numeric(6, 1))
    one_k_pr_time = db.Column(db.Numeric(6, 1))
    two_k_pr_time = db.Column(db.Numeric(6, 1))
    five_k_pr_time = db.Column(db.Numeric(6, 1))
    six_k_pr_time = db.Column(db.Numeric(6, 1))
    ten_k_pr_time = db.Column(db.Numeric(6, 1))
    half_marathon_pr_time = db.Column(db.Numeric(6, 1))
    marathon_pr_time = db.Column(db.Numeric(6, 1))


    def __repr__(self):
        """Output the object's values when it's printed"""

        #start the string with the user_id
        repr_string = "<UserStatList user_id: {id} ".format(id=self.user_id)

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



class WorkoutTemplate(db.Model, ToDictMixin):
    """Workout templates (many-to-many with piece templates via the
       w_p_template_pairings table, many-to-one with users)"""

    __tablename__ = "workout_templates"

    workout_template_id = db.Column(db.Integer,
                                    primary_key=True,
                                    autoincrement=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey("users.user_id"),
                        nullable=False)
    primary_zone = db.Column(db.Unicode(32))
    description = db.Column(db.Unicode(256)) #TODO autogenerate?
    warmup_format = db.Column(db.Unicode(128)) #same
    warmup_stroke_rates = db.Column(db.Unicode(128)) #same
    warmup_notes = db.Column(db.UnicodeText)
    workout_body_format = db.Column(db.Unicode(128)) #same
    workout_body_stroke_rates = db.Column(db.Unicode(128)) #same
    workout_body_notes = db.Column(db.UnicodeText)
    cooldown_format = db.Column(db.Unicode(128)) #same
    cooldown_stroke_rates = db.Column(db.Unicode(128)) #same
    cooldown_notes = db.Column(db.UnicodeText)

    #many (workout results) to one (workout template)
    workout_results = db.relationship("WorkoutResult",
                                      backref="workout_template")

    #many (piece templates) to many (workout templates)
    #TODO MAKE SURE THE ORDERING WORKS, AND FIGURE OUT IF YOU GET MULTIPLE
    #COPIES OF PIECE TEMPLATES (DO I NEED TO SPECIFY PRIMARY AND SECONDARY
    #JOINS?) SAME QUESTION WITH THE FILTERED PIECE TEMPLATES BELOW
    piece_templates = db.relationship("PieceTemplate",
                                      secondary="w_p_template_pairings",
                                      order_by="WPTemplatePairing.ordinal",
                                      backref="workout_templates")

    #internal join strings specifying the joins for filtered piece template
    #attributes below
    _wu_join = ("and_(" +
                    "WPTemplatePairing.piece_template_id == " +
                        "PieceTemplate.piece_template_id, " +
                    "PieceTemplate.phase == 'warmup')")
    _main_join = ("and_(" +
                      "WPTemplatePairing.piece_template_id == " +
                          "PieceTemplate.piece_template_id, " +
                      "PieceTemplate.phase == 'main')")
    _cd_join = ("and_(" +
                    "WPTemplatePairing.piece_template_id == " +
                        "PieceTemplate.piece_template_id, " +
                    "PieceTemplate.phase == 'cooldown')")

    #subsets of the associated piece templates, filtered by phase
    warmup_piece_templates = (db.relationship("PieceTemplate",
                                              secondary="w_p_template_pairings",
                                              secondaryjoin=_wu_join))
    main_piece_templates = (db.relationship("PieceTemplate",
                                            secondary="w_p_template_pairings",
                                            secondaryjoin=_main_join))
    cooldown_piece_templates = (db.relationship("PieceTemplate",
                                                secondary="w_p_template_pairings",
                                                secondaryjoin=_cd_join))


    def __repr__(self):
        """Output the object's values when it's printed"""

        repr_string = "<WorkoutTemplate id: {id}, user_id: {user_id}>"
        return repr_string.format(id=self.workout_template_id,
                                  user_id=self.user_id)



class WPTemplatePairing(db.Model, ToDictMixin):
    """Not quite a true association table (because it has ordinal data)
       between workout templates and piece templates (one-to-many with
       both)"""

    __tablename__ = "w_p_template_pairings"

    w_p_template_pairing_id = db.Column(db.Integer,
                                        primary_key=True,
                                        autoincrement=True)
    workout_template_id = db.Column(db.Integer,
                                    db.ForeignKey("workout_templates.workout_template_id"),
                                    nullable=False)
    piece_template_id = db.Column(db.Integer,
                                  db.ForeignKey("piece_templates.piece_template_id"),
                                  nullable=False)
    ordinal = db.Column(db.Integer, nullable=False)


    #this makes sure that two different pieces can't be the nth piece in a
    #given workout
    __table_args__ = (schema.UniqueConstraint(workout_template_id, ordinal),)




class PieceTemplate(db.Model, ToDictMixin):
    """Templates for pieces (many-to-many with workout templates via the
       w_p_template_pairings table)"""

    __tablename__ = "piece_templates"

    piece_template_id = db.Column(db.Integer,
                                  primary_key=True,
                                  autoincrement=True)
    phase = db.Column(db.Enum("warmup", "main", "cooldown",
                              name="workout_phases"),
                              nullable=False)
    piece_type = db.Column(db.Enum("time", "distance", name="piece_types"))
    distance = db.Column(db.Integer)
    time_seconds = db.Column(db.Integer)
    default_split_length = db.Column(db.Integer)
    zone = db.Column(db.String(8))
    description = db.Column(db.UnicodeText)


    def __repr__(self):
        """Output the object's values when it's printed"""

        repr_string = "<PieceTemplate id: {id} ({description})>"
        return repr_string.format(id=self.piece_template_id,
                                  description=self.description)



class WorkoutResult(db.Model, ToDictMixin):
    """The data/results of a workout (one-to-many with piece results,
       many-to-one with both users and workout templates)"""

    __tablename__ = "workout_results"

    workout_result_id = db.Column(db.Integer,
                                  primary_key=True,
                                  autoincrement=True)
    workout_template_id = db.Column(db.Integer,
                                    db.ForeignKey("workout_templates.workout_template_id"),
                                    nullable=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey("users.user_id"),
                        nullable=False)
    total_meters = db.Column(db.Integer, default=0, nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_of_day = db.Column(db.Time)
    avg_HR = db.Column(db.Integer)
    calories = db.Column(db.Integer)
    comments = db.Column(db.UnicodeText)
    public = db.Column(db.Boolean)


    #many (piece results) to one (workout result)
    piece_results = db.relationship("PieceResult", backref="workout_result")

    #internal join strings specifying the joins for filtered piece result
    #attributes below
    _wu_join = ("and_(" +
                    "WorkoutResult.workout_result_id == " + 
                        "PieceResult.workout_result_id, " +
                    "PieceResult.phase == 'warmup')")
    _main_join = ("and_(" +
                      "WorkoutResult.workout_result_id == " + 
                          "PieceResult.workout_result_id, " +
                      "PieceResult.phase == 'main')")
    _cd_join = ("and_(" +
                    "WorkoutResult.workout_result_id == " + 
                        "PieceResult.workout_result_id, " +
                    "PieceResult.phase == 'cooldown')")

    #subsets of the associated piece results, filtered by phase
    warmup_piece_results = (db.relationship("PieceTemplate",
                                              primaryjoin=_wu_join))
    main_piece_results = (db.relationship("PieceTemplate",
                                            primaryjoin=_main_join))
    cooldown_piece_results = (db.relationship("PieceTemplate",
                                                primaryjoin=_cd_join))


    def __repr__(self):
        """Output the object's values when it's printed"""

        repr_string = ("<WorkoutResult id: {id}, template_id: {template_id}" +
                       "user_id: {user_id}, date: {date}, time: {time}>")
        return repr_string.format(id=self.workout_result_id,
                                  template_id=self.workout_template_id,
                                  user_id=self.user_id,
                                  date=self.date,
                                  time=self.time_of_day)


class PieceResult(db.Model, ToDictMixin):
    """Piece results (many-to-one with workout_results, one-to-many with
       piece templates)"""

    __tablename__ = "piece_results"

    piece_result_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    workout_result_id = db.Column(db.Integer,
                                  db.ForeignKey("workout_results.workout_result_id"),
                                  nullable=False)
    piece_template_id = db.Column(db.Integer,
                                  db.ForeignKey("piece_templates.piece_template_id"),
                                  nullable=False)
    ordinal = db.Column(db.Integer, nullable=False)
    goal_split_seconds = db.Column(db.Integer)
    goal_SR = db.Column(db.Integer)
    total_time_seconds = db.Column(db.Integer)
    total_meters = db.Column(db.Integer)
    split_length = db.Column(db.Integer)
    avg_split_seconds = db.Column(db.Integer)
    avg_SR = db.Column(db.Integer)
    avg_watts = db.Column(db.Integer)
    avg_HR = db.Column(db.Integer)
    drag_factor = db.Column(db.Integer)
    comments = db.Column(db.UnicodeText)
    completed = db.Column(db.Boolean)
    exclude_from_prs = db.Column(db.Boolean)

    #one (piece template) to many (piece results)
    piece_template = db.relationship("PieceTemplate", backref="piece_results")

    #this makes sure that two different pieces can't be the nth piece in a
    #given workout
    __table_args__ = (schema.UniqueConstraint(workout_result_id, ordinal),)


    def __repr__(self):
        """Output the object's values when it's printed"""

        repr_string = ("<PieceResult id: {id}, " +
                       "workout_result_id: {workout_result_id}, " +
                       "piece_template_id: {piece_template_id}>")
        return repr_string.format(id=self.piece_result_id,
                                  workout_result_id=self.workout_result_id,
                                  piece_template_id=self.piece_template_id)



class SplitResult(db.Model, ToDictMixin):
    """Split results (many-to-one with piece_results)"""

    __tablename__ = "split_results"

    split_result_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    piece_result_id = db.Column(db.Integer,
                                db.ForeignKey("piece_results.piece_result_id"),
                                nullable=False)
    ordinal = db.Column(db.Integer, nullable=False)
    label = db.Column(db.String(64))
    time_seconds = db.Column(db.Integer)
    meters = db.Column(db.Integer)
    avg_split_seconds = db.Column(db.Integer)
    avg_SR = db.Column(db.Integer)
    avg_watts = db.Column(db.Integer)
    avg_HR = db.Column(db.Integer)
    comments = db.Column(db.UnicodeText)

    #one (piece result) to many (split results)
    piece_result = db.relationship("PieceResult",
                                   backref=db.backref("split_results",
                                                      order_by="split_results.ordinal"))

    #this makes sure that two different splits can't be the nth split in a
    #given piece
    __table_args__ = (schema.UniqueConstraint(piece_result_id, ordinal),)


    def __repr__(self):
        """Output the object's values when it's printed"""

        repr_string = ("<SplitResult id: {id}, " +
                       "piece_result_id:{piece_result_id}>" +
                       "(split # {ordinal})>")
        return repr_string.format(id=self.split_result_id,
                                  piece_result_id=self.piece_result_id,
                                  ordinal=self.ordinal)



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
