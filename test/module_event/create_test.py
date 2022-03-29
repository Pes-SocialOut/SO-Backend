# -*- coding: utf-8 -*-
import pytest
from werkzeug.test import Client
from app import app

class TestCreateEventSuite:

    # Individual tests

    # Fixtures

    # @pytest.fixture
    # def set_event(event):
    #     yield
    #     try:
    #         event.delete()
    #     except:
    #         return "error in setting event!", 400
    
    #Attribute validation tests:

   #testing the date restriction: dataStarted <= dataEnd
    def test_endDate_before_startDate(self):
        print("running test endDate before startDate...")
        c = Client(app)
        args = {
            "name": "endDate_before_startDate",
            "description": "test",
            "date_started": "2022-03-29 11:03:08",
            "date_end": "2022-05-29 12:00:00",
            "user_creator": "52a43b27-46e3-47c1-8d56-7f01cbba5121",
            "longitud": 1.00,
            "latitude": 41.00,
            "max_participants": 5
        }
        response = c.post("/events",data=args, content_type="application/json")
        print(type(response))
        #assert response.status == 400
        #assert response.data == ({"error_message": "date Started is bigger than date End, that's not possible!"})

    # #testing vulgar words API works with username
    # def test_validate_vulgar_name():
    #     print("running test validate vulgar name...")
    #     pass

    # #testing vulgar words API works with description            
    # def test_validate_vulgar_description():
    #     print("running test validate description name...")
    #     pass

 

    # #testing the date restriction dataStarted >= now
    # def test_startDate_bigger_now():
    #     print("running test startDate bigger now...")
    #     pass

    # #testing the longitude and latitude restrictions
    # def test_longitude_and_latitude_restrictions():
    #     print("running test longitude and latitude restrictions...")
    #     pass

    # #testing the max characters restriction of the username
    # def test_username_too_long():
    #     print("running test username too long...")
    #     pass

    # #testing the max characters restriction of the username
    # def test_description_too_long():
    #     print("running test description too long...")
    #     pass

    # #Other tests

    # #testing a succesful creation of an event
    # def test_succesful_event_creation():
    #     print("running test succesful event creation...")
    #     pass

    # #testing a database throw (should we do one for user and for null?)
    # def test_database_error_throw():
    #     print("running test database error throw...")
    #     pass



