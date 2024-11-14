import unittest
import logging
from home_page import PropertyApp
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)

class TestHomePage(unittest.TestCase):
    def setUp(self):
        self.app = PropertyApp()
        self.app.update()  # Ensure the app is fully loaded

    def test_home_page_loads(self):
        # Simulate loading the home page
        home_page_loaded = PropertyApp()
        self.assertTrue(home_page_loaded, "Home page should load successfully")


    def test_property_selection_updates_tenants(self):
        # Simulate selecting a property
        self.app.property_combo.set("3175 Seminole Ave, SouthGate Property")
        self.app.on_property_select()
        
        # Check if tenant combo box is updated
        tenants = self.app.tenant_combo.cget("values")
        self.assertNotEqual(tenants, ["Select a property first"], "Tenant list should be updated after property selection")
        self.assertNotEqual(tenants, ["No tenants found"], "Tenant list should not be empty if tenants exist")

    def test_submit_button_functionality(self):
        # Simulate selecting a property and tenant
        self.app.property_combo.set("3175 Seminole Ave, SouthGate Property")
        self.app.on_property_select()
        self.app.tenant_combo.set("Hector Garcia")  # Replace with an actual tenant name if available

        # Simulate selecting a date
        self.app.cal.selection_set("9/13/24")

        # Capture the output of the submit function
        with self.assertLogs(level='INFO') as log:
            self.app.submit()
            self.assertIn("INFO:root:Property: 3175 Seminole Ave, SouthGate Property", log.output)
            self.assertIn("INFO:root:Tenant: Hector Garcia", log.output)
            self.assertIn("INFO:root:Billing Date: 9/13/24", log.output)

    def test_set_selected_tenant_as_default(self):
        # Simulate selecting a property and tenant
        self.app.property_combo.set("3306 Seminole Ave, Lynwood Property")
        self.app.on_property_select()
        self.app.tenant_combo.set("Maria Mercedes")

        # Set selected tenant as default
        self.app.set_selected_tenant_as_default()

        # Verify if the default tenant is set correctly
        self.assertEqual(self.app.default_tenants["3306 Seminole Ave, Lynwood Property"], "Maria Mercedes")

    def test_load_default_tenants(self):
        # Create a mock default tenants file
        default_tenants = {"3306 Seminole Ave, Lynwood Property": "Maria Mercedes"}
        with open('default_tenants.json', 'w') as f:
            json.dump(default_tenants, f)

        # Load default tenants
        loaded_tenants = self.app.load_default_tenants()

        # Verify if the default tenants are loaded correctly
        self.assertEqual(loaded_tenants, default_tenants)

if __name__ == '__main__':
    unittest.main()