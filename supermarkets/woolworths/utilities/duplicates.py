import csv
from collections import defaultdict
from pprint import pprint

# Open the CSV file
with open('output.csv', 'r') as f:
    reader = csv.reader(f)
    # Assuming the barcode is in the first column
    # If it's in a different column, adjust the index below
    barcode_counts = defaultdict(list)
    for row in reader:
        barcode = row[0]
        barcode_counts[barcode].append(row)

# Find duplicates
duplicates = {barcode: rows for barcode, rows in barcode_counts.items() if len(rows) > 1}

# Print results
print(f"Total unique barcodes: {len(barcode_counts)}")
print(f"Number of barcodes with duplicates: {len(duplicates)}")

# Optionally, print some of the duplicates
print("\nSample of duplicates:")
for barcode, rows in list(duplicates.items())[:5]:  # Print first 5 duplicates
    print(f"\nBarcode {barcode} appears {len(rows)} times:")
    for row in rows:
        print(f"  {row}")

# If you want to save the duplicates to a file
with open('duplicate_barcodes.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Barcode', 'Occurrences', 'Data'])
    for barcode, rows in duplicates.items():
        writer.writerow([barcode, len(rows), rows])

print(f"\nDuplicate barcodes have been saved to 'duplicate_barcodes.csv'")
