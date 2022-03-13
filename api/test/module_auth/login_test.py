# -*- coding: utf-8 -*-
import pytest

class TestLoginSuite:

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
        print()
        print("setup method...")

    def teardown_method(self, test_method):
        # Hacer todo lo comun de despues de los tests de esta suite, se ejecuta despues de cada test
        # Por ej:
            # Cerrar conexiones, etc
        print("teardown method...")

    # Los tests individuales deben empezar con el prefijo test_

    def test_wrong_username_and_password(self):
        print("running test wrongUserPass...")
        response_code = 300
        assert 300 == response_code

    def test_that_throws_an_error(self):
        print("running test throwing error")
        a = ['item1', 'item2']
        with pytest.raises(Exception):
            a.split(2)
