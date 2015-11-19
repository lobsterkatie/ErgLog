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
    """Workout templates (one-to-many with piece templates, many-to-one
       with users)"""

    __tablename__ = "workout_templates"

    workout_template_id = db.Column(db.Integer,
                                    primary_key=True,
                                    autoincrement=True)
    user_id = db.Column(db.Integer,
                        db.ForeignKey("users.user_id"),
                        nullable=False)
    num_pieces = db.Column(db.Integer)
    description = db.Column(db.Unicode(256)) #TODO autogenerate?
    primary_zone = db.Column(db.Unicode(32))
    warmup_format = db.Column(db.Unicode(128)) #same
    warmup_stroke_rates = db.Column(db.Unicode(128)) #same
    warmup_notes = db.Column(db.UnicodeText)
    main_format = db.Column(db.Unicode(128)) #same
    main_stroke_rates = db.Column(db.Unicode(128)) #same
    main_notes = db.Column(db.UnicodeText)
    cooldown_format = db.Column(db.Unicode(128)) #same
    cooldown_stroke_rates = db.Column(db.Unicode(128)) #same
    cooldown_notes = db.Column(db.UnicodeText)
    date_added = db.Column(db.DateTime)

    #many (workout results) to one (workout template)
    workout_results = db.relationship("WorkoutResult",
                                      backref="workout_template")

    #many (piece templates) to one (workout templates)
    piece_templates = db.relationship("PieceTemplate",
                                      order_by="PieceTemplate.ordinal",
                                      backref="workout_template")

    #internal join strings specifying the joins for filtered piece template
    #attributes below
    _wu_join = ("and_(" +
                    "WorkoutTemplate.workout_template_id == " +
                        "PieceTemplate.workout_template_id, " +
                    "PieceTemplate.phase == 'warmup')")
    _main_join = ("and_(" +
                      "WorkoutTemplate.workout_template_id == " +
                          "PieceTemplate.workout_template_id, " +
                      "PieceTemplate.phase == 'main')")
    _cd_join = ("and_(" +
                    "WorkoutTemplate.workout_template_id == " +
                        "PieceTemplate.workout_template_id, " +
                    "PieceTemplate.phase == 'cooldown')")

    #subsets of the associated piece templates, filtered by phase
    warmup_piece_templates = (db.relationship("PieceTemplate",
                                              primaryjoin=_wu_join))
    main_piece_templates = (db.relationship("PieceTemplate",
                                            primaryjoin=_main_join))
    cooldown_piece_templates = (db.relationship("PieceTemplate",
                                                primaryjoin=_cd_join))


    def __repr__(self):
        """Output the object's values when it's printed"""

        repr_string = "<WorkoutTemplate id: {id}, user_id: {user_id}>"
        return repr_string.format(id=self.workout_template_id,
                                  user_id=self.user_id)


    def to_dict_verbose(self):
        """Creates a dictionary representation of the WorkoutTemplate
           object, including all associated piece templates.

           The returned dictionary will have the following structure:
                returned_dict = {
                    workout_template: {dict}
                    pieces: {
                        1: {
                            template: {dict}
                        }
                        2: {
                            template: {dict}
                        }
                        ...
                    }
                }
        """

        #create a dictionary of self and add it to dict_to_return
        dict_to_return = {}
        dict_to_return["workout_template"] = self.to_dict()

        #create a dictionary to hold piece templates, and stock it, keyed
        #by piece ordinal
        pieces_dict = {}
        for p in self.piece_templates:
            p_dict = {}
            p_dict["template"] = p.to_dict()
            pieces_dict[p.ordinal] = p_dict

        #add the pieces dictionary to the main dictionary and return it
        dict_to_return["pieces"] = pieces_dict
        return dict_to_return



