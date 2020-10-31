from datetime import date, time, datetime, timedelta

# Data is passed as a dictionary of key value pairs
class Message:
    def __init__(self, data):
        today = datetime.now()
        self.title = data['title']
        self.start_date = None
        self.end_date = None
        self.delay = ""
        self.display = True

        if (not 'start_date' in data.keys()):
            # If no start date then start at begining of year (1st jan current year)
            self.start_date = date(today.year, 1, 1)
        else:
            # We have a date so parse
            start_date_elements = data['start_date'].split(':')
            # If 3 elements then must include year
            if (len(start_date_elements) > 2) :
                year = int(start_date_elements[0])
                month = int(start_date_elements[1])
                day = int(start_date_elements[2])
                self.start_date = date (year, month, day)
            # If 2 elements (min) then need to work out whether this year or next (whether start is before end or not)
            # Do this after working out end date
        if (not 'end_date' in data.keys()):
            self.end_date = date(today.year, 12, 31)
        else:
            # We have a date so parse
            end_date_elements = data['end_date'].split(':')
            # If 3 elements then must include year
            if (len(end_date_elements) > 2) :
                year = int(end_date_elements[0])
                month = int(end_date_elements[1])
                day = int(end_date_elements[2])
                self.end_date = date (year, month, day)
        # Do not allow start_date and no end_date / vice versa
        if ((self.start_date == None and not self.end_date == None) or (self.start_date == None and not self.end_date == None)) :
            print ("Warning invalid entry - both start and end dates required %s", self.title)
            return
        if (self.start_date == None or self.end_date == None):
            if (len(start_date_elements) == 2 and len(end_date_elements) == 2):
                # if we have mm:dd for start and end then need to work out whether this is
                # start and end this year (end > start)
                # start this year and end next year (start > end)
                # check month first - then if same check date
                start_month = int(start_date_elements[0])
                start_day = int(start_date_elements[1])
                end_month = int(end_date_elements[0])
                end_day = int(end_date_elements[1])
                # start_year is always this year - end may be next year
                start_year = today.year
                if (end_month > start_month):
                    end_year = today.year
                elif (start_month > end_month):
                    end_year = today.year+1
                # start month and year is same
                elif (end_day == start_day):
                    end_year = today.year
                else:
                    end_year = today.year+1
                self.start_date = date(start_year, start_month, start_day)
                self.end_date = date(end_year, end_month, end_day)
            else :
                print ("Invalid start or end date")
                exit (0)
        # Now must have start and end date

        # If start time and end time then save
        if ('start_time' in data.keys() and 'end_time' in data.keys()):
            time_elements = data['start_time'].split(':')
            self.start_time = time(int(time_elements[0]), int(time_elements[1]),int(time_elements[1]))
            time_elements = data['end_time'].split(':')
            self.end_time = time(int(time_elements[0]), int(time_elements[1]),int(time_elements[1]))
        # Otherwise start time and end time are both 00:00 - start time should take precedent 
        else:
            self.start_time = time()
            self.end_time = time()
        


        # Directory is required
        self.directory = data['directory']

        if ('prefix' in data.keys()):
            self.prefix = data['prefix']
        else:
            self.prefix = ""

        if ('pir_enable' in data.keys() and 'pir_prefix' in data.keys() and data['pir_enable'] == "true"):
            self.pir_enable = True
            self.pir_prefix = data['pir_prefix']
        else:
            self.pir_enable = False

        # Count is kept as a string for config file - not processed
        if ('count' in data.keys()) :
            self.count = data['count']
        else:
            self.count = ""
            
        if ('delay' in data.keys()) :
            self.delay = data['delay']
        else :
            self.delay = ""


    # Return number of minutes to start (if already started then 0, if more than 24 hours then 1440)
    def minutes_to_start (self):
        today = datetime.now()
        # If current active
        if self.date_time_valid():
            return 0
        # If today but in future
        if (self.date_valid () and self.start_time > today.time()):
            time_in_sec =  (datetime.combine(today.date(),self.start_time) - today).total_seconds()
            return time_in_sec // 60    # return as minutes (ignore any remainder)
        # If tomorrow 
        if ((today + timedelta(days=1)).date() >= self.start_date):
            self.start_date == (today + timedelta(days=1)).date()
            seconds_future = (datetime.combine(today.date(), self.start_time) + timedelta(days=1) - today).total_seconds()
            minutes_future = seconds_future // 60
            if (minutes_future < 1440):
                return minutes_future
        # Reach here then it's at least 24 hours until start
        return 1440

    # Return minutes to end - if already started - if not return 0
    def minutes_to_end (self):
        today = datetime.now()
        if (not self.date_time_valid()) :
            return 0
        # if ends today (end time is later than current time)
        if (self.end_time > today.time()) :
            seconds_future = (datetime.combine(today.date(), self.end_time) - today).total_seconds()
        else:
            # If not then ends tomorrow
            # seconds until end of today
            seconds_future_today = (datetime.combine(today.date(), time(23,59,59)) - today).total_seconds() 
            #print ("time in seconds today is "+str(seconds_future_today))
            # plus seconds to time tommorow
            seconds_future = seconds_future_today + (datetime.combine(today.date(), time(0,0,0)) - datetime.combine(today.date(), self.end_time)).seconds
        #print ("time in seconds "+str(seconds_future))
        minutes_future = seconds_future // 60
        #print ("time in seconds is "+str(minutes_future))
        if (minutes_future < 1440):
            return minutes_future
        return 1440


    # returns true if in current date valid
    # Does not check time only day
    def date_valid (self):
        today = datetime.now()
        # Still run on end date so <=
        if (today.date() >= self.start_date and today.date() <= self.end_date):
            return True
        else :
            return False

    # returns true if in current time, otherwise false
    # Does not check day, only time
    def time_valid (self):
        today = datetime.now()
        today_time = today.time()
        # If start and end time are same then valid at all times
        if (self.start_time == self.end_time):
            return True
        # if start early and finish later same day
        if (self.end_time > self.start_time and today_time > self.start_time and today_time < self.end_time):
            return True
        # if start_late and then go to end_time following day
        elif (self.end_time < self.start_time and (today_time > self.start_time or today_time < self.end_time)):
            return True
        return False

    # Checks date and time
    def date_time_valid (self):
        if (self.date_valid() and self.time_valid()):
            return True
        return False


    # Gives a multiine summary of object
    def to_string (self):
        return_string = "Object summary\n"
        return_string += "title=" + self.title + "\n"
        return_string += "start date=" + self.start_date.strftime("%Y:%m:%d") + "\n"
        return_string += "start time=" + self.start_time.strftime("%H:%M:%S") + "\n"
        return_string += "end date=" + self.end_date.strftime("%Y:%m:%d") + "\n"
        return_string += "end time=" + self.end_time.strftime("%H:%M:%S") + "\n"
        return return_string



