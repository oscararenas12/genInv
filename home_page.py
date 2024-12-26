# home_page.py

from tkcalendar import Calendar
import customtkinter as ctk
import os
import json
import logging
from datetime import datetime
from invoice_generator import fill_invoice
from invoice_handler import update_invoice_numbers

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
        
        # Add path for invoice template
        self.template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Invoice Master.pdf')

        # Configure window
        self.title("GenInv") 
        self.geometry("1000x700")  # Wider and taller to accommodate history
        ctk.set_appearance_mode("dark")
        
        # Configure grid weight for window expansion
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create main container frame
        container = ctk.CTkFrame(self)
        container.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)  # Make history section expandable

        # Top section frame (existing controls)
        top_frame = ctk.CTkFrame(container)
        top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Configure grid weights for top_frame
        top_frame.grid_columnconfigure(0, weight=1)  # Property column
        top_frame.grid_columnconfigure(1, weight=1)  # Calendar column

        # Property selection
        property_label = ctk.CTkLabel(top_frame, text="Select Property", font=("Arial", 16))
        property_label.grid(row=0, column=0, padx=20, pady=(15, 0), sticky="w")
        
        self.property_combo = ctk.CTkComboBox(top_frame, values=property_names, command=self.on_property_select)
        self.property_combo.set("Select Property")
        self.property_combo.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")

        # Tenant selection
        tenant_label = ctk.CTkLabel(top_frame, text="Select Tenant", font=("Arial", 16))
        tenant_label.grid(row=2, column=0, padx=20, pady=(10,5), sticky="w")
        
        self.tenant_combo = ctk.CTkComboBox(top_frame, values=["Select a property first"])
        self.tenant_combo.grid(row=3, column=0, padx=20, pady=(0,10), sticky="ew")

        # Button to set the selected tenant as default
        set_default_btn = ctk.CTkButton(top_frame, text="Set Default Tenant", command=self.set_default_tenant)
        set_default_btn.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        # Message label
        self.message_label = ctk.CTkLabel(top_frame, text="", font=("Arial", 12))
        self.message_label.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        # Add invoice number label
        self.invoice_label = ctk.CTkLabel(top_frame, text="Current Invoice #: -", font=("Arial", 12))
        self.invoice_label.grid(row=5, column=1, padx=20, pady=5, sticky="ew")

        # Billing date selection
        date_label = ctk.CTkLabel(top_frame, text="Select Billing Date", font=("Arial", 16))
        date_label.grid(row=0, column=1, padx=20, pady=(20,5), sticky="w")
        
        self.cal = Calendar(top_frame, selectmode="day", year=2024, month=9, day=13,
                          background="gray25", foreground='white', 
                          selectbackground="lightblue", 
                          selectforeground='black',
                          font=('Arial', 12), headersbackground="gray15", 
                          headersforeground='white', borderwidth=2,
                          showweeknumbers=False)
        self.cal.grid(row=1, column=1, rowspan=4, padx=20, pady=(0,10), sticky="nsew")

        # Generate Button
        submit_btn = ctk.CTkButton(top_frame, text="Generate", command=self.submit)
        submit_btn.grid(row=6, column=0, columnspan=2, padx=20, pady=(10,20), sticky="ew")

        # History section
        history_frame = ctk.CTkFrame(container)
        history_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # History title
        history_label = ctk.CTkLabel(history_frame, text="Invoice History", font=("Arial", 16, "bold"))
        history_label.pack(pady=(10, 5))

        # Headers frame
        headers_frame = ctk.CTkFrame(history_frame)
        headers_frame.pack(fill="x", padx=5, pady=5)
        headers_frame.grid_columnconfigure((0,1,2,3,4), weight=1)

        # Header labels
        headers = ["Date", "Invoice #", "Property", "Tenant", "Amount"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(headers_frame, text=header, font=("Arial", 14, "bold")).grid(
                row=0, column=i, padx=5, pady=5, sticky="ew")

        # Create scrollable frame for history entries
        self.history_scrollable = ctk.CTkScrollableFrame(history_frame)
        self.history_scrollable.pack(fill="both", expand=True, padx=5, pady=5)
        self.history_scrollable.grid_columnconfigure((0,1,2,3,4), weight=1)

        # Load initial history
        self.update_history()

        # Set minimum size for the window
        self.minsize(1000, 700)

    def update_history(self):
        try:
            # Clear existing history
            for widget in self.history_scrollable.winfo_children():
                widget.destroy()

            # Load data
            with open('properties_data.json', 'r') as f:
                data = json.load(f)

            # Create a list of all invoices
            all_invoices = []
            for prop in data['properties']:
                if isinstance(prop['invoice_no'], list):
                    for inv_no in prop['invoice_no']:
                        all_invoices.append({
                            'date': prop['date'],
                            'invoice_no': inv_no,
                            'property': prop['property_address1'],
                            'tenant': prop['to_renter'].split(',')[0],
                            'amount': prop['total']
                        })

            # Sort invoices by date (newest first) and invoice number
            all_invoices.sort(key=lambda x: (datetime.strptime(x['date'], '%m-%d-%Y'), x['invoice_no']), reverse=True)

            # Add entries to history
            for i, invoice in enumerate(all_invoices):
                bg_color = ("gray90", "gray20") if i % 2 == 0 else ("white", "gray30")
                row_frame = ctk.CTkFrame(self.history_scrollable, fg_color=bg_color)
                row_frame.grid(row=i, column=0, columnspan=5, sticky="ew", padx=2, pady=1)
                row_frame.grid_columnconfigure((0,1,2,3,4), weight=1)

                ctk.CTkLabel(row_frame, text=invoice['date']).grid(row=0, column=0, padx=5, pady=3)
                ctk.CTkLabel(row_frame, text=str(invoice['invoice_no'])).grid(row=0, column=1, padx=5, pady=3)
                ctk.CTkLabel(row_frame, text=invoice['property']).grid(row=0, column=2, padx=5, pady=3)
                ctk.CTkLabel(row_frame, text=invoice['tenant']).grid(row=0, column=3, padx=5, pady=3)
                ctk.CTkLabel(row_frame, text=invoice['amount']).grid(row=0, column=4, padx=5, pady=3)

        except Exception as e:
            self.display_message(f"Error loading invoice history: {str(e)}", "error")
            logging.error(f"Error loading invoice history: {str(e)}")

    # Add update_history call to submit method
    def submit(self):
        selected_property = self.property_combo.get()
        selected_tenant = self.tenant_combo.get()
        billing_date = self.cal.get_date()
        
        if selected_property == "Select Property" or selected_tenant in ["Select a property first", "Select Tenant", "No tenants found"]:
            self.display_message("Please select both property and tenant.", "error")
            return
            
        try:
            # Load existing data
            with open('properties_data.json', 'r') as f:
                data = json.load(f)
            
            # Find matching property data
            matching_property = None
            for prop in data['properties']:
                if prop['to_renter'].split(',')[0].strip() == selected_tenant.split(',')[0].strip():
                    matching_property = prop
                    break
            
            if matching_property:
                # Update date
                matching_property['date'] = datetime.strptime(billing_date, '%m/%d/%y').strftime('%m-%d-%Y')
                
                # Update invoice number and get the new number
                new_invoice_no = update_invoice_numbers(matching_property)
                
                # Create a copy of property data with the new invoice number
                invoice_data = matching_property.copy()
                invoice_data['invoice_no'] = new_invoice_no
                
                # Save updated data back to file
                with open('properties_data.json', 'w') as f:
                    json.dump(data, f, indent=4)
                
                # Generate invoice with new number
                output_pdf = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                        f"Invoice {new_invoice_no}.pdf")
                
                if fill_invoice(self.template_path, output_pdf, invoice_data):
                    self.display_message(f"Invoice {new_invoice_no} generated successfully!", "success")
                    # Update the invoice label with new number
                    self.invoice_label.configure(text=f"Current Invoice #: {new_invoice_no}")
                    # Update history after successful generation
                    self.update_history()
                else:
                    self.display_message("Failed to generate invoice.", "error")
            else:
                self.display_message("No matching tenant data found.", "error")
                
        except Exception as e:
            self.display_message(f"Error: {str(e)}", "error")
            logging.error(f"Error in submit: {str(e)}")

    # Rest of your existing methods remain the same
    def load_default_tenants(self):
        try:
            with open('default_tenants.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_default_tenants(self):
        with open('default_tenants.json', 'w') as f:
            json.dump(self.default_tenants, f, indent=4)

    def on_property_select(self, event=None):
        selected_property = self.property_combo.get()
        if selected_property:
            tenant_folders = self.find_tenants(properties[selected_property])
            
            # Update invoice number
            try:
                with open('properties_data.json', 'r') as f:
                    data = json.load(f)
                
                # Find the most recent invoice number for this property
                invoice_number = "-"
                property_short = selected_property.split(',')[0].strip()
                
                for prop in data['properties']:
                    if property_short in prop['property_address1']:
                        if isinstance(prop['invoice_no'], list) and prop['invoice_no']:
                            invoice_number = prop['invoice_no'][-1]
                        else:
                            invoice_number = prop['invoice_no']
                        break
                
                self.invoice_label.configure(text=f"Current Invoice #: {invoice_number}")
            except Exception as e:
                self.invoice_label.configure(text="Current Invoice #: Error loading")
                logging.error(f"Error loading invoice number: {str(e)}")

            # Tenant handling
            if tenant_folders:
                self.tenant_combo.configure(values=tenant_folders)
                default_tenant = self.default_tenants.get(selected_property)
                if default_tenant and default_tenant in tenant_folders:
                    self.tenant_combo.set(default_tenant)
                else:
                    self.tenant_combo.set("Select Tenant")
            else:
                self.tenant_combo.configure(values=["No tenants found"])
                self.tenant_combo.set("No tenants found")
                self.display_message("No tenants found for this property.", "error")
        else:
            self.tenant_combo.configure(values=["Select a property first"])
            self.tenant_combo.set("Select a property first")
            self.invoice_label.configure(text="Current Invoice #: -")

    def set_default_tenant(self):
        selected_property = self.property_combo.get()
        selected_tenant = self.tenant_combo.get()
        if selected_property == "Select Property" or not selected_property:
            self.display_message("Please select a property before setting a default tenant.", "error")
        elif selected_tenant in ["Select a property first", "Select Tenant", "No tenants found"] or not selected_tenant:
            self.display_message("Please select a valid tenant before setting it as the default.", "error")
        else:
            self.default_tenants[selected_property] = selected_tenant
            self.save_default_tenants()
            self.display_message("Default Tenant Set", "success")

    def find_tenants(self, property_folder):
        tenants = []
        tenants_path = os.path.join(invoice_directory, property_folder, "tenants")

        if os.path.exists(tenants_path):
            for folder_name in os.listdir(tenants_path):
                tenant_path = os.path.join(tenants_path, folder_name)
                if os.path.isdir(tenant_path):
                    tenants.append(folder_name)
        else:
            self.display_message(f"The 'tenants' folder for {property_folder} was not found.", "error")

        return tenants

    def display_message(self, message, message_type):
        if message_type == "error":
            self.message_label.configure(text=message, text_color="red")
        elif message_type == "success":
            self.message_label.configure(text=message, text_color="green")

if __name__ == "__main__":
    app = PropertyApp()
    app.mainloop()