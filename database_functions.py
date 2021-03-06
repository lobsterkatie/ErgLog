################################################################################
# TO REMAKE DATABASE #

\c Katie
DROP DATABASE workoutlog;
CREATE DATABASE workoutlog;
\c workoutlog
\dt

#do the above, then run python -i model.py
#>>>db.create_all()
#then paste the functions below into the database



################################################################################
# TEMPLATES FOR TRIGGER FUNCTIONS #



CREATE OR REPLACE FUNCTION function_name() RETURNS trigger AS $$
    """DOCSTRING"""

    #do stuff


$$ LANGUAGE plpythonu;


CREATE TRIGGER function_name_trigger
    AFTER ***** ON "tablename"
    FOR EACH ROW
    EXECUTE PROCEDURE function_name();

# ***** can be INSERT, UPDATE, or DELETE
# tablename (if all lowercase) technically doesn't have to be in quotes,
# but it doesn't hurt anything and makes it stand out visually here in sublime


################################################################################
# THE FUNCTIONS THEMSELVES #

# The PL/Pythonu extension needs to be added to the database once before
# any functions can be written in Python

CREATE EXTENSION plpythonu;




CREATE OR REPLACE FUNCTION new_user_stats() RETURNS trigger AS $$
    """When a new user is entered into the users table, create a corresponding
       record in the user_stat_lists table, with the same user_id"""

    #get user_id of newly created user, as a string
    user_id_str = str(TD["new"]["user_id"])

    #create insert query string and execute it, creating the new record
    insert_query = ("INSERT INTO user_stat_lists " +
                    "(user_id, lifetime_meters, new_pr) VALUES (" +
                    user_id_str + ", 0, FALSE);")
    plpy.execute(insert_query)

$$ LANGUAGE plpythonu;


CREATE TRIGGER new_user_stats_trigger
    AFTER INSERT ON "users"
    FOR EACH ROW
    EXECUTE PROCEDURE new_user_stats();





CREATE OR REPLACE FUNCTION check_against_PRs() RETURNS trigger AS $$
    """Checks the new piece to see if it's one for which PR's are kept, and if
       so, compares it to the relevant PR, updating the PR if applicable."""

    #create useful variables
    new_piece_time = TD["new"]["total_time_seconds"]
    new_piece_dist = TD["new"]["total_meters"]
    special_times = {60: "one_min_pr_dist",
                     1800: "half_hour_pr_dist",
                     3600: "half_hour_pr_dist"}
    special_distances = {500: "half_k_pr_time",
                         1000: "one_k_pr_time",
                         2000: "two_k_pr_time",
                         5000: "five_k_pr_time",
                         6000: "six_k_pr_time",
                         10000: "ten_k_pr_time",
                         21097: "half_marathon_pr_time",
                         42195: "marathon_pr_time"}


    #get the user_id associated with the piece, as a string
    workout_result_id_str = str(TD["new"]["workout_result_id"])
    select_query = ("SELECT user_id FROM workout_results WHERE " +
                    "workout_result_id=" + workout_result_id_str + ";")
    user_id_str = str(plpy.execute(select_query)[0]["user_id"])

    #see if the new pices is one of the special time-pieces, and if so, update
    #the PR list as necessary
    if special_times.get(new_piece_time) is not None:
        #figure out which column was matched
        PR_column_name = special_times[new_piece_time]

        #get the old data in that column for comparison
        select_query = ("SELECT " + PR_column_name + " FROM user_stat_lists " +
                        "WHERE user_id=" + user_id_str + ";")
        old_PR_dist = plpy.execute(select_query)[0][PR_column_name]

        #if there was no data there, or the new result is better, update
        #the user_stat_lists table and set the new_pr flag (column) to true
        if (old_PR_dist is None) or (old_PR_dist < new_piece_dist):
            update_query = ("UPDATE user_stat_lists SET " +
                            PR_column_name + "=" + str(new_piece_dist) +
                            ", new_pr=TRUE WHERE user_id=" +
                            user_id_str + ";")
            plpy.execute(update_query)

    #see if the new pices is one of the special distance-pieces, and if so,
    #update the PR list as necessary
    if special_distances.get(new_piece_dist) is not None:
        #figure out which column was matched
        PR_column_name = special_distances[new_piece_dist]

        #get the old data in that column for comparison
        select_query = ("SELECT " + PR_column_name + " FROM user_stat_lists " +
                        "WHERE user_id=" + user_id_str + ";")
        old_PR_time = plpy.execute(select_query)[0][PR_column_name]

        #if there was no data there, or the new result is better, update
        #the user_stat_lists table and set the new_pr flag (column) to true
        if (old_PR_time is None) or (old_PR_time > new_piece_time):
            update_query = ("UPDATE user_stat_lists SET " +
                            PR_column_name + "=" + str(new_piece_time) +
                            ", new_pr=TRUE WHERE user_id=" +
                            user_id_str + ";")
            plpy.execute(update_query)

$$ LANGUAGE plpythonu;



CREATE TRIGGER check_against_PRs_trigger
    AFTER INSERT OR UPDATE ON "piece_results"
    FOR EACH ROW
    EXECUTE PROCEDURE check_against_PRs();




