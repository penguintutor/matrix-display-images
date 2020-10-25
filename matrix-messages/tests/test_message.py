import unittest
from message import Message
from datetime import date, time, datetime, timedelta


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
   

    # Use start date and in future but current time so date time should not be met
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



if __name__ == '__main__':
    unittest.main()
