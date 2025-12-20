# Script to customize the AI Detector app name (Windows PowerShell)
# Usage: .\customize-name.ps1 "Your Custom Name"

param(
    [Parameter(Mandatory=$true)]
    [string]$NewName
)

$OldName = "AI Content Detector"

Write-Host "🎨 Customizing App Name" -ForegroundColor Cyan
Write-Host "=======================" -ForegroundColor Cyan
Write-Host "Old Name: $OldName"
Write-Host "New Name: $NewName"
Write-Host ""

# Backup files
Write-Host "📦 Creating backups..." -ForegroundColor Yellow
Copy-Item "Frontend\index.html" "Frontend\index.html.backup"
Copy-Item "Frontend\src\App.jsx" "Frontend\src\App.jsx.backup"
Copy-Item "Frontend\src\AppEnhanced.jsx" "Frontend\src\AppEnhanced.jsx.backup"
Copy-Item "README.md" "README.md.backup"

# Update Frontend/index.html
Write-Host "📝 Updating Frontend\index.html..." -ForegroundColor Green
(Get-Content "Frontend\index.html") -replace "<title>$OldName</title>", "<title>$NewName</title>" | Set-Content "Frontend\index.html"

# Update Frontend/src/App.jsx
Write-Host "📝 Updating Frontend\src\App.jsx..." -ForegroundColor Green
(Get-Content "Frontend\src\App.jsx") -replace "<h1 className=`"header-title`">$OldName</h1>", "<h1 className=`"header-title`">$NewName</h1>" | Set-Content "Frontend\src\App.jsx"

# Update Frontend/src/AppEnhanced.jsx
Write-Host "📝 Updating Frontend\src\AppEnhanced.jsx..." -ForegroundColor Green
(Get-Content "Frontend\src\AppEnhanced.jsx") -replace "<h1 className=`"header-title`">$OldName</h1>", "<h1 className=`"header-title`">$NewName</h1>" | Set-Content "Frontend\src\AppEnhanced.jsx"

# Update README.md
Write-Host "📝 Updating README.md..." -ForegroundColor Green
(Get-Content "README.md") -replace "# $OldName", "# $NewName" | Set-Content "README.md"

Write-Host ""
Write-Host "✅ Customization Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Files Updated:" -ForegroundColor Cyan
Write-Host "  - Frontend\index.html"
Write-Host "  - Frontend\src\App.jsx"
Write-Host "  - Frontend\src\AppEnhanced.jsx"
Write-Host "  - README.md"
Write-Host ""
Write-Host "📦 Backups created:" -ForegroundColor Yellow
Write-Host "  - Frontend\index.html.backup"
Write-Host "  - Frontend\src\App.jsx.backup"
Write-Host "  - Frontend\src\AppEnhanced.jsx.backup"
Write-Host "  - README.md.backup"
Write-Host ""
Write-Host "🔄 Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Review changes: git diff"
Write-Host "  2. Rebuild frontend: cd Frontend; npm run build"
Write-Host "  3. Commit changes: git add .; git commit -m 'Customize app name to $NewName'"
Write-Host "  4. Push to GitHub: git push origin main"
Write-Host "  5. Update on EC2: ssh into EC2 and run ./update.sh"
Write-Host ""
