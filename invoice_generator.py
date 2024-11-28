import sys
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os

def fill_invoice(input_pdf, output_pdf, data):
    try:
        # Read the template PDF
        template_pdf = PdfReader(open(input_pdf, 'rb'))
        output = PdfWriter()
        
        # Create a new PDF with our text
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)
        
        # Set font and size
        c.setFont("Helvetica", 10)
        
        # Fill in all fields
        field_positions = {
            'date': (345, 742),
            'invoice_no': (380, 725),
            'property_address1': (425, 710),
            'property_address2': (310, 695),
            
            # FROM section
            'from_company': (120, 652),
            'from_email': (105, 635),
            'from_phone': (105, 205),
            
            # BILL TO section
            'to_renter': (370, 652),
            'to_address': (370, 617),
            'to_city_state': (378, 600),
            'to_zip': (333, 583),
            'to_phone': (350, 567),
            'to_email': (350, 549),
        }
        
        # Fill in the basic fields
        for field, (x, y) in field_positions.items():
            if field in data:
                c.drawString(x, y, str(data[field]))
        
        # Fill in line items
        if 'line_items' in data:
            y_position = 480
            for desc, amount in data['line_items']:
                c.drawString(60, y_position, str(desc))
                c.drawString(480, y_position, str(amount))
                y_position -= 20
        
        # Fill in totals
        totals_positions = {
            'subtotal': (480, 243),
            'discount': (480, 219),
            'fees': (480, 197),
            'tax': (480, 174),
            'total': (480, 152)
        }
        
        for field, (x, y) in totals_positions.items():
            if field in data:
                c.drawString(x, y, str(data[field]))
        
        c.save()
        packet.seek(0)
        
        # Create new PDF with the text
        new_pdf = PdfReader(packet)
        
        # Merge with template
        page = template_pdf.pages[0]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)
        
        # Write the output file
        with open(output_pdf, 'wb') as outputStream:
            output.write(outputStream)
            
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

# Example data
sample_data = {
    'date': '2024-11-27',
    'invoice_no': '27',
    'property_address1': '10974 Lou Dillon Ave',
    'property_address2': 'Anytown, USA',
    'from_company': 'Property Management LLC',
    'from_email': 'john@property.com',
    'from_phone': 'Questions: (555) 123-4567',
    'to_renter': 'Helen Tenant',
    'to_address': '789 Resident St',
    'to_city_state': 'Townsburg, ST',
    'to_zip': '67890',
    'to_phone': '(555) 987-6543',
    'to_email': 'jane@tenant.com',
    'line_items': [
        ('Monthly Rent - December 2024', '$1500.00'),
        ('Utilities', '$200.00'),
        ('Parking', '$100.00')
    ],
    'subtotal': '$1800.00',
    'discount': '$0.00',
    'fees': '$50.00',
    'tax': '$0.00',
    'total': '$1850.00'
}

def main():
    
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set input and output paths
    input_pdf = os.path.join(script_dir, 'input.pdf')
    output_pdf = os.path.join(script_dir, 'filled_invoice.pdf')
    
    # Check if input file exists
    if not os.path.exists(input_pdf):
        print(f"Error: Input PDF file not found at {input_pdf}")
        print("Please ensure your template PDF is named 'input.pdf' and is in the same directory as this script.")
        return
    
    # Fill the invoice
    print("Filling invoice...")
    if fill_invoice(input_pdf, output_pdf, sample_data):
        print(f"Success! Filled invoice saved as: {output_pdf}")
    else:
        print("Failed to fill invoice. Please check the error message above.")

if __name__ == "__main__":
    main()