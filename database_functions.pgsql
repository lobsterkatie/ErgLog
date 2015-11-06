
/* When a new user is entered into the Users table, create a corresponding
   record in the User_stat_lists table, with the same user_id */

CREATE OR REPLACE FUNCTION new_user_stats() RETURNS trigger AS $$
    BEGIN
        INSERT INTO "User_stat_lists" ("user_id", "lifetime_meters", "new_PR")
               VALUES (NEW.user_id, 0, FALSE);
        RETURN NULL;
        END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER new_user_stats_trigger 
    AFTER INSERT ON "Users"
    FOR EACH ROW
    EXECUTE PROCEDURE new_user_stats();


/* When a new record is created in the Piece_results table, check it against 
   PR's table (User_stat_lists), updating as necessary */

CREATE OR REPLACE FUNCTION check_against_PRs() RETURNS trigger AS $$
    """Checks the new piece to see if it's one for which PR's are kept, and if
       so, compares it to the relevant PR, updating the PR if applicable."""

    new_piece_time = NEW.total_time_seconds
    new_piece_dist = NEW.total_meters
    special_times = {60: "one_min_PR_dist", 
                     1800: "half_hour_PR_dist", 
                     3600: "half_hour_PR_dist"}
    special_dists = {500: "half_K_PR_time", 
                     1000: "one_K_PR_time", 
                     2000: "two_K_PR_time", 
                     5000: "five_K_PR_time", 
                     6000: "six_K_PR_time", 
                     10000: "ten_K_PR_time", 
                     21097: "half_marathon_PR_time", 
                     42195: "marathon_PR_time"}
    
    #get the user_id associated with the piece, as a string
    workout_result_id_str = str(NEW.workout_result_id)
    select_query = ("SELECT user_id FROM Workout_results WHERE " +
                    "workout_result_id=" + workout_result_id_str + ";")
    user_id_str = str(plpy.execute(select_query))

    #check to see if the new piece is one of the special ones, and if so,
    #compare it to the old PR and update if necessary
    if special_times.get(new_piece_time) is not None:
        #figure out which column was matched
        PR_column_name = special_times[new_piece_time]

        #get the old data in that column for comparison
        select_query = ("SELECT " + PR_column_name + " FROM User_stat_lists " +
                        "WHERE user_id=" + user_id_str + ";")
        old_PR_dist = plpy.execute(select_query)

        #see if the new result is better, and if so, replace it and set the
        #new_PR flag (column) to true
        if old_PR_dist < new_piece_dist:
            update_query = ("UPDATE User_stat_lists SET " +
                            PR_column_name + "=" + str(new_piece_dist) +
                            ", new_PR=TRUE WHERE user_id=" +
                            user_id_str + ";")
            plpy.execute(update_query)

    #IF THE ABOVE WORKS, DO THE SAME FOR SPECIAL DISTANCES

    

    

$$ LANGUAGE plpythonu;



CREATE TRIGGER check_against_PRs_trigger 
    AFTER INSERT ON "Piece_results"
    FOR EACH ROW
    EXECUTE PROCEDURE check_against_PRs();










/* When a new record is created in the Piece_results table, add the meters to 
   lifetime_meters and workout total meters */