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