@echo off
echo ========================================
echo GitHub Publishing Helper
echo ========================================
echo.

echo This script will help you publish to GitHub.
echo.
echo BEFORE RUNNING THIS SCRIPT:
echo 1. Create a new repository on GitHub
echo 2. Copy the repository URL
echo.

set /p REPO_URL="Enter your GitHub repository URL (e.g., https://github.com/username/repo.git): "

if "%REPO_URL%"=="" (
    echo ERROR: Repository URL cannot be empty
    pause
    exit /b 1
)

echo.
echo Adding remote repository...
git remote add origin %REPO_URL%

if %errorlevel% neq 0 (
    echo.
    echo Remote might already exist. Trying to update...
    git remote set-url origin %REPO_URL%
)

echo.
echo Verifying remote...
git remote -v

echo.
echo Pushing to GitHub...
git push -u origin main

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo PUSH FAILED
    echo ========================================
    echo.
    echo Possible reasons:
    echo 1. Authentication failed - You need a Personal Access Token
    echo 2. Repository doesn't exist on GitHub
    echo 3. Network connection issue
    echo.
    echo To create a Personal Access Token:
    echo 1. Go to: https://github.com/settings/tokens
    echo 2. Click "Generate new token (classic)"
    echo 3. Select "repo" scope
    echo 4. Copy the token and use it as your password
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo SUCCESS!
echo ========================================
echo.
echo Your project has been published to GitHub!
echo Repository URL: %REPO_URL%
echo.
echo Next steps:
echo 1. Visit your repository on GitHub
echo 2. Add topics/tags for better discoverability
echo 3. Share the URL with your team
echo.
pause
