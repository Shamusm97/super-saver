#!/bin/zsh

# Check if a directory is provided as an argument
if [[ $# -eq 0 ]]; then
    echo "Please provide a directory path as an argument."
    exit 1
fi

# Store the provided directory path
target_dir="$1"

# Check if the provided path is a directory
if [[ ! -d "$target_dir" ]]; then
    echo "The provided path is not a directory."
    exit 1
fi

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "jq is not installed. Please install it and try again."
    exit 1
fi

# Function to format JSON files
format_json() {
    local file="$1"
    echo "Formatting $file"
    # Create a temporary file
    temp_file=$(mktemp)
    # Format the JSON and write to the temporary file
    jq '.' "$file" > "$temp_file"
    # Check if jq command was successful
    if [[ $? -eq 0 ]]; then
        # If successful, overwrite the original file with the formatted content
        mv "$temp_file" "$file"
    else
        echo "Error formatting $file"
        rm "$temp_file"
    fi
}

# Find all JSON files in the directory and its subdirectories, then format them
find "$target_dir" -type f -name "*.json" -print0 | while IFS= read -r -d '' file; do
    format_json "$file"
done

echo "Formatting complete."
