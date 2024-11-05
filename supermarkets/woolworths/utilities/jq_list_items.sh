#!/usr/bin/env bash

# Check if a directory argument is provided
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

main_dir="$1"

# Check if the provided directory exists
if [[ ! -d "$main_dir" ]]; then
    echo "Error: Directory '$main_dir' does not exist."
    exit 1
fi

# Initialize variables
declare -A category_counts
declare -A category_totals

# Process each subdirectory
for category_dir in "$main_dir"/*/; do
    category=$(basename "$category_dir")
    category_count=0
    category_total=0

    # Process each JSON file in the category
    for json_file in "$category_dir"/*.json; do
        if [[ -f "$json_file" ]]; then
            # Count items in products.items
            items_count=$(jq '.products.items | length' "$json_file")
            category_count=$((category_count + items_count))

            # Get total items (should be the same for all files in the category)
            file_total_items=$(jq '.products.totalItems' "$json_file")
            if [[ $category_total -eq 0 ]]; then
                category_total=$file_total_items
            elif [[ $category_total -ne $file_total_items ]]; then
                echo "Warning: Inconsistent totalitems value in $json_file"
            fi
        fi
    done

    category_counts["$category"]=$category_count
    category_totals["$category"]=$category_total
done

# Print results
echo "Item counts and expected totals by category:"
for category in "${!category_counts[@]}"; do
    echo "$category:"
    echo "  Counted items: ${category_counts[$category]}"
    echo "  Expected total: ${category_totals[$category]}"
done

# Calculate and print the grand total of expected items
grand_total=0
for total in "${category_totals[@]}"; do
    grand_total=$((grand_total + total))
done
# Calculate and print the grand total of actual items
actual_total=0
for count in "${category_counts[@]}"; do
    actual_total=$((actual_total + count))
done
echo -e "\nGrand total of actual items across all categories: $actual_total"
echo -e "\nGrand total of expected items across all categories: $grand_total"
