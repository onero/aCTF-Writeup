#!/bin/bash

# Function to convert a string to lowercase and replace spaces with hyphens
slugify() {
    echo "$1" | awk '{print tolower($0)}' | sed -r 's/\s+/-/g'
}

# Prompt for challenge details
read -p "Title of the Challenge: " title
read -p "Category of the Challenge: " category
read -p "Date of Completion (YYYY-MM-DDTHH:MM:SS+ZZ:ZZ) [Default: current date]: " date

# Default date if not provided
if [ -z "$date" ]; then
    date=$(date +"%Y-%m-%dT%H:%M:%S")
    tz=$(date +%z | sed 's/\(.\{3\}\)/\1:/')
    date="$date$tz"
fi

# Convert title and category to URL-friendly slugs
title_slug=$(slugify "$title")
category_slug=$(slugify "$category")

# Directory path
category_dir="./$category_slug"
challenge_dir="$category_dir/$title_slug"

# Create category directory if it doesn't exist
if [ ! -d "$category_dir" ]; then
    mkdir -p "$category_dir"
fi

# Create challenge directory
mkdir -p "$challenge_dir"

# Create index.md with provided details
cat << EOF > "$challenge_dir/index.md"
+++
title = '$title'
categories = ['$category']
date = $date
scrollToTop = true
+++

## Challenge Name:

$title

## Category:

$category

## Challenge Description:

## Approach

## Flag

\`\`\`text

\`\`\`

## Reflections and Learnings
EOF

echo "Writeup template created at $challenge_dir/index.md"
