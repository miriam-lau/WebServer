from app import app
import unittest


class AppTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    def tearDown(self):
        pass

    def test_set_username_cookie(self):
        result = self.app.post('/setcookie', data=dict(username='james'))
        self.assertEqual(result.status_code, 302)

    def test_render_homepage(self):
        result = self.app.get('/')
        self.assertEqual(result.status_code, 200)
        self.assertTrue("Welcome" in str(result.data))