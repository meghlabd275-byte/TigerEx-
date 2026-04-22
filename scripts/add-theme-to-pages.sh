#!/bin/bash
# Script to add theme system to all HTML files

THEME_TOGGLE_HTML='<!-- Theme Toggle -->
<div class="theme-toggle" onclick="toggleTheme()" title="Toggle Theme" style="padding: 8px;">
    <span>🌙</span>
</div>'

THEME_CSS_LINK='<link rel="stylesheet" href="assets/css/theme.css">'
THEME_JS='<script src="assets/js/theme.js"></script>'
THEME_TOGGLE_CSS='.theme-toggle { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; background: var(--bg-card); border: 1px solid var(--border); cursor: pointer; transition: all 0.2s; padding: 8px; } .theme-toggle:hover { background: var(--bg-card-hover); } body { transition: background-color 0.3s, color 0.3s; }'

# Find all HTML files
find . -name "*.html" -type f | while read file; do
    echo "Processing: $file"
    
    # Add CSS link after <head> tag (if not exists)
    if ! grep -q 'assets/css/theme.css' "$file"; then
        sed -i 's|<head>|<head>\n    <link rel="stylesheet" href="assets/css/theme.css">|' "$file"
    fi
    
    # Add JS script before </body> tag (if not exists)
    if ! grep -q 'assets/js/theme.js' "$file"; then
        sed -i 's|</body>|    <script src="assets/js/theme.js"></script>\n</body>|' "$file"
    fi
    
    # Add theme toggle CSS if not exists
    if ! grep -q '.theme-toggle' "$file"; then
        sed -i 's|</style>|.theme-toggle { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; background: var(--bg-card); border: 1px solid var(--border); cursor: pointer; transition: all 0.2s; padding: 8px; } .theme-toggle:hover { background: var(--bg-card-hover); } body { transition: background-color 0.3s, color 0.3s; }\n    </style>|' "$file"
    fi
done

echo "Done! All HTML files updated with theme system."