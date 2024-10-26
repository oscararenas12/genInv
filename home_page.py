from tkcalendar import Calendar
import customtkinter as ctk
import os
from tkinter import messagebox
import json
from tkinter import Menu

# Main directory where property folders are stored
invoice_directory = r"C:\Users\oscar\OneDrive\Oscar\Properties"

# List of properties and their respective folders
properties = {
    "3175 Seminole Ave, SouthGate Property": "3175 Seminole Ave, SouthGate Property",
    "3306 Seminole Ave, Lynwood Property": "3306 Seminole Ave, Lynwood Property",
    "10755 State St, Lynwood Property": "10755 State St, Lynwood Property",
    "10756 State St, Lynwood Property": "10756 State St, Lynwood Property",
    "10757 State St, Lynwood Property": "10757 State St, Lynwood Property",
    "10974 Lou Dillon Ave, Los Angeles Property": "10974 Lou Dillon Ave, Los Angeles Property"
}

# Extract the property names (keys) as a list
property_names = list(properties.keys())

class PropertyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Load default tenants from JSON file
        self.default_tenants = self.load_default_tenants()

        # Oscar opens a new desktop app called genInv
        self.title("GenInv") 
        self.geometry("600x450")
        ctk.set_appearance_mode("dark")  # Set appearance mode

        # Create a menu bar at the top
        self.menu_bar = Menu(self)
        self.config(menu=self.menu_bar)

        # Add 'Settings' menu
        settings_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label='Settings', menu=settings_menu)

        # Add 'Set Selected Tenant as Default' command
        settings_menu.add_command(label='Set Selected Tenant as Default', command=self.set_selected_tenant_as_default)

        # Create a main frame to hold the widgets
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=20, pady=20)

        # Oscar is required to choose a specific property from a drop-down menu
        property_label = ctk.CTkLabel(main_frame, text="Select Property", font=("Arial", 16))
        property_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")
        self.property_combo = ctk.CTkComboBox(main_frame, values=property_names, command=self.on_property_select)
        self.property_combo.set("Select Property")
        self.property_combo.grid(row=1, column=0, padx=20, pady=0, sticky="n")

        # Once selected, he moves on to the tenant selection.
        tenant_label = ctk.CTkLabel(main_frame, text="Select Tenant", font=("Arial", 16))
        tenant_label.grid(row=2, column=0, padx=20, pady=0, sticky="w")
        self.tenant_combo = ctk.CTkComboBox(main_frame, values=["Select a property first"])
        self.tenant_combo.grid(row=3, column=0, padx=20, pady=0, sticky="n")

        # Oscar then moves on to the next step, which is to select the billing date.
        date_label = ctk.CTkLabel(main_frame, text="Select Billing Date", font=("Arial", 16))
        date_label.grid(row=0, column=1, padx=20, pady=0)
        self.cal = Calendar(main_frame, selectmode="day", year=2024, month=9, day=13,
                            background="gray25", foreground='white', 
                            selectbackground="lightblue", 
                            selectforeground='black',
                            font=('Arial', 12), headersbackground="gray15", 
                            headersforeground='white', borderwidth=20,
                            showweeknumbers=False)  # Hide week numbers
        self.cal.grid(row=1, column=1, rowspan=3, padx=20, pady=0)

        # Submit Button to submit the form
        submit_btn = ctk.CTkButton(main_frame, text="Submit", command=self.submit)
        submit_btn.grid(row=4, column=0, columnspan=2, padx=20, pady=20, sticky="we")  # Centered horizontally

    def load_default_tenants(self):
        """Load default tenants from JSON file."""
        try:
            with open('default_tenants.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}  # Return empty dict if file not found

    def save_default_tenants(self):
        """Save default tenants to JSON file."""
        with open('default_tenants.json', 'w') as f:
            json.dump(self.default_tenants, f)

    def submit(self):
        print("Property:", self.property_combo.get())
        print("Tenant:", self.tenant_combo.get())
        print("Billing Date:", self.cal.get_date())

    def on_property_select(self, event=None):
        """Handles property selection event and updates the tenant list."""
        selected_property = self.property_combo.get()
        if selected_property:
            tenant_folders = self.find_tenants(properties[selected_property])

            if tenant_folders:
                # Update tenant combo box with the found tenant folders
                self.tenant_combo.configure(values=tenant_folders)
                # Set the default tenant if it exists
                default_tenant = self.default_tenants.get(selected_property)
                if default_tenant and default_tenant in tenant_folders:
                    self.tenant_combo.set(default_tenant)
                else:
                    self.tenant_combo.set("Select Tenant")
            else:
                # No tenants found
                self.tenant_combo.configure(values=["No tenants found"])
                self.tenant_combo.set("No tenants found")
                messagebox.showinfo("No Tenants Found", f"No tenants found for {selected_property}.")
        else:
            self.tenant_combo.configure(values=["Select a property first"])
            self.tenant_combo.set("Select a property first")

    def set_selected_tenant_as_default(self):
        """Sets the currently selected tenant as the default for the selected property."""
        selected_property = self.property_combo.get()
        selected_tenant = self.tenant_combo.get()
        if selected_property in properties and selected_tenant and selected_tenant != "Select Tenant":
            self.default_tenants[selected_property] = selected_tenant
            self.save_default_tenants()
            messagebox.showinfo("Default Tenant Changed", f"The default tenant for {selected_property} has been set to {selected_tenant}.")
        else:
            messagebox.showerror("Selection Error", "Please select a property and tenant before setting the default tenant.")

    # Function to find tenant folders in the 'tenants' subfolder of the specified property
    def find_tenants(self, property_folder):
        tenants = []
        tenants_path = os.path.join(invoice_directory, property_folder, "tenants")  # Construct the full path to the 'tenants' folder

        if os.path.exists(tenants_path):
            for folder_name in os.listdir(tenants_path):
                tenant_path = os.path.join(tenants_path, folder_name)
                if os.path.isdir(tenant_path):  # Ensure it is a directory (tenant folder)
                    tenants.append(folder_name)
        else:
            messagebox.showerror("Folder Not Found", f"The 'tenants' folder for {property_folder} was not found.")

        return tenants

if __name__ == "__main__":
    app = PropertyApp()
    app.mainloop()
