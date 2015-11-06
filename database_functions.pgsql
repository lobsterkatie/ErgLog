
/* When a new user is entered into the Users table, create a corresponding
   record in the User_stat_lists table, with the same user_id */

CREATE TRIGGER new_user_stats_trigger 
    AFTER INSERT ON "Users"
    FOR EACH ROW
    EXECUTE PROCEDURE new_user_stats();


CREATE OR REPLACE FUNCTION new_user_stats() RETURNS trigger AS $$
    BEGIN
        INSERT INTO "User_stat_lists" ("user_id", "lifetime_meters", "new_PR")
               VALUES (NEW.user_id, 0, FALSE);
        RETURN NULL;
        END;
$$ LANGUAGE plpgsql;


/* When a new record is created in the Piece_results table, check it against 
   PR's table (User_stat_lists, updating as necessary), and add the meters to 
   lifetime_meters and workout total meters */