# Easy way of quickly running tests for the different scripts in python (to allow better imports).

# Just swap out X in
# from X import test
# And use that to test different scripts. 
if __name__ == "__main__":
    from make_weekly_meetings.make_weekly_calendars import test
    test()