CREATE OR REPLACE FUNCTION add_piece_dist_to_totals() RETURNS trigger AS $$
    """Adds the meters rowed in the piece both to the total for the workout
       and to the lifetime total user stat."""

    #get the piece's meters
    new_piece_dist = TD["new"]["total_meters"]

    #get the workout_result_id and user_id associated with the piece, as strings
    workout_result_id_str = str(TD["new"]["workout_result_id"])
    select_query = ("SELECT user_id FROM workout_results WHERE " +
                    "workout_result_id=" + workout_result_id_str + ";")
    user_id_str = str(plpy.execute(select_query)[0]["user_id"])

    #get the current total distance for the workout and update it
    select_query = ("SELECT total_meters FROM workout_results WHERE " +
                    "workout_result_id=" + workout_result_id_str + ";")
    workout_total = plpy.execute(select_query)[0]["total_meters"]
    new_workout_total = workout_total + new_piece_dist
    update_query = ("UPDATE workout_results SET total_meters=" +
                    str(new_workout_total) + "WHERE user_id=" + user_id_str +
                    "AND workout_result_id=" + workout_result_id_str + ";")
    plpy.execute(update_query)

    #get the current lifetime total distance  and update it
    select_query = ("SELECT lifetime_meters FROM user_stat_lists " +
                    "WHERE user_id=" + user_id_str + ";")
    lifetime_total = plpy.execute(select_query)[0]["lifetime_meters"]
    new_lifetime_total = lifetime_total + new_piece_dist
    update_query = ("UPDATE user_stat_lists SET lifetime_meters=" +
                    str(new_lifetime_total) + "WHERE user_id=" + user_id_str + ";")
    plpy.execute(update_query)

$$ LANGUAGE plpythonu;



CREATE TRIGGER add_piece_dist_to_totals_trigger
    AFTER INSERT ON "piece_results"
    FOR EACH ROW
    EXECUTE PROCEDURE add_piece_dist_to_totals();






CREATE OR REPLACE FUNCTION change_piece_dist_on_totals() RETURNS trigger AS $$
    """When a piece is updated, reflects the change in meters rowed in the
       piece in both the total for the workout and the lifetime total user stat."""

    #get the piece's old and new meters
    old_piece_dist = TD["old"]["total_meters"]
    new_piece_dist = TD["new"]["total_meters"]

    #get the workout_result_id and user_id associated with the piece, as strings
    workout_result_id_str = str(TD["new"]["workout_result_id"])
    select_query = ("SELECT user_id FROM workout_results WHERE " +
                    "workout_result_id=" + workout_result_id_str + ";")
    user_id_str = str(plpy.execute(select_query)[0]["user_id"])

    #get the current total distance for the workout and update it
    select_query = ("SELECT total_meters FROM workout_results WHERE " +
                    "workout_result_id=" + workout_result_id_str + ";")
    workout_total = plpy.execute(select_query)[0]["total_meters"]
    new_workout_total = workout_total - old_piece_dist + new_piece_dist
    update_query = ("UPDATE workout_results SET total_meters=" +
                    str(new_workout_total) + "WHERE user_id=" + user_id_str +
                    "AND workout_result_id=" + workout_result_id_str + ";")
    plpy.execute(update_query)

    #get the current lifetime total distance  and update it
    select_query = ("SELECT lifetime_meters FROM user_stat_lists " +
                    "WHERE user_id=" + user_id_str + ";")
    lifetime_total = plpy.execute(select_query)[0]["lifetime_meters"]
    new_lifetime_total = lifetime_total - old_piece_dist + new_piece_dist
    update_query = ("UPDATE user_stat_lists SET lifetime_meters=" +
                    str(new_lifetime_total) + "WHERE user_id=" + user_id_str + ";")
    plpy.execute(update_query)

$$ LANGUAGE plpythonu;



CREATE TRIGGER change_piece_dist_on_totals_trigger
    AFTER UPDATE ON "piece_results"
    FOR EACH ROW
    EXECUTE PROCEDURE change_piece_dist_on_totals();




CREATE OR REPLACE FUNCTION delete_piece_dist_from_totals() RETURNS trigger AS $$
    """When a piece is deleted, reflects the loss in meters rowed in the piece
       in both the total for the workout and the lifetime total user stat."""

    #get the piece's meters
    piece_dist = TD["old"]["total_meters"]

    #get the workout_result_id and user_id associated with the piece, as strings
    workout_result_id_str = str(TD["old"]["workout_result_id"])
    select_query = ("SELECT user_id FROM workout_results WHERE " +
                    "workout_result_id=" + workout_result_id_str + ";")
    user_id_str = str(plpy.execute(select_query)[0]["user_id"])

    #get the current total distance for the workout and update it
    select_query = ("SELECT total_meters FROM workout_results WHERE " +
                    "workout_result_id=" + workout_result_id_str + ";")
    workout_total = plpy.execute(select_query)[0]["total_meters"]
    new_workout_total = workout_total - piece_dist
    update_query = ("UPDATE workout_results SET total_meters=" +
                    str(new_workout_total) + "WHERE user_id=" + user_id_str +
                    "AND workout_result_id=" + workout_result_id_str + ";")
    plpy.execute(update_query)

    #get the current lifetime total distance  and update it
    select_query = ("SELECT lifetime_meters FROM user_stat_lists " +
                    "WHERE user_id=" + user_id_str + ";")
    lifetime_total = plpy.execute(select_query)[0]["lifetime_meters"]
    new_lifetime_total = lifetime_total - piece_dist
    update_query = ("UPDATE user_stat_lists SET lifetime_meters=" +
                    str(new_lifetime_total) + "WHERE user_id=" + user_id_str + ";")
    plpy.execute(update_query)

$$ LANGUAGE plpythonu;



CREATE TRIGGER delete_piece_dist_from_totals_trigger
    AFTER DELETE ON "piece_results"
    FOR EACH ROW
    EXECUTE PROCEDURE delete_piece_dist_from_totals();








