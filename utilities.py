from re import match
from datetime import date



def days_til_HOCR(given_date=None):
    """Calculates the number of days between the given date and the next
       Head of the Charles. If no date is given, the current date is used.

       Note that a return value of 0 means it's HOCR Saturday, and a return
       value of -1 means it's HOCR Sunday."""

    #if no date was given, get today's date
    if not given_date:
        given_date = date.today()

    #get the given date's (or today's) year
    given_year = given_date.year

    #HOCR is the penultimate complete weekend in October
    #said differently, Sat of HOCR is always between 10/17 and 10/23
    #use that the figure out the date of given/this year's HOCR Sat
    oct_17_to_HOCR_sat = {0: 22, #if 10/17 is a Mon, HOCR starts the 22nd
                          1: 21, #if 10/17 is a Tues, HOCR starts the 21st
                          2: 20, #etc
                          3: 19,
                          4: 18,
                          5: 17,
                          6: 23}
    given_oct_17_weekday = date(given_year, 10, 17).weekday()
    given_HOCR_sat_date = oct_17_to_HOCR_sat[given_oct_17_weekday]
    given_HOCR_sat = date(given_year, 10, given_HOCR_sat_date)

    #compute the number of days between given date and HOCR Sat of that year
    num_days = (given_HOCR_sat - given_date).days

    #if it's positive (HOCR is yet to come), zero (it's HOCR Sat), or -1
    #(it's HOCR Sun), return it
    if num_days >= -1:
        return num_days

    #otherwise, figure out next year's HOCR Sat date, and calculate
    #based on that
    else:
        next_year = given_year + 1
        next_oct_17_weekday = date(next_year, 10, 17).weekday()
        next_HOCR_sat_date = oct_17_to_HOCR_sat[next_oct_17_weekday]
        next_HOCR_sat = date(next_year, 10, next_HOCR_sat_date)
        num_days = (next_HOCR_sat - given_date).days
        return num_days


def hms_string_to_seconds(hms_string):
    """Takes a string of the form hours:minutes:seconds and parses it,
       returning the number of seconds represented by the string."""

    #handle corner cases
    if not hms_string:
        return None
    if not match(r"^(\d*:[0-5]\d:[0-5]\d)|([0-5]?\d:[0-5]\d)|(:[0-5]\d)$",
                 hms_string):
        error_msg = ("expected string of the form [[h:]m]:s. Got " +
                     str(hms_string) + ".")
        raise ValueError(error_msg)

    #now that we know the string is of the right format, split it on ":",
    #figure out whether we have h:m:s, m:s, or :s, and do the appropriate math
    seconds = 0
    parts = hms_string.split(":")
    if len(parts) == 3: #h:m:s
        seconds += int(parts[0]) * 3600 #hours
        seconds += int(parts[1]) * 60 #minutes
        seconds += int(parts[2]) #seconds
    elif len(parts) == 2: #m:s
        seconds += int(parts[0]) * 60 #minutes
        seconds += int(parts[1]) #seconds
    else: #:s
        seconds += int(parts[0]) #seconds

    return seconds


def seconds_to_hms_string(sec):
    """Given a number of seconds, return a string in the form D:H:M:S."""

    #handle corner cases
    if not sec:
        return None
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

    #make strings of each time quantity, both padded with zeros and unpadded
    #(except days (which never gets padded) and seconds (which always gets
    #padded))
    days_str = str(days)
    hours_str = str(hours)
    hours_str_padded = "{hours:0>2d}".format(hours=hours)
    minutes_str = str(minutes)
    minutes_str_padded = "{minutes:0>2d}".format(minutes=minutes)
    seconds_str_padded = "{seconds:0>2d}".format(seconds=seconds)

    #create the string, avoiding leading zeros
    if days != 0:
        time_string = time_string + days_str + ":"
        time_string = time_string + hours_str_padded + ":"
        time_string = time_string + minutes_str_padded + ":"
        time_string = time_string + seconds_str_padded
    elif hours != 0:
        time_string = time_string + hours_str + ":"
        time_string = time_string + minutes_str_padded + ":"
        time_string = time_string + seconds_str_padded
    elif minutes != 0:
        time_string = time_string + minutes_str + ":"
        time_string = time_string + seconds_str_padded
    else:
        time_string = ":" + seconds_str_padded

    #return the string
    return time_string
