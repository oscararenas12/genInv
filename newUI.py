from tkcalendar import Calendar
import customtkinter as ctk
import os
from tkinter import messagebox

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

        # Change the title of the app window here
        self.title("GenInv")  # Update this to your desired title

        self.geometry("600x450")

        # Set appearance mode
        ctk.set_appearance_mode("dark")

        # Create a main frame to hold the widgets
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=0, column=0, padx=20, pady=20)

        # Property Selection (left)
        property_label = ctk.CTkLabel(main_frame, text="Select Property", font=("Arial", 16))
        property_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        self.property_combo = ctk.CTkComboBox(main_frame, values=property_names, command=self.on_property_select)
        self.property_combo.grid(row=1, column=0, padx=20, pady=0, sticky="n")

        # Tenant Selection (left)
        tenant_label = ctk.CTkLabel(main_frame, text="Select Tenant", font=("Arial", 16))
        tenant_label.grid(row=2, column=0, padx=20, pady=0, sticky="w")

        self.tenant_combo = ctk.CTkComboBox(main_frame, values=["Select a property first"])
        self.tenant_combo.grid(row=3, column=0, padx=20, pady=0, sticky="n")

        # Billing Date (right)
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

        # Submit Button (centered horizontally with columnspan=2)
        submit_btn = ctk.CTkButton(main_frame, text="Submit", command=self.submit)
        submit_btn.grid(row=4, column=0, columnspan=2, padx=20, pady=20, sticky="we")  # Centered horizontally

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
            else:
                # No tenants found
                self.tenant_combo.configure(values=["No tenants found"])
                messagebox.showinfo("No Tenants Found", f"No tenants found for {selected_property}.")

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
