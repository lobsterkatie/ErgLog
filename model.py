"""Models and database functions for the project.
    Based largely on the model.py file written by HB staff. (Thanks, guys!)"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, schema
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
    """Logbook user"""

    __tablename__ = "Users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.Unicode(64), nullable=False)
    lastname = db.Column(db.Unicode(64), nullable=False)
    gender = db.Column(db.Enum(["F", "M", "Other"]), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    #I GUESS THAT MEANS ONLY THE US FOR THE MOMENT
    zipcode = db.Column(db.Numeric(5, 0), nullable=False)
    email = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    #ASK ABOUT DEFAULT TODAY
    date_joined = db.Column(db.Date, nullable=False, default=date.today())
    #WOULD LIKE TO CALCULATE THIS FROM ZIPCODE
    # in hours ahead or behind UTC
    timezone = db.Column(db.Integer, nullable=False, default=0)
    weight = db.Column(db.Numeric(4, 1), nullable=False)

    def __repr__(self):
        """Output the object's values when it's printed"""

        repr_string = "<User id: {id}, name: {firstname} {lastname}, email: {email}>"
        return repr_string.format(id=self.user_id, firstname=self.firstname,
                                  lastname=self.lastname, email=self.email)


class User_stat(db.Model):
    """Stats for a given user, mostly PR's (one-to-one with Users)"""

    __tablename__ = "User_stats"

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

    user = db.relationship("User", backref="stats")


    def __repr__(self):
        """Output the object's values when it's printed"""

        #start the string with the user_id
        repr_string = "<User_stat user_id: {id} ".format(id=self.user_id)

        #for each of the object's attributes, excluding dunder attributes
        #(because we don't care about them) and the user_id (because we've
        #already got it)...
        for attr, value in self.__dict__.items():
            # print attr, type(attr)
            # print value, type(value)
            if not str(attr).startswith(("_", "user_id")):

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



class Movie(db.Model):
    """Movie table"""

    __tablename__ = "Movies"

    movie_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False)
    released_at = db.Column(db.DateTime, nullable=True)
    imdb_url = db.Column(db.Text, nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        repr_string = "<Movie movie_id={id}, title={title}, released_at={date}, imdb_url={url}>"
        return repr_string.format(id=self.movie_id, 
                                  title=self.title, 
                                  date=self.released_at, 
                                  url=self.imdb_url)


class Rating(db.Model):
    """Ratings table"""

    __tablename__ = "Ratings"


    rating_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    movie_id = db.Column(db.Integer, db.ForeignKey("Movies.movie_id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("Users.user_id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)

    movie = db.relationship('Movie',
                            backref=db.backref("ratings"), order_by=desc(score))
    user = db.relationship("User", 
                           backref=db.backref("ratings"), order_by=desc(score))

    #TODO clean seed data so we can put this back in then fix add new rating
    #route to try adding the new rating (which will error out if it's a duplicate)
    #and then reroute to the update route (this also means add/update ratings hasn't
    #been fully tested yet)
    __table_args__ = (schema.UniqueConstraint(user_id, movie_id),)


    def __repr__(self):
        """Provide helpful representation when printed."""

        repr_string = "<Rating rating_id={id}, movie_id={movie}, user_id={user}, score={score}>"
        return repr_string.format(id=self.rating_id,
                                  movie=self.movie_id,
                                  user=self.user_id,
                                  score=self.score)

##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ratings.db'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."