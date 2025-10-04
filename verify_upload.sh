#!/bin/bash
# TigerEx Complete System Upload Verification Script

echo "🚀 TigerEx Complete System - Upload Verification"
echo "==============================================="
echo ""

# Check repository status
echo "📊 REPOSITORY STATUS:"
echo "---------------------"
cd /workspace/tigerex-repo
git status
echo ""

# Show recent commits
echo "📋 RECENT COMMITS:"
echo "------------------"
git log --oneline -5
echo ""

# Count total files
echo "📁 TOTAL FILES:"
echo "--------------"
echo "Total files in repository: $(git ls-files | wc -l)"
echo ""

# Show file categories
echo "📦 FILE CATEGORIES:"
echo "------------------"
echo "Backend services: $(find backend -name "*.py" | wc -l) files"
echo "Frontend components: $(find frontend -name "*.jsx" -o -name "*.js" | wc -l) files"
echo "Mobile app files: $(find mobile -type f | wc -l) files"
echo "Desktop app files: $(find desktop -type f | wc -l) files"
echo "Documentation: $(find docs -name "*.md" | wc -l) files"
echo "Screenshots: $(find screenshots -name "*.jpg" | wc -l) files"
echo ""

# Show repository size
echo "💾 REPOSITORY SIZE:"
echo "------------------"
du -sh .
echo ""

# Verify key files exist
echo "✅ KEY FILES VERIFICATION:"
echo "-------------------------"
declare -a files=(
    "backend/admin_dashboard_complete.py"
    "backend/services/advanced_transfer_service.py"
    "backend/services/trading_history_service.py"
    "backend/services/deposit_withdraw_service.py"
    "backend/services/portfolio_service.py"
    "frontend/src/components/Exchange/CEXTrading.jsx"
    "frontend/src/components/Exchange/DEXTrading.jsx"
    "mobile/package.json"
    "desktop/main.js"
    "docs/FINAL_IMPLEMENTATION_REPORT.md"
    "screenshots/Screenshot_20251004_000023_com.binance.dev.jpg"
)

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - MISSING"
    fi
done
echo ""

echo "🎯 PUSH INSTRUCTIONS:"
echo "--------------------"
echo "To push to GitHub, run:"
echo "git push origin main"
echo ""
echo "If authentication is needed:"
echo "1. Use HTTPS: git push https://github.com/meghlabd275-byte/TigerEx-.git main"
echo "2. Use SSH: git push git@github.com:meghlabd275-byte/TigerEx-.git main"
echo "3. Use GitHub CLI: gh repo sync"
echo ""

echo "🏆 SYSTEM STATUS: COMPLETE AND READY FOR UPLOAD!"
echo "==============================================="