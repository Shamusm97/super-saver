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
        
        for item in data['products']['items']:
            if item['type'] == 'Product':
                product = {
                    'sku': item['sku'],
                    'name': item['name'].strip(),
                    'barcode': item['barcode'],
                    'price': item['price']['originalPrice'],
                    'salePrice': item['price']['salePrice'],
                    'savePrice': item['price']['savePrice'],
                    'savePercentage': item['price']['savePercentage'],
                    'isClubPrice': item['price']['isClubPrice'],
                    'isSpecial': item['price']['isSpecial'],
                    'isNew': item['price']['isNew'],
                    'brand': item['brand'],
                    'unit': item['unit'],
                    'variety': item['variety'],
                    'stockLevel': item['stockLevel'],
                    'departments': item['departments'][0]['name'] if item['departments'] else '',
                    'image_big': item['images']['big'],
                    'image_small': item['images']['small'],
                    'availabilityStatus': item['availabilityStatus']
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
