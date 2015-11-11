################################################################################
#  STUFF ABOUT BEING ABLE TO SEE OTHER USER'S PAGES #


@app.route("/<string:username>")
def show_dashboard(username):
    """Show the dashboard of user with given username"""

    #get the user with the given username (if any)
    dash_owner = (db.session.query(User)
                            .filter(User.username == username)
                            .first())

    #if given username isn't valid (not in database), redirect to a
    #user-not-found page
    if dash_owner is None:
        return render_template("user-not-found.html")

    #otherwise, determine if the user is logged in and asking to view their
    #own dashboard
    viewing_own_dash = user_is_logged_in(username=username)

    #show the dashboard
    return render_template("dashboard.html",
                           dash_owner=dash_owner,
                           viewing_own_dash=viewing_own_dash)






@app.route("/register-user", methods=["POST"])
def add_new_user():
    
    ...

    #display the user's dashboard page, in logged-in state
    return redirect("/" + username)






@app.route("/login", methods=["POST"])
def log_user_in():
    
    ...

    #display the user's dashboard page, in logged-in state
    return redirect("/" + user.username)




@app.route("/logout", methods=["POST"])
def log_user_out():
    """Log user out by clearing the session. Return user to whatever page
       they were on."""



################################################################################
# GOAL FIELDS TO BE PUT... SOMEWHERE... IN THE DATABASE #

    goal_split_seconds = db.Column(db.Integer)
    goal_sr = db.Column(db.Integer)
    goal_hr = db.Column(db.Integer)
    goal_watts = db.Column(db.Integer)


