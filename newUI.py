from tkcalendar import Calendar
import customtkinter as ctk

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
        property_label.grid(row=0, column=0, padx=20, pady=20, sticky="w")  # Use small positive pady

        self.property_combo = ctk.CTkComboBox(main_frame, values=["Property 1", "Property 2", "Property 3"])
        self.property_combo.grid(row=1, column=0, padx=20, pady=0, sticky="n")  

        # Tenant Selection (left)
        tenant_label = ctk.CTkLabel(main_frame, text="Select Tenant", font=("Arial", 16))
        tenant_label.grid(row=2, column=0, padx=20, pady=0, sticky="w")

        self.tenant_combo = ctk.CTkComboBox(main_frame, values=["Tenant 1", "Tenant 2", "Tenant 3"])
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

if __name__ == "__main__":
    app = PropertyApp()
    app.mainloop()
