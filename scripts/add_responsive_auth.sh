#!/bin/bash
# Script to add responsive CSS and auth guard to all HTML pages

# Find all HTML files (excluding node_modules, vendor, etc.)
find /workspace/project/TigerEx -name "*.html" -type f \
    ! -path "*/node_modules/*" \
    ! -path "*/vendor/*" \
    ! -path "*/.git/*" \
    ! -path "*/dist/*" \
    ! -path "*/build/*" \
    > /tmp/html_files.txt

# Process each file
while read -r file; do
    echo "Processing: $file"
    
    # Add responsive CSS after theme.css if not present
    if ! grep -q "responsive.css" "$file"; then
        sed -i 's|<link rel="stylesheet" href="assets/css/theme.css">|<link rel="stylesheet" href="assets/css/theme.css">\n    <link rel="stylesheet" href="assets/css/responsive.css">|g' "$file"
        echo "  Added responsive.css"
    fi
    
    # Add auth guard before closing body if not present
    if ! grep -q "auth-guard.js" "$file"; then
        # Add before </body>
        sed -i 's|<script src="assets/js/.*"></script>\s*</body>|...|g' "$file" 2>/dev/null || true
        
        # Just append before </body>
        sed -i 's|</body>|    <script src="assets/js/auth-guard.js"></script>\n</body>|g' "$file"
        echo "  Added auth-guard.js"
    fi

done < /tmp/html_files.txt

echo "Done!"