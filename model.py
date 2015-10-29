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
    #WOULD LIKE TO CALCULATE THIS FROM ZIPCODE EVENTUALLY
    # in hours ahead or behind UTC
    timezone = db.Column(db.Integer, nullable=False, default=0)
    weight = db.Column(db.Numeric(4, 1), nullable=False)

    #get lists of a user's followers or followees
    followers = relationship("User",
                             secondary="Followings",
                             primaryjoin=(user_id == Following.followee_id),
                             secondaryjoin=(user_id == Following.follower_id),
                             backref=db.backref("followees", lazy="dynamic"))





    def __repr__(self):
        """Output the object's values when it's printed"""

        repr_string = "<User id: {id}, name: {firstname} {lastname}, email: {email}>"
        return repr_string.format(id=self.user_id, firstname=self.firstname,
                                  lastname=self.lastname, email=self.email)

    def is_following(self, user):
        """Returns true iff self is already following user"""

        #filter the list of users self is following by [user]'s id
        #if something is found, self is already following [user]
        return self.followees.filter(Following.followee_id == user.user_id)
                             .count() != 0


    def follow(self, user):
        """Adds user to self's list of followees"""

        if not self.is_following(user):
            self.followees.append(user) #DOES THIS WORK???

            #new_following = Following(follower_id=self.user_id, followee_id=user.user_id)
            #db.session.add(new_following)
            #db.session.commit()


    def unfollow(self, user):
        """Removes user from self's list of followees"""

        if self.is_following(user):
            self.followees.remove(user) #DOES THIS WORK??

            # followhsip = db.session.query(Following)
            #                        .filter(Following.follower_id == self.user_id,
            #                                Following.followee_id == user.user_id)
            #                        .one()
            # db.session.delete(followship)
            # db.session.commit()


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


class Following(db.Model):
    """Table keeping track of who's following whom"""

    __tablename__ = "Followings"

    followship_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    follower_id = db.Column(db.Integer, db.ForeignKey("User.user_id"), nullable=False)
    followee_id = db.Column(db.Integer, db.ForeignKey("User.user_id"), nullable=False)

    #SHOULD I DO A COMPOSITE PRIMARY KEY INSTEAD OF A REGULAR ID? HOW TO DO THIS? 
    #(seems like just putting primary key on both does it?)
    #(IF SO, CAN PRESUMABLY TAKE OUT THE COMPOSITE UNIQUE CONSTRAINT BELOW)

    #make sure that the same follower can't follow the same followee twice
    __table_args__ = (schema.UniqueConstraint(follower_id, followee_id),)


    def __repr__(self):
        """Output the object's values when it's printed"""

        repr_string = "<Following followship_id: {id}, follower_id: " +
                      "{follower}, followee_id: {followee}>"
        return repr_string.format(id=self.followship_id, 
                                  follower=self.follower_id,
                                  followee=self.followee_id)


class Workout_result(db.Model):
    """The data/results of a workout"""

    __tablename__ = "Workout_results"

    workout_results_id = db.Column(db.Integer, primary_key=True,
                                   autoincrement=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=True)
    #TODO SHOULD BE FILLED IN WHEN PIECES ARE ADDED (ONUPDATE BELT ETC?)
    total_meters = db.Column(db.Integer, nullable=False, default=0)
    avg_HR = db.Column(db.Integer, nullable=True)
    calories = db.Column(db.Integer, nullable=True)
    comments = db.Column(db.UnicodeText, nullable=True)
    public = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User.user_id"), nullable=False)
    workout_template_id = db.Column(db.Integer,
                          db.ForeignKey("Workout_template.workout_template_id"),
                          nullable=False)

    user = db.relationship("User",
                           backref=db.backref("workout_results",
                                              order_by=(date, time)))
    #HOW DO I MAKE IT SO THAT THE BACKREF ONLY GETS RESULTS FROM THIS USER?
    workout_template = db.relationship("Workout_template")


    def __repr__(self):
        """Output the object's values when it's printed"""

        repr_string = "<Workout_result id:{id}, template_id: {template_id}" +
                      "user_id: {user_id}, date: {date}, time: {time}>"
        return repr_string.format(id=self.workout_results_id,
                                  template_id=workout_template_id,
                                  user_id=user_id,
                                  date=date,
                                  time=time)

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