<#
.SYNOPSIS
    Creates an AI-friendly zip package of Digital Watercolors (excludes frames and audio)

.PARAMETER Mode
    lite     - Core files only (~30KB) - DEFAULT
    standard - Includes scene-manager.py (~50KB)

.EXAMPLE
    .\Create-AIPackage.ps1
    .\Create-AIPackage.ps1 -Mode standard
#>

param(
    [ValidateSet("lite", "standard")]
    [string]$Mode = "lite"
)

$ErrorActionPreference = "Stop"

# Get script location (project root)
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Timestamp = Get-Date -Format "yyyy-MM-dd-HHmm"
$OutputName = "digital-watercolors-$Mode-$Timestamp.zip"
$OutputPath = Join-Path $ProjectRoot $OutputName

# Temp folder for staging
$TempDir = Join-Path $env:TEMP "digital-watercolors-ai-package"
if (Test-Path $TempDir) { Remove-Item $TempDir -Recurse -Force }
New-Item -ItemType Directory -Path $TempDir | Out-Null

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Digital Watercolors AI Package Creator" -ForegroundColor Cyan
Write-Host "  Mode: $Mode" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Define what to include
$LiteFiles = @(
    "index.html",
    "scenes.js",
    "README.md"
)

$StandardExtras = @(
    "scene-manager.py"
)

# Build file list based on mode
$FilesToInclude = $LiteFiles
if ($Mode -eq "standard") {
    $FilesToInclude += $StandardExtras
}

# Copy files to temp directory
$CopiedCount = 0
$TotalSize = 0

foreach ($RelPath in $FilesToInclude) {
    $SourcePath = Join-Path $ProjectRoot $RelPath
    $DestPath = Join-Path $TempDir $RelPath
    
    if (Test-Path $SourcePath) {
        # Create directory structure
        $DestDir = Split-Path -Parent $DestPath
        if ($DestDir -and !(Test-Path $DestDir)) {
            New-Item -ItemType Directory -Path $DestDir -Force | Out-Null
        }
        
        Copy-Item $SourcePath $DestPath
        $FileSize = (Get-Item $SourcePath).Length
        $TotalSize += $FileSize
        $CopiedCount++
        
        $SizeKB = [math]::Round($FileSize / 1KB, 1)
        Write-Host "  + $RelPath ($SizeKB KB)" -ForegroundColor Green
    } else {
        Write-Host "  ? $RelPath (not found)" -ForegroundColor Yellow
    }
}

# Find and copy scene index.html files (but NOT frames or audio)
$ScenesDir = Join-Path $ProjectRoot "scenes"
if (Test-Path $ScenesDir) {
    $SceneFolders = Get-ChildItem -Path $ScenesDir -Directory
    
    foreach ($SceneFolder in $SceneFolders) {
        $SceneIndexPath = Join-Path $SceneFolder.FullName "index.html"
        
        if (Test-Path $SceneIndexPath) {
            $RelPath = "scenes\$($SceneFolder.Name)\index.html"
            $DestPath = Join-Path $TempDir $RelPath
            $DestDir = Split-Path -Parent $DestPath
            
            if (!(Test-Path $DestDir)) {
                New-Item -ItemType Directory -Path $DestDir -Force | Out-Null
            }
            
            Copy-Item $SceneIndexPath $DestPath
            $FileSize = (Get-Item $SceneIndexPath).Length
            $TotalSize += $FileSize
            $CopiedCount++
            
            $SizeKB = [math]::Round($FileSize / 1KB, 1)
            Write-Host "  + $RelPath ($SizeKB KB)" -ForegroundColor Green
        }
    }
}

# Add the guide
$GuidePath = Join-Path $TempDir "AI-ZIP-GUIDE.md"
$GuideContent = @"
# Digital Watercolors - AI Package ($Mode)

Created: $Timestamp

## Included Files
- index.html (hub page)
- scenes.js (scene configuration)
- README.md
- scenes/*/index.html (scene templates)
$(if ($Mode -eq "standard") { "- scene-manager.py (management tool)" })

## Excluded (Large Files)
- hub-frames/ (~5MB of animation PNGs)
- scenes/*/frames/ (animation frames per scene)
- scenes/*/audio/ (ambient MP3s)
- .git/ folder

## Notes
- scenes.js defines which scenes appear in the hub menu
- Each scene's index.html contains sceneConfig with frameCount, audio settings
- Animation frames are named frame-000.png, frame-001.png, etc.
- scene-manager.py auto-renames uploaded frames and updates frameCount
"@
Set-Content -Path $GuidePath -Value $GuideContent
Write-Host "  + AI-ZIP-GUIDE.md (generated)" -ForegroundColor Cyan

# Create zip
Write-Host ""
Write-Host "Creating zip..." -ForegroundColor Cyan

if (Test-Path $OutputPath) { Remove-Item $OutputPath }
Compress-Archive -Path "$TempDir\*" -DestinationPath $OutputPath -CompressionLevel Optimal

# Cleanup temp
Remove-Item $TempDir -Recurse -Force

# Report
$ZipSize = (Get-Item $OutputPath).Length
$ZipSizeKB = [math]::Round($ZipSize / 1KB, 1)

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Package created successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Files:    $CopiedCount" -ForegroundColor White
Write-Host "  Size:     $ZipSizeKB KB" -ForegroundColor White
Write-Host "  Output:   $OutputName" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Ready to upload to Claude!" -ForegroundColor Cyan
Write-Host ""
