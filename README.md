***GenInv***

**UI Libraries Used**

`pip install tkcalendar`

`pip install customtkinter`

**General Test Driven Development Story approach:**

Oscar opens a new desktop app called genInv, designed to automatically generate invoices without manual input. The app presents him with three key options: selecting a property, a tenant, and a billing date. 

First, Oscar is required to choose a specific property from a drop-down menu. Once selected, he moves on to the tenant selection. He notices that the default tenant is incorrect, but quickly fixes it by selecting the 'Change Default Tenant' option at the bottom of the menu. After choosing the correct tenant, the system updates to remember this as the default for future invoices related to that property.

Lastly, he sees that the date is automatically set for the next billing period, but he has the option to adjustit if needed. This ensures that future invoices are appended with correct data if it's for a new month. 

**Use Cases:**

*Use Case 1:* User selects a specific property.

-   Initial look “--- Select a Property ---”
-   Drop down menu will list all properties 

*Use Case 2:* User selects a specific
-   Drop down menu will list all tenant from past and present
-   Ability to set a default tenant
-   Default will stay the same until user want to change it

*Use Case 3:* User selects a date

-   The date will automatically be set to the next month, as the invoice is intended for the upcoming billing period.
-   Users can change date if necessary. 

*Use Case 4:* Invoice Generator Button 

-   In the background, the program will retrieve information (PDF files as invoices) from the directory where I’ve formatted the file paths.
-   
**Commands to Run Code**

`python home_page.py`

`python -m unittest test_home_page.py`