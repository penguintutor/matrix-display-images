import unittest
from message import Message
from datetime import date, time, datetime, timedelta


### Need to add tests for minutes_to_start etc.

# Test date functions in Message class 
# To keep the tests simple some of these may not work if run close to midnight (within 1 hour either side). That is not a failure of the message class, but a limitation of this test

class TestMessageClass(unittest.TestCase):

    # Only minimum entries (title and directory)
    # Should be valid for any date and time
    def test_create(self):
        data = {
            'title':"Test 1",
            'directory':"directory1"
            }
        test_message = Message(data)
        #print (test_message.to_string())
        self.assertEqual(test_message.title, data['title'])
        self.assertEqual(test_message.directory, data['directory'])
        self.assertTrue(test_message.date_valid())
        self.assertTrue(test_message.time_valid())
        self.assertTrue(test_message.date_time_valid())
        # Test minutes to start (0 as running) - unable to test minutes to end as unknown
        self.assertEqual(test_message.minutes_to_start(), 0)


    # Use start date and time 2 mins ago end time 2 mins after - must be run after 00:02:00 and before 23:58:00
    # Uses 2 digit dates
    def test_start_now(self):
        today = datetime.now()
        data = {
            'title':"Test 2",
            'directory':"directory1",
            'start_date':today.strftime("%m:%d"),
            'start_time':(today+timedelta(minutes=-2)).strftime("%H:%M"),
            'end_date':today.strftime("%m:%d"),
            'end_time':(today+timedelta(minutes=+2)).strftime("%H:%M")
            }
        test_message = Message(data)
        #print (test_message.to_string())
        self.assertEqual(test_message.title, data['title'])
        self.assertEqual(test_message.directory, data['directory'])
        self.assertTrue(test_message.date_valid())
        self.assertTrue(test_message.time_valid())
        self.assertTrue(test_message.date_time_valid())
        self.assertEqual(test_message.minutes_to_start(), 0)
        self.assertAlmostEqual(test_message.minutes_to_end(), 2, delta=1)
   

    # Use start date and end in future but current time so date time should not be met
    # Uses 2 digit dates
    def test_future_date_1(self):
        today = datetime.now()
        data = {
            'title':"Test 3",
            'directory':"directory1",
            'start_date':(today+timedelta(days=+1)).strftime("%m:%d"),
            'start_time':(today+timedelta(hours=-1)).strftime("%H:%M"),
            'end_date':(today+timedelta(days=+2)).strftime("%m:%d"),
            'end_time':(today+timedelta(hours=+1)).strftime("%H:%M")
            }
        test_message = Message(data)
        #print (test_message.to_string())
        self.assertEqual(test_message.title, data['title'])
        self.assertEqual(test_message.directory, data['directory'])
        self.assertFalse(test_message.date_valid())
        self.assertTrue(test_message.time_valid())
        self.assertFalse(test_message.date_time_valid())
        self.assertGreater(test_message.minutes_to_start(), 1220)
        self.assertLessEqual(test_message.minutes_to_start(), 1440)
        self.assertEqual(test_message.minutes_to_end(), 0)
        

    # Test valid time on a valid date where time is not yet reached (overnight only)
    # Uses 4 digit dates
    def test_not_time1(self):
        today = datetime.now()
        data = {
            'title':"Test 4",
            'directory':"directory1",
            'start_date':(today+timedelta(days=-1)).strftime("%Y:%m:%d"),
            'start_time':(today+timedelta(hours=+1)).strftime("%H:%M"),
            'end_date':(today+timedelta(days=+2)).strftime("%Y:%m:%d"),
            'end_time':(today+timedelta(hours=-1)).strftime("%H:%M")
            }
        test_message = Message(data)
        #print (test_message.to_string())
        self.assertEqual(test_message.title, data['title'])
        self.assertEqual(test_message.directory, data['directory'])
        self.assertTrue(test_message.date_valid())
        self.assertFalse(test_message.time_valid())
        self.assertFalse(test_message.date_time_valid())
        self.assertAlmostEqual(test_message.minutes_to_start(), 60, delta=5)
        self.assertEqual(test_message.minutes_to_end(), 0)
        
     # Test valid time on a valid date where time is not yet reached (not overnight)
    # Uses 4 digit dates
    def test_not_time2(self):
        today = datetime.now()
        data = {
            'title':"Test 5",
            'directory':"directory1",
            'start_date':(today+timedelta(days=-30)).strftime("%Y:%m:%d"),
            'start_time':(today+timedelta(hours=+1)).strftime("%H:%M"),
            'end_date':(today+timedelta(days=+30)).strftime("%Y:%m:%d"),
            'end_time':(today+timedelta(hours=+2)).strftime("%H:%M")
            }
        test_message = Message(data)
        #print (test_message.to_string())
        self.assertEqual(test_message.title, data['title'])
        self.assertEqual(test_message.directory, data['directory'])
        self.assertTrue(test_message.date_valid())
        self.assertFalse(test_message.time_valid())
        self.assertFalse(test_message.date_time_valid())
        self.assertAlmostEqual(test_message.minutes_to_start(), 60, delta=5)
        self.assertEqual(test_message.minutes_to_end(), 0)

    # Use start date today and end day future but time passed (turn off overnight)
    def test_future_date_2(self):
        today = datetime.now()
        data = {
            'title':"Test 6",
            'directory':"directory1",
            'start_date':(today+timedelta(days=0)).strftime("%Y:%m:%d"),
            'start_time':(today+timedelta(hours=-2)).strftime("%H:%M"),
            'end_date':(today+timedelta(days=+2)).strftime("%Y:%m:%d"),
            'end_time':(today+timedelta(hours=-1)).strftime("%H:%M")
            }
        test_message = Message(data)
        #print (test_message.to_string())
        self.assertEqual(test_message.title, data['title'])
        self.assertEqual(test_message.directory, data['directory'])
        self.assertTrue(test_message.date_valid())
        self.assertFalse(test_message.time_valid())
        self.assertFalse(test_message.date_time_valid())
        self.assertGreater(test_message.minutes_to_start(), 120)
        self.assertLessEqual(test_message.minutes_to_start(), 1440)
        self.assertGreater(test_message.minutes_to_start(), test_message.minutes_to_end())

    # Date already past
    def test_past_date_1(self):
        today = datetime.now()
        data = {
            'title':"Test 7",
            'directory':"directory1",
            'start_date':(today+timedelta(days=-31)).strftime("%m:%d"),
            'start_time':(today+timedelta(hours=-2)).strftime("%H:%M"),
            'end_date':(today+timedelta(days=-1)).strftime("%m:%d"),
            'end_time':(today+timedelta(hours=-4)).strftime("%H:%M")
            }
        test_message = Message(data)
        #print (test_message.to_string())
        self.assertEqual(test_message.title, data['title'])
        self.assertEqual(test_message.directory, data['directory'])
        self.assertFalse(test_message.date_valid())
        self.assertTrue(test_message.time_valid())
        self.assertFalse(test_message.date_time_valid())
        self.assertEqual(test_message.minutes_to_start(), 1440)
        self.assertEqual(test_message.minutes_to_end(), 0)


    # Use start date and time 2 mins ago end time 2 mins after - must be run after 00:02:00 and before 23:58:00
    # Uses 2 digit dates
    def test_with_pir(self):
        today = datetime.now()
        data = {
            'title':"Test 8",
            'directory':"directory1",
            'start_date':today.strftime("%m:%d"),
            'start_time':(today+timedelta(minutes=-2)).strftime("%H:%M"),
            'end_date':today.strftime("%m:%d"),
            'end_time':(today+timedelta(minutes=+2)).strftime("%H:%M"),
            'prefix':"normal",
            'pir_enable':"true",
            'pir_prefix':"pir",
            'pir_ontime':"10"
            }
        test_message = Message(data)
        #print (test_message.to_string())
        self.assertEqual(test_message.title, data['title'])
        self.assertEqual(test_message.directory, data['directory'])
        self.assertTrue(test_message.date_valid())
        self.assertTrue(test_message.time_valid())
        self.assertTrue(test_message.date_time_valid())
        self.assertEqual(test_message.minutes_to_start(), 0)
        self.assertAlmostEqual(test_message.minutes_to_end(), 2, delta=1)
        self.assertEqual(test_message.pir_ontime, 10)       # Check it's an int value
        self.assertEqual(test_message.prefix, data['prefix'])
        self.assertEqual(test_message.pir_prefix, data['pir_prefix'])
   
    # Active message - due to finish just before midnight - check minutes to end time < end day
    def test_active_message_change(self):
        today = datetime.now()
        data = {
            'title':"Test 9",
            'directory':"directory1",
            'start_date':today.strftime("%m:%d"),
            'start_time':(today+timedelta(minutes=-2)).strftime("%H:%M"),
            'end_date':today.strftime("%m:%d"),
            'end_time':"23:58:00"
            }
        test_message = Message(data)
        # difference between now and end_time
        today_end_time = datetime.now()
        today_end_time = today_end_time.replace(hour=23, minute=58, second=0)
        seconds_to_end = (today_end_time - today).total_seconds()
        #print (test_message.to_string())
        self.assertEqual(test_message.title, data['title'])
        self.assertEqual(test_message.directory, data['directory'])
        self.assertTrue(test_message.date_valid())
        self.assertTrue(test_message.time_valid())
        self.assertTrue(test_message.date_time_valid())
        self.assertEqual(test_message.minutes_to_start(), 0)
        self.assertLessEqual(test_message.minutes_to_end(), (seconds_to_end / 60)+1)

if __name__ == '__main__':
    unittest.main()
