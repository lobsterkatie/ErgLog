/* When a new user is entered into the Users table, create a corresponding
   record in the user_stat_lists table, with the same user_id */

CREATE OR REPLACE FUNCTION new_user_stats() RETURNS trigger AS $$
    BEGIN
        INSERT INTO user_stat_lists (user_id, lifetime_meters, new_pr)
               VALUES (NEW.user_id, 0, FALSE);
        RETURN NULL;
        END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER new_user_stats_trigger 
    AFTER INSERT ON users
    FOR EACH ROW
    EXECUTE PROCEDURE new_user_stats();

