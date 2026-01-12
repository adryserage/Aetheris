# =============================================================================
# Aetheris Local Setup Script (Windows PowerShell)
# =============================================================================
#
# This script helps you set up Aetheris locally to view and run analysis
# from CI/CD artifacts or fresh installations.
#
# Usage:
#   .\setup-local.ps1
#
# =============================================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║                    Aetheris Local Setup                        ║" -ForegroundColor Blue
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""

# Check Python version
Write-Host "[1/4] Checking Python version..." -ForegroundColor Blue
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)") {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        if ($major -ge 3 -and $minor -ge 9) {
            Write-Host "  ✓ $pythonVersion found" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Python 3.9+ required (found $pythonVersion)" -ForegroundColor Red
            Write-Host "  Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
            exit 1
        }
    }
} catch {
    Write-Host "  ✗ Python not found" -ForegroundColor Red
    Write-Host "  Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check if Aetheris is installed
Write-Host "[2/4] Checking Aetheris installation..." -ForegroundColor Blue
try {
    $aetherisVersion = aetheris --version 2>&1
    Write-Host "  ✓ Aetheris $aetherisVersion found" -ForegroundColor Green
} catch {
    Write-Host "  ! Aetheris not installed" -ForegroundColor Yellow
    Write-Host "  Installing..."
    pip install adryserage-aetheris
    Write-Host "  ✓ Aetheris installed" -ForegroundColor Green
}

# Check API key
Write-Host "[3/4] Checking API key configuration..." -ForegroundColor Blue
$hasApiKey = $false
if ($env:GEMINI_API_KEY -or $env:OPENAI_API_KEY -or $env:ANTHROPIC_API_KEY) {
    Write-Host "  ✓ API key found in environment" -ForegroundColor Green
    $hasApiKey = $true
} else {
    Write-Host "  ! No API key found" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  To run analyses, you need an AI API key."
    Write-Host "  Set one of the following environment variables:"
    Write-Host ""
    Write-Host '    $env:GEMINI_API_KEY = "your_key_here"     # Recommended (free tier)'
    Write-Host '    $env:OPENAI_API_KEY = "your_key_here"'
    Write-Host '    $env:ANTHROPIC_API_KEY = "your_key_here"'
    Write-Host ""
    Write-Host "  Get a free Gemini API key: https://ai.google.dev"
    Write-Host ""
}

# Check for analysis results
Write-Host "[4/4] Checking for analysis results..." -ForegroundColor Blue
$analysisPath = "docs\analyses"
$parentPath = "..\docs\analyses"

if (Test-Path $analysisPath) {
    $fileCount = (Get-ChildItem -Path $analysisPath -Filter "*.md" -Recurse).Count
    Write-Host "  ✓ Found $fileCount analysis reports in $analysisPath" -ForegroundColor Green
    Write-Host ""
    Write-Host "Analysis results available!" -ForegroundColor Green
    Write-Host "  Open $analysisPath in your browser or Markdown viewer"
} elseif (Test-Path $parentPath) {
    $fileCount = (Get-ChildItem -Path $parentPath -Filter "*.md" -Recurse).Count
    Write-Host "  ✓ Found $fileCount analysis reports in $parentPath" -ForegroundColor Green
    Write-Host ""
    Write-Host "Analysis results available!" -ForegroundColor Green
    Write-Host "  Open $parentPath in your browser or Markdown viewer"
} else {
    Write-Host "  ! No analysis results found" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Run Aetheris to generate analysis:"
    Write-Host "    aetheris analysis"
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Blue
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Quick commands:"
Write-Host "  aetheris analysis                    # Run full analysis"
Write-Host "  aetheris analysis --reanalyze        # Analyze changed files only"
Write-Host "  aetheris analysis --profile safe     # Run in safe mode"
Write-Host "  aetheris stats                       # View statistics"
Write-Host ""
Write-Host "Documentation: https://adryserage.github.io/aetheris/"
Write-Host "═══════════════════════════════════════════════════════════════════" -ForegroundColor Blue
