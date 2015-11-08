# The PL/Pythonu extension needs to be added to the database once before
# any functions can be written in Python

CREATE EXTENSION plpythonu;




# When a new record is created in the Piece_results table, check it against
# PR's table (User_stat_lists), updating as necessary

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
    new_piece_is_PR = False
    
    #get the user_id associated with the piece, as a string
    workout_result_id_str = str(TD["new"]["workout_result_id"])
    select_query = ("SELECT user_id FROM workout_results WHERE " +
                    "workout_result_id=" + workout_result_id_str + ";")
    user_id_str = str(plpy.execute(select_query)[0]["user_id"])

    #see if the new pices is one of the special time-pieces
    if special_times.get(new_piece_time) is not None:
        #figure out which column was matched
        PR_column_name = special_times[new_piece_time]

        #get the old data in that column for comparison
        select_query = ("SELECT " + PR_column_name + " FROM user_stat_lists " +
                        "WHERE user_id=" + user_id_str + ";")
        query_result = plpy.execute(select_query)
        old_PR_dist = query_result[0][PR_column_name]

        #if there was no data there, or the new result is better, update 
        #the user_stat_lists table and set the new_pr flag (column) to true
        if (old_PR_dist is None) or (old_PR_dist < new_piece_dist):
            update_query = ("UPDATE user_stat_lists SET " +
                            PR_column_name + "=" + str(new_piece_dist) +
                            ", new_pr=TRUE WHERE user_id=" +
                            user_id_str + ";")
            plpy.execute(update_query)

    #reset the internal flag because it's just *conceiveable* that a piece
    #could be both a time *and* distance PR, or at least qualify to be so
    new_piece_is_PR = False

    #see if the new pices is one of the special distance-pieces
    if special_distances.get(new_piece_dist) is not None:
        #figure out which column was matched
        PR_column_name = special_distances[new_piece_dist]

        #get the old data in that column for comparison
        select_query = ("SELECT " + PR_column_name + " FROM user_stat_lists " +
                        "WHERE user_id=" + user_id_str + ";")
        query_result = plpy.execute(select_query)
        old_PR_time = query_result[0][PR_column_name]

        #if there was no data there, or the new result is better, update
        #the user_stat_lists table and set the new_pr flag (column) to true
        if (old_PR_time is None) or (old_PR_time > new_piece_time):
            update_query = ("UPDATE user_stat_lists SET " +
                            PR_column_name + "=" + str(new_piece_time) +
                            ", new_pr=TRUE WHERE user_id=" +
                            user_id_str + ";")
            plpy.execute(update_query)

        # #if there was no data there, the new pieces is automatically a PR
        # # raise Exception("Here! " + str(query_result[0][PR_column_name]))
        # if query_result[0][PR_column_name] is None:
        #     new_piece_is_PR = True

        # #otherwise, compare the old and new data
        # else:
        #     old_PR_time = plpy.execute(select_query)[0][PR_column_name]
        #     if old_PR_time > new_piece_time:
        #         new_piece_is_PR = True

        # #if the new result is a PR, put it in the table and set the new_pr
        # #flag (column) to true
        # if new_piece_is_PR:
        #     update_query = ("UPDATE user_stat_lists SET " +
        #                     PR_column_name + "=" + str(new_piece_time) +
        #                     ", new_pr=TRUE WHERE user_id=" +
        #                     user_id_str + ";")
        #     plpy.execute(update_query)

$$ LANGUAGE plpythonu;



CREATE TRIGGER check_against_PRs_trigger 
    AFTER INSERT OR UPDATE ON "piece_results"
    FOR EACH ROW
    EXECUTE PROCEDURE check_against_PRs();





# When a new record is created in the Piece_results table, add the meters to 
# lifetime_meters and workout total meters





