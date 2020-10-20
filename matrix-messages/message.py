from datetime import date;

// Data is passed as a dictionary of key value pairs
class Message:
    def __init__(self, data):
        today = date.today()
        self.title = data['title']

        if (not 'start_date' in data.keys()):
            # If no start date then start at begining of year (1st jan current year)
            self.start_date = date(today.year(), 1, 1)
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
            self.end_date = date(today.year(), 12, 31)
        else:
            # We have a date so parse
            end_date_elements = data['end_date'].split(':')
            # If 3 elements then must include year
            if (len(end_date_elements) > 2) :
                year = int(end_date_elements[0])
                month = int(end_date_elements[1])
                day = int(end_date_elements[2])
                self.end_date = date (year, month, day)
        if (len(start_date_elements == 2) and len(end_date_elements == 2)):
            # if we have mm:dd for start and end then need to work out whether this is 
            # start and end this year (end > start)
            # start this year and end next year (start > end)
            # check month first - then if same check date
            start_month = int(start_date_elements[0])
            start_day = int(start_date_elements[1])
            end_month = int(end_date_elements[0])
            end_day = int(end_date_elements[1])
            # start_year is always this year - end may be next year
            start_year = today.year()
            if (end_month > start_month):
                end_year = today.year()
            elif (start_month > end_month):
                end_year = today.year()+1
            # start month and year is same
            elif (end_day > start_day):
                end_year = today.year()
            else:
                end_year = today.year()+1
            start_date = date(start_year, start_month, start_day)
            end_date = date(end_year, end_month, end_day)
        # Now must have start and end date
        
        # If start time and end time then save
        if ('start-time' in data.keys() and 'end-time' in data.keys()):
            time_elements = data['start-time']
            self.start-time = (*time_elements)
            time_elements = data['end-time']
            self.end-time = (*time_elements)
            
        # Directory is required
        self.directory = data['directory']
        
        if ('prefix' in data.keys()):
            self.prefix = data['prefix']
        else:
            self.prefix = ""
            
        if ('pir-enable' in data.keys() and 'pir-prefix' in data.keys() and data['pir-enable'] == True):
            self.pir-enable = True
            self.pir-prefix = data['pir-prefix']
        else:
            self.pir-enable = False
            
        # Count is kept as a string for config file - not processed 
        if ('count' in data.keys()) :
            self.count = data['count']
        else:
            self.count = ""
           
          
    # returns true if in current date range
    def date_valid ():
        if today.date
            