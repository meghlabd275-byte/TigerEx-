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

echo "Done! All HTML files updated with theme system."# Wallet API - TigerEx Multi-chain Wallet
create_wallet() {
    address="0x$(head -c 40 /dev/urandom | xxd -p)"
    seed="abandon ability able about above absent absorb abstract absurd abuse access accident account accuse achieve acid acoustic acquire across act action actor actress actual adapt add adjust admin admit adult advance advice aerobic affair afford afraid again age agency agent agree ahead aim air airport alarm album alcohol alien alike alive allow alone along alpha already also alter always amazing among amount analyze ancient angle angry animal anniversary announce another answer antenna anxiety any apart apology appear apple approve april aqua arabian architecture area argue arise armed armor army around arrange arrest arrival arrive arrow artist artwork area"
    echo "{\"address\":\"$address\",\"seed\":\"$seed\",\"ownership\":\"USER_OWNS\"}"
}
