import unittest
import logging
from unittest.mock import patch, mock_open, MagicMock, call
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)

# Create mock Calendar class
class MockCalendar(MagicMock):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._selection = None
        self.grid = MagicMock()
    
    def get_date(self):
        return self._selection
    
    def selection_set(self, date):
        self._selection = date

# Mock patch dictionary for babel
mock_babel = {
    'dates': MagicMock(),
    'core': MagicMock(),
    'localedata': MagicMock()
}

# Setup patches before importing PropertyApp
with patch('tkcalendar.Calendar', MockCalendar), \
     patch('babel.dates', mock_babel['dates']), \
     patch('babel.core', mock_babel['core']), \
     patch('babel.localedata', mock_babel['localedata']):
    from home_page import PropertyApp

@patch('tkcalendar.Calendar', MockCalendar)
@patch('babel.dates', mock_babel['dates'])
@patch('babel.core', mock_babel['core'])
@patch('babel.localedata', mock_babel['localedata'])
class TestHomePage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Set up any class-level patches
        cls.calendar_patcher = patch('tkcalendar.Calendar', MockCalendar)
        cls.calendar_patcher.start()

    @classmethod
    def tearDownClass(cls):
        cls.calendar_patcher.stop()

    def setUp(self):
        # Create context managers for patching
        self.json_patcher = patch('json.load')
        self.mock_json_load = self.json_patcher.start()
        
        # Mock data for testing
        self.mock_data = {
            "properties": [
                {
                    "date": "09-13-2024",
                    "invoice_no": [28],
                    "to_renter": "Hector Garcia",
                    "property_address1": "3175 Seminole Ave",
                    "total": "$1,368.00",  # Added total field
                    "line_items": [  # Added line items
                        ["Monthly Rent", "$1,312.50"],
                        ["Water", "$37.50"],
                        ["Internet", "$18.00"]
                    ]
                }
            ]
        }
        
        # Set up the mock to return our test data
        self.mock_json_load.return_value = self.mock_data
        
        # Create a context manager for patching open
        self.open_patcher = patch('builtins.open', new_callable=mock_open)
        self.mock_file = self.open_patcher.start()
        
        # Initialize the app
        self.app = PropertyApp()
        self.app.withdraw()  # Hide window during tests
        self.app.update()  # Ensure the app is fully loaded

    def tearDown(self):
        if hasattr(self, 'app') and self.app:
            try:
                # Get all after ids
                after_ids = self.app.tk.call('after', 'info')
                # Cancel all pending after events
                for after_id in after_ids:
                    self.app.after_cancel(after_id)
            except Exception:
                pass
            self.app.quit()
            self.app.destroy()
            self.app = None
            
        # Stop the patchers
        self.json_patcher.stop()
        self.open_patcher.stop()

    def test_home_page_loads(self):
        """Test if the home page loads successfully"""
        self.assertIsInstance(self.app, PropertyApp)
        self.assertEqual(self.app.title(), "GenInv")
        self.assertTrue(self.app.property_combo)
        self.assertTrue(self.app.tenant_combo)
        self.assertTrue(self.app.cal)

    @patch('os.path.exists')
    @patch('os.listdir')
    def test_property_selection_updates_tenants(self, mock_listdir, mock_exists):
        """Test if selecting a property updates the tenant list correctly"""
        # Mock the file system calls
        mock_exists.return_value = True
        mock_listdir.return_value = ["Hector Garcia", "Another Tenant"]
        
        # Simulate selecting a property
        self.app.property_combo.set("3175 Seminole Ave, SouthGate Property")
        self.app.on_property_select()
        
        # Check if tenant combo box is updated
        tenants = self.app.tenant_combo.cget("values")
        self.assertIn("Hector Garcia", tenants)
        self.assertNotEqual(tenants, ["Select a property first"])
        self.assertNotEqual(tenants, ["No tenants found"])

    @patch('home_page.fill_invoice')
    @patch('json.dump')
    @patch('os.path.exists')
    @patch('os.listdir')
    def test_submit_button_functionality(self, mock_listdir, mock_exists, mock_json_dump, mock_fill_invoice):
        """Test if the submit button works correctly"""
        # Mock the fill_invoice function to return True
        mock_fill_invoice.return_value = True
        
        # Mock the file system calls
        mock_exists.return_value = True
        mock_listdir.return_value = ["Hector Garcia"]
        
        # Setup test data
        test_property = "3175 Seminole Ave, SouthGate Property"
        test_tenant = "Hector Garcia"
        test_date = "9/13/24"

        # Set up the mock to return our test data for json.load
        with patch('json.load', return_value=self.mock_data):
            # Simulate selections
            self.app.property_combo.set(test_property)
            self.app.on_property_select()
            self.app.tenant_combo.set(test_tenant)
            self.app.cal._selection = test_date

            # Call submit
            self.app.submit()
            
            # Verify success message
            self.assertEqual(
                self.app.message_label.cget("text"),
                "Invoice 29 generated successfully!"  # Updated to include invoice number
            )

    @patch('json.dump')
    def test_set_default_tenant_success(self, mock_json_dump):
        """Test successful setting of default tenant"""
        test_property = "3306 Seminole Ave, Lynwood Property"
        test_tenant = "Maria Mercedes"

        # Setup and execute
        self.app.property_combo.set(test_property)
        self.app.tenant_combo.set(test_tenant)
        self.app.set_default_tenant()

        # Verify results
        self.assertEqual(self.app.default_tenants[test_property], test_tenant)
        self.assertEqual(self.app.message_label.cget("text"), "Default Tenant Set")
        self.assertEqual(self.app.message_label.cget("text_color"), "green")
        mock_json_dump.assert_called_once()

    def test_set_default_tenant_invalid_cases(self):
        """Test invalid cases for setting default tenant"""
        # Test no property selected
        self.app.property_combo.set("Select Property")
        self.app.set_default_tenant()
        self.assertEqual(
            self.app.message_label.cget("text"),
            "Please select a property before setting a default tenant."
        )
        self.assertEqual(
            self.app.message_label.cget("text_color"),
            "red"
        )

        # Test no tenant selected
        self.app.property_combo.set("3306 Seminole Ave, Lynwood Property")
        self.app.tenant_combo.set("Select Tenant")
        self.app.set_default_tenant()
        self.assertEqual(
            self.app.message_label.cget("text"),
            "Please select a valid tenant before setting it as the default."
        )
        self.assertEqual(
            self.app.message_label.cget("text_color"),
            "red"
        )

    @patch('os.path.exists')
    @patch('os.listdir')
    def test_default_tenant_persistence(self, mock_listdir, mock_exists):
        """Test if default tenant persists after setting and reselecting property"""
        test_property = "3306 Seminole Ave, Lynwood Property"
        test_tenant = "Maria Mercedes"

        # Mock the file system calls
        mock_exists.return_value = True
        mock_listdir.return_value = [test_tenant]

        # Set default tenant
        self.app.property_combo.set(test_property)
        self.app.on_property_select()
        self.app.tenant_combo.set(test_tenant)
        self.app.set_default_tenant()

        # Reselect property
        self.app.on_property_select()

        # Verify persistence
        self.assertEqual(self.app.tenant_combo.get(), test_tenant)

    @patch('home_page.fill_invoice')
    @patch('json.dump')
    @patch('os.path.exists')
    @patch('os.listdir')
    def test_date_update_in_properties_data(self, mock_listdir, mock_exists, mock_json_dump, mock_fill_invoice):
        """Test if the date gets updated correctly in properties_data.json"""
        # Mock the necessary functions
        mock_fill_invoice.return_value = True
        mock_exists.return_value = True
        mock_listdir.return_value = ["Hector Garcia"]
        
        # Setup test data
        test_property = "3175 Seminole Ave, SouthGate Property"
        test_tenant = "Hector Garcia"
        test_date = "12/01/24"
        
        # Set the values in the app
        self.app.property_combo.set(test_property)
        self.app.on_property_select()
        self.app.tenant_combo.set(test_tenant)
        self.app.cal._selection = test_date
        
        # Call submit
        self.app.submit()
        
        # Verify json.dump was called with updated date
        calls = mock_json_dump.call_args_list
        if calls:
            written_data = calls[0][0][0]  # Get the first argument of the first call
            expected_date = datetime.strptime(test_date, '%m/%d/%y').strftime('%m-%d-%Y')
            self.assertEqual(
                written_data['properties'][0]['date'],
                expected_date
            )
        else:
            self.fail("json.dump was not called")

    def test_display_message(self):
        """Test if messages are displayed correctly"""
        # Test error message
        self.app.display_message("Error message", "error")
        self.assertEqual(self.app.message_label.cget("text"), "Error message")
        self.assertEqual(self.app.message_label.cget("text_color"), "red")
        
        # Test success message
        self.app.display_message("Success message", "success")
        self.assertEqual(self.app.message_label.cget("text"), "Success message")
        self.assertEqual(self.app.message_label.cget("text_color"), "green")

if __name__ == '__main__':
    unittest.main()