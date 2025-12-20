#!/bin/bash

# Script to customize the AI Detector app name
# Usage: ./customize-name.sh "Your Custom Name"

if [ -z "$1" ]; then
    echo "❌ Error: Please provide a custom name"
    echo "Usage: ./customize-name.sh \"Your Custom Name\""
    exit 1
fi

NEW_NAME="$1"
OLD_NAME="AI Content Detector"

echo "🎨 Customizing App Name"
echo "======================="
echo "Old Name: $OLD_NAME"
echo "New Name: $NEW_NAME"
echo ""

# Backup files
echo "📦 Creating backups..."
cp Frontend/index.html Frontend/index.html.backup
cp Frontend/src/App.jsx Frontend/src/App.jsx.backup
cp Frontend/src/AppEnhanced.jsx Frontend/src/AppEnhanced.jsx.backup
cp README.md README.md.backup

# Update Frontend/index.html
echo "📝 Updating Frontend/index.html..."
sed -i.bak "s/<title>$OLD_NAME<\/title>/<title>$NEW_NAME<\/title>/g" Frontend/index.html

# Update Frontend/src/App.jsx
echo "📝 Updating Frontend/src/App.jsx..."
sed -i.bak "s/<h1 className=\"header-title\">$OLD_NAME<\/h1>/<h1 className=\"header-title\">$NEW_NAME<\/h1>/g" Frontend/src/App.jsx

# Update Frontend/src/AppEnhanced.jsx
echo "📝 Updating Frontend/src/AppEnhanced.jsx..."
sed -i.bak "s/<h1 className=\"header-title\">$OLD_NAME<\/h1>/<h1 className=\"header-title\">$NEW_NAME<\/h1>/g" Frontend/src/AppEnhanced.jsx

# Update README.md
echo "📝 Updating README.md..."
sed -i.bak "s/# $OLD_NAME/# $NEW_NAME/g" README.md

# Clean up .bak files
rm -f Frontend/index.html.bak Frontend/src/App.jsx.bak Frontend/src/AppEnhanced.jsx.bak README.md.bak

echo ""
echo "✅ Customization Complete!"
echo ""
echo "📋 Files Updated:"
echo "  - Frontend/index.html"
echo "  - Frontend/src/App.jsx"
echo "  - Frontend/src/AppEnhanced.jsx"
echo "  - README.md"
echo ""
echo "📦 Backups created:"
echo "  - Frontend/index.html.backup"
echo "  - Frontend/src/App.jsx.backup"
echo "  - Frontend/src/AppEnhanced.jsx.backup"
echo "  - README.md.backup"
echo ""
echo "🔄 Next Steps:"
echo "  1. Review changes: git diff"
echo "  2. Rebuild frontend: cd Frontend && npm run build"
echo "  3. Commit changes: git add . && git commit -m \"Customize app name to $NEW_NAME\""
echo "  4. Push to GitHub: git push origin main"
echo "  5. Update on EC2: ssh into EC2 and run ./update.sh"
echo ""
