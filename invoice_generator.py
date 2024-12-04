# invoice_generator.py

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