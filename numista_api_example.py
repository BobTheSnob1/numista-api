import csv
import requests
from tqdm import tqdm

# Define the base URL and API key
base_url = 'https://api.numista.com/api/v3'
api_key = 'S2tRJWSvTiV8gJSTsC8WTdHvSRBxv7mcAJNBw27M'

# List of type IDs to process
type_ids = input("ID List:").split(" ")

# Function to get type details
def get_type_details(type_id):
    response = requests.get(
        f"{base_url}/types/{type_id}",
        headers={'Numista-API-Key': api_key}
    )
    return response.json()

# Function to get type prices
def get_type_prices(type_id):
    response = requests.get(
        f"{base_url}/types/{type_id}/issues",
        headers={'Numista-API-Key': api_key}
    )
    issues = response.json()
    if issues:
        year_line_id = str(issues[0]['id'])
        response = requests.get(
            f"{base_url}/types/{type_id}/issues/{year_line_id}/prices",
            headers={'Numista-API-Key': api_key}
        )
        return response.json()
    return {}

# Function to calculate the average sale price
def calculate_average_sale_price(prices_data):
    if 'prices' in prices_data:
        total_price = 0
        count = 0
        for price in prices_data['prices']:
            total_price += price['price']
            count += 1
        if count > 0:
            return total_price / count
    return 'N/A'

# Function to format the face value
def format_face_value(value):
    if 'numeric_value' in value and 'currency' in value:
        return f"{value['numeric_value']} {value['currency']['name']}"
    return ''

# Function to extract required details from type data
def extract_details(type_data, prices_data):
    average_price = calculate_average_sale_price(prices_data)
    return {
        'Title': type_data.get('title'),
        'ID': type_data.get('id'),
        'URL': type_data.get('url'),
        'Value': format_face_value(type_data.get('value', {})),
        'Composition': type_data.get('composition', {}).get('text', 'N/A'),
        'Weight': type_data.get('weight', 'N/A'),
        'Obverse Picture': type_data.get('obverse', {}).get('picture', 'N/A'),
        'Reverse Picture': type_data.get('reverse', {}).get('picture', 'N/A'),
        'Average Sale Price': average_price
    }


# Prepare CSV file for output
with open('numista_details.csv', mode='w', newline='', encoding='utf-8') as csv_file:
    fieldnames = [
        'Title', 'ID', 'URL', 'Value', 'Composition', 'Weight',
        'Obverse Picture', 'Reverse Picture', 'Average Sale Price'
    ]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    # Process each type ID
    for type_id in tqdm(type_ids, desc="Processing type IDs"):
        type_details = get_type_details(type_id)
        prices_details = get_type_prices(type_id)
        details = extract_details(type_details, prices_details)
        writer.writerow(details)

print("CSV file created successfully.")