class PieceTemplate(db.Model, ToDictMixin):
    """Templates for pieces (many-to-one with workout templates)"""

    __tablename__ = "piece_templates"

    piece_template_id = db.Column(db.Integer,
                                  primary_key=True,
                                  autoincrement=True)
    workout_template_id = db.Column(db.Integer,
                                    db.ForeignKey("workout_templates.workout_template_id"),
                                    nullable=False)
    ordinal = db.Column(db.Integer, nullable=False)
    phase = db.Column(db.Enum("warmup", "main", "cooldown",
                              name="workout_phases"),
                      nullable=False)
    ordinal_in_phase = db.Column(db.Integer)
    piece_type = db.Column(db.Enum("time", "distance", name="piece_types"))
    zone = db.Column(db.Unicode(32))
    distance = db.Column(db.Integer)
    time_seconds = db.Column(db.Integer)
    rest = db.Column(db.Unicode(32))
    has_splits = db.Column(db.Boolean)
    default_split_length = db.Column(db.Integer)
    notes = db.Column(db.UnicodeText)

    #this makes sure that two different pieces can't be the nth piece in a
    #given workout, nor the nth piece in a particular phase of a given workout
    __table_args__ = (schema.UniqueConstraint(workout_template_id, ordinal),)
    __table_args__ = (schema.UniqueConstraint(workout_template_id,
                                              ordinal_in_phase),)

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
    avg_hr = db.Column(db.Integer)
    calories = db.Column(db.Integer)
    goals = db.Column(db.UnicodeText)
    comments = db.Column(db.UnicodeText)
    warmup_comments = db.Column(db.UnicodeText)
    main_comments = db.Column(db.UnicodeText)
    cooldown_comments = db.Column(db.UnicodeText)
    public = db.Column(db.Boolean) #not yet being used


    #many (piece results) to one (workout result)
    piece_results = db.relationship("PieceResult", backref="workout_result")

    # TODO fix these
    # #internal join strings specifying the joins for filtered piece result
    # #attributes below
    # _wu_join = ("and_(" +
    #                 "WorkoutResult.workout_result_id == " +
    #                     "PieceResult.workout_result_id, " +
    #                 "PieceResult.phase == 'warmup')")
    # _main_join = ("and_(" +
    #                   "WorkoutResult.workout_result_id == " +
    #                       "PieceResult.workout_result_id, " +
    #                   "PieceResult.phase == 'main')")
    # _cd_join = ("and_(" +
    #                 "WorkoutResult.workout_result_id == " +
    #                     "PieceResult.workout_result_id, " +
    #                 "PieceResult.phase == 'cooldown')")

    # #subsets of the associated piece results, filtered by phase
    # warmup_piece_results = (db.relationship("PieceTemplate",
    #                                           primaryjoin=_wu_join))
    # main_piece_results = (db.relationship("PieceTemplate",
    #                                         primaryjoin=_main_join))
    # cooldown_piece_results = (db.relationship("PieceTemplate",
    #                                             primaryjoin=_cd_join))


    def __repr__(self):
        """Output the object's values when it's printed"""

        repr_string = ("<WorkoutResult id: {id}, template_id: {template_id}" +
                       "user_id: {user_id}, date: {date}, time: {time}>")
        return repr_string.format(id=self.workout_result_id,
                                  template_id=self.workout_template_id,
                                  user_id=self.user_id,
                                  date=self.date,
                                  time=self.time_of_day)


    def to_dict_verbose(self):
        """Create a dictionary version of self, including workout template
           and pieces (themselves including results, template, and splits).

           The returned dictionary will have the following structure:
                returned_dict = {
                    workout_template: {dict}
                    workout_result: {dict}
                    pieces: {
                        1: {
                            template: {dict}
                            results: {dict}
                            splits: {
                                1: {dict}
                                2: {dict}
                                ...
                            }
                        2: {
                            ...
                        }
                        ...
                    }
                }
        """

        #create a dictionary from self and the associated workout template
        w_result_dict = self.to_dict()
        w_template_dict = self.workout_template.to_dict()

        #get the piece results for this workout and create a dictionary of
        #piece dictionaries (keyed by ordinal)
        #each piece's dictionary will include dictionary versions of the
        #template object, results object, and a splits dictionary holding
        #dictionary versions of the splits (also keyed by ordinal)
        piece_results = self.piece_results
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
            #a dictionary version of each, keyed by its ordinal, then add the
            #whole splits dictionary to the dictionary for this piece
            if split_results:
                splits_dict = {} #to hold info about all this piece's splits
                for s in split_results:
                    splits_dict[s.ordinal] = s.to_dict
                p_dict["splits"] = splits_dict

            #otherwise (if there weren't any split results), reflect that in
            #the piece dictionary
            else:
                p_dict["splits"] = None

            #now that the dictionary for this piece is complete, add it to the
            #dictionary holding all the pieces, using its ordinal as a key
            pieces_dict[p.ordinal] = p_dict

        #add the workout_template, workout_results, and pieces dictionaries to
        #the overall dictionary, then return it
        dict_to_return = {}
        dict_to_return["workout_template"] = w_template_dict
        dict_to_return["workout_results"] = w_result_dict
        dict_to_return["pieces"] = pieces_dict
        return dict_to_return


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
    goal_sr = db.Column(db.Integer)
    goal_hr = db.Column(db.Integer)
    goal_watts = db.Column(db.Integer)
    total_time_seconds = db.Column(db.Integer)
    total_meters = db.Column(db.Integer)
    has_splits = db.Column(db.Boolean)
    split_length = db.Column(db.Integer)
    avg_split_seconds = db.Column(db.Integer)
    avg_sr = db.Column(db.Integer)
    avg_watts = db.Column(db.Integer)
    avg_hr = db.Column(db.Integer)
    drag_factor = db.Column(db.Integer)
    comments = db.Column(db.UnicodeText)
    completed = db.Column(db.Boolean)
    exclude_from_prs = db.Column(db.Boolean)

    #one (piece template) to many (piece results)
    piece_template = db.relationship("PieceTemplate", backref="piece_results")

    #many (split results) to one (piece result)
    split_results = db.relationship("SplitResult",
                                    order_by="SplitResult.ordinal",
                                    backref="piece_result")

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
    avg_sr = db.Column(db.Integer)
    avg_watts = db.Column(db.Integer)
    avg_hr = db.Column(db.Integer)
    comments = db.Column(db.UnicodeText)


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
