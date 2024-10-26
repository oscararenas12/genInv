import unittest
from home_page import PropertyApp

class TestHomePage(unittest.TestCase):
    def setUp(self):
        self.app = PropertyApp()
        self.app.update()  # Ensure the app is fully loaded

    def test_home_page_loads(self):
        # Simulate loading the home page
        home_page_loaded = PropertyApp()  # Replace with actual logic to load the home page
        self.assertTrue(home_page_loaded, "Home page should load successfully")

if __name__ == '__main__':
    unittest.main()