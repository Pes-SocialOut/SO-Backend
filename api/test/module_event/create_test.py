# -*- coding: utf-8 -*-
import pytest
from app.module_event.controllers import create_event


class TestCreateEventSuite:
        
    @classmethod
    def setup_class(cls):
        # Hacer lo comun que no hace falta reiniciar tras cada test. Se ejecuta una vez antes de empezar ningun test.
        print("setup class...")

    @classmethod
    def teardown_class(cls):
        # Limpiar el entorno. Se ejecuta una vez despues de acabar todos los tests.
        print("teardown class...")

    def setup_method(self, test_method):
        # Hacer todo lo comun de antes de los tests de esta suite, se ejecuta antes de cada test
        # Por ej:
            # Limpiar BD de testing
        print("setup method...")

    def teardown_method(self, test_method):
        # Hacer todo lo comun de despues de los tests de esta suite, se ejecuta despues de cada test
        # Por ej:
            # Cerrar conexiones, etc
        print("teardown method...")


    # Individual tests

    #Attribute validation tests:

    #testing vulgar words API works with username
    def test_validate_vulgar_name():
        print("running test validate vulgar name...")

    #testing vulgar words API works with description            
    def test_validate_vulgar_description():
        print("running test validate description name...")

    #testing the date restriction: dataStarted <= dataEnd
    def test_endDate_before_startDate():
        print("running test endDate before startDate...")
    
    #testing the date restriction dataStarted >= now
    def test_startDate_bigger_now():
        print("running test startDate bigger now...")
    
    #testing the longitude and latitude restrictions
    def test_longitude_and_latitude_restrictions():
        print("running test longitude and latitude restrictions...")
    
    #testing the max characters restriction of the username
    def test_username_too_long():
        print("running test username too long...")
    
    #testing the max characters restriction of the username
    def test_description_too_long():
        print("running test description too long...")
    
    
    #Other tests

    #testing a succesful creation of an event
    def test_succesful_event_creation():
        print("running test succesful event creation...")

    #testing a database throw (should we do one for user and for null?)
    def test_database_error_throw():
        print("running test database error throw...")




