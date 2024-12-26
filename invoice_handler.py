# invoice_handler.py

def get_next_invoice_number(current_numbers):
    """Get the next invoice number based on the current list of numbers"""
    if not current_numbers:
        return 1
    return int(current_numbers[-1]) + 1

def update_invoice_numbers(property_data):
    """Add a new invoice number to the property's invoice_no list"""
    if not isinstance(property_data['invoice_no'], list):
        # Convert single number to list if needed
        property_data['invoice_no'] = [int(property_data['invoice_no'])]
    
    # Add next number to the sequence
    next_number = get_next_invoice_number(property_data['invoice_no'])
    property_data['invoice_no'].append(next_number)
    return str(next_number)  # Return the new invoice number as string