
import json
import csv
from pathlib import Path

def process_product_data(base_dir, output_file):
    base_path = Path(base_dir)
    all_products = []

    # Process all JSON files in the data directory
    for json_file in base_path.glob('*/*.json'):
        with json_file.open() as f:
            data = json.load(f)
        
        for item in data['products']:
            product = {
                'productId': item.get('productId', ''),
                'brand': item.get('brand', ''),
                'name': item.get('name', ''),
                'displayName': item.get('displayName', ''),
                'availability': item.get('availability', ''),
                'saleType': item.get('saleType', ''),
                'restrictedFlag': item.get('restrictedFlag', False),
                'liquorFlag': item.get('liquorFlag', False),
                'tobaccoFlag': item.get('tobaccoFlag', False),
                'originRegulated': item.get('originRegulated', False),
                'singlePrice': item.get('singlePrice', {}).get('price', '')
            }
            all_products.append(product)

    # Write products to CSV file
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = all_products[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for product in all_products:
            writer.writerow(product)

    print(f"Processed {len(all_products)} products and saved to {output_file}")

# Usage
process_product_data('./data', 'output.csv')
