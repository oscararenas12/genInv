import unittest
import logging
from home_page import PropertyApp
import json
from unittest.mock import patch, mock_open, MagicMock

# Configure logging
logging.basicConfig(level=logging.INFO)

class TestHomePage(unittest.TestCase):
    def setUp(self):
        self.app = PropertyApp()
        self.app.withdraw()  # Hide window during tests
        self.app.update()  # Ensure the app is fully loaded

    def tearDown(self):
        if self.app:
            self.app.after_cancel('check_dpi_scaling')  # Cancel any pending after events
            self.app.after_cancel('update')
            self.app.quit()
            self.app.destroy()
            self.app = None

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

    @patch('logging.info')
    def test_submit_button_functionality(self, mock_logging):
        """Test if the submit button captures and logs the correct information"""
        # Setup test data
        test_property = "3175 Seminole Ave, SouthGate Property"
        test_tenant = "Hector Garcia"
        test_date = "9/13/24"

        # Simulate selections
        self.app.property_combo.set(test_property)
        self.app.on_property_select()
        self.app.tenant_combo.set(test_tenant)
        self.app.cal.selection_set(test_date)

        # Test submit function
        self.app.submit()

        # Verify logging calls
        expected_calls = [
            unittest.mock.call(f"Property: {test_property}"),
            unittest.mock.call(f"Tenant: {test_tenant}"),
            unittest.mock.call(f"Billing Date: {test_date}")
        ]
        mock_logging.assert_has_calls(expected_calls)

    @patch('json.dump')
    @patch('builtins.open', mock_open())
    def test_set_default_tenant_success(self, mock_json_dump):
        """Test successful setting of default tenant"""
        test_property = "3306 Seminole Ave, Lynwood Property"
        test_tenant = "Maria Mercedes"

        # Setup and execute
        self.app.property_combo.set(test_property)
        self.app.on_property_select()
        self.app.tenant_combo.set(test_tenant)
        self.app.set_default_tenant()

        # Verify results
        self.assertEqual(self.app.default_tenants[test_property], test_tenant)
        self.assertEqual(self.app.message_label.cget("text"), "Default Tenant Set")
        self.assertEqual(self.app.message_label.cget("text_color"), "green")
        mock_json_dump.assert_called_once()

    @patch('json.dump')
    @patch('builtins.open', mock_open())
    def test_set_default_tenant_invalid_cases(self, mock_json_dump):
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
        self.app.on_property_select()
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

        # Test with "No tenants found"
        self.app.tenant_combo.set("No tenants found")
        self.app.set_default_tenant()
        self.assertEqual(
            self.app.message_label.cget("text"),
            "Please select a valid tenant before setting it as the default."
        )
        self.assertEqual(
            self.app.message_label.cget("text_color"),
            "red"
        )

    @patch('json.dump')
    @patch('builtins.open', mock_open())
    def test_default_tenant_persistence(self, mock_json_dump):
        """Test if default tenant persists after setting and reselecting property"""
        test_property = "3306 Seminole Ave, Lynwood Property"
        test_tenant = "Maria Mercedes"

        # Mock tenant folders
        with patch('os.path.exists') as mock_exists, \
             patch('os.listdir') as mock_listdir:
            
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

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_load_default_tenants(self, mock_json_load, mock_file):
        """Test loading default tenants from file"""
        test_data = {"3306 Seminole Ave, Lynwood Property": "Maria Mercedes"}
        mock_json_load.return_value = test_data

        # Test successful load
        loaded_tenants = self.app.load_default_tenants()
        self.assertEqual(loaded_tenants, test_data)
        mock_file.assert_called_once_with('default_tenants.json', 'r')

        # Test file not found scenario
        mock_file.side_effect = FileNotFoundError
        loaded_tenants = self.app.load_default_tenants()
        self.assertEqual(loaded_tenants, {})

if __name__ == '__main__':
    unittest.main()