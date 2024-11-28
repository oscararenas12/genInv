import sys
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os
import json

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

def main():
    # Get the directory of the script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set input paths
    input_pdf = os.path.join(script_dir, 'MasterInvoice.pdf')
    json_file = os.path.join(script_dir, 'properties_data.json')
    
    # Check if input files exist
    if not os.path.exists(input_pdf):
        print(f"Error: Input PDF file not found at {input_pdf}")
        print("Please ensure your template PDF is named 'input.pdf' and is in the same directory as this script.")
        return
        
    if not os.path.exists(json_file):
        print(f"Error: JSON file not found at {json_file}")
        print("Please ensure properties_data.json is in the same directory as this script.")
        return
    
    # Read JSON data
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Process all properties in the list
        for property_data in data['properties']:
            # Generate output filename using invoice number
            output_filename = f"invoice_{property_data['invoice_no']}.pdf"
            output_pdf = os.path.join(script_dir, output_filename)
            
            # Fill the invoice
            print(f"Creating invoice {property_data['invoice_no']} for {property_data['to_renter']}...")
            if fill_invoice(input_pdf, output_pdf, property_data):
                print(f"Success! Filled invoice saved as: {output_pdf}")
            else:
                print(f"Failed to create invoice {property_data['invoice_no']}. Check the error message above.")
            
        print("\nAll invoices have been generated!")
            
    except Exception as e:
        print(f"Error processing JSON data: {str(e)}")

if __name__ == "__main__":
    main()