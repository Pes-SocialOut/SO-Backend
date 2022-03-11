import unittest

class LoginTestSuite(unittest.TestCase):

    def setUp(self):
        # Hacer todo lo común de antes de los tests de esta suite, la función debe llamarse setUp y se ejecuta antes de cada test
        # Por ej:
            # Limpiar BD de testing
        print()
        print("setup...")

    def tearDown(self):
        # Hacer todo lo común de después de los tests de esta suite, la función debe llamarse tearDown y se ejecuta después de cada test
        # Por ej:
            # Cerrar conexiones, etc
        print("tearDown...")

    # Los tests individuales deben empezar con el prefijo test_

    def test_wrong_username_and_password(self):
        print("running test wrongUserPass...")
        response_code = 300
        self.assertEqual(300, response_code)
    
    def test_that_throws_an_error(self):
        print("running test throwing error")
        a = ['item1', 'item2']
        with self.assertRaises(Exception):
            a.split(2)

if __name__ == '__main__':
    unittest.main()