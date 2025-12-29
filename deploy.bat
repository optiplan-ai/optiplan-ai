@echo off
:: OptiPlan AI Service - Vercel Deployment Script (Windows)
:: This script automates the deployment process to Vercel

echo 🚀 OptiPlan AI Service - Vercel Deployment
echo ==========================================

:: Check if we're in the right directory
if not exist "main.py" (
    echo ❌ Error: Please run this script from the ai\ directory
    echo    Current directory should contain main.py
    pause
    exit /b 1
)

:: Check if vercel CLI is installed
where vercel >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 📦 Installing Vercel CLI...
    npm install -g vercel
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Failed to install Vercel CLI
        pause
        exit /b 1
    )
) else (
    echo ✅ Vercel CLI is already installed
)

:: Check for required files
echo 🔍 Checking required files...
set missing_files=0

if exist "main.py" (
    echo   ✅ main.py
) else (
    echo   ❌ main.py ^(missing^)
    set missing_files=1
)

if exist "PineconeSDK.py" (
    echo   ✅ PineconeSDK.py
) else (
    echo   ❌ PineconeSDK.py ^(missing^)
    set missing_files=1
)

if exist "configs.py" (
    echo   ✅ configs.py
) else (
    echo   ❌ configs.py ^(missing^)
    set missing_files=1
)

if exist "requirements.txt" (
    echo   ✅ requirements.txt
) else (
    echo   ❌ requirements.txt ^(missing^)
    set missing_files=1
)

if exist "vercel.json" (
    echo   ✅ vercel.json
) else (
    echo   ❌ vercel.json ^(missing^)
    set missing_files=1
)

if %missing_files% EQU 1 (
    echo ❌ Missing required files. Please ensure all files are present.
    pause
    exit /b 1
)

:: Check environment variables
echo 🔧 Checking environment variables...
if exist ".env" (
    echo   ✅ .env file found
    findstr /C:"GOOGLE_API_KEY" .env >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        findstr /C:"PINECONE_API_KEY" .env >nul 2>nul
        if %ERRORLEVEL% EQU 0 (
            echo   ✅ Required API keys found in .env
        ) else (
            echo   ⚠️  .env file missing PINECONE_API_KEY
        )
    ) else (
        echo   ⚠️  .env file missing GOOGLE_API_KEY
    )
) else (
    echo   ⚠️  .env file not found ^(this is OK for production deployment^)
    echo      Remember to set environment variables in Vercel dashboard
)

:: Test Gemini embeddings if possible
if exist ".env" (
    findstr /C:"GOOGLE_API_KEY" .env >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo 🧪 Testing Gemini embeddings...
        python test_gemini_embeddings.py
        if %ERRORLEVEL% EQU 0 (
            echo   ✅ Gemini embeddings test passed
        ) else (
            echo   ⚠️  Gemini embeddings test failed
            echo      This might be due to API key issues or network connectivity
            echo      Deployment will continue, but please verify your API keys
        )
    ) else (
        echo 🧪 Skipping embeddings test ^(no GOOGLE_API_KEY found^)
    )
) else (
    echo 🧪 Skipping embeddings test ^(no .env file found^)
)

:: Deploy to Vercel
echo 🚀 Deploying to Vercel...
vercel --prod

if %ERRORLEVEL% EQU 0 (
    echo.
    echo 🎉 Deployment successful!
    echo.
    echo Next steps:
    echo 1. Set environment variables in Vercel dashboard:
    echo    - GOOGLE_API_KEY
    echo    - PINECONE_API_KEY
    echo.
    echo 2. Test your deployed API:
    echo    curl https://your-project.vercel.app/health-check
    echo.
    echo 3. View API documentation:
    echo    https://your-project.vercel.app/docs
    echo.
    echo 📖 For detailed instructions, see DEPLOYMENT_GUIDE.md
) else (
    echo ❌ Deployment failed
    echo Check the error messages above and try again
)

pause 