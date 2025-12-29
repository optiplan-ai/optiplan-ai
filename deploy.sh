#!/bin/bash

# OptiPlan AI Service - Vercel Deployment Script
# This script automates the deployment process to Vercel

echo "🚀 OptiPlan AI Service - Vercel Deployment"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the ai/ directory"
    echo "   Current directory should contain main.py"
    exit 1
fi

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "📦 Installing Vercel CLI..."
    npm install -g vercel
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Vercel CLI"
        exit 1
    fi
else
    echo "✅ Vercel CLI is already installed"
fi

# Check for required files
echo "🔍 Checking required files..."
required_files=("main.py" "PineconeSDK.py" "configs.py" "requirements.txt" "vercel.json")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (missing)"
        missing_files=true
    fi
done

if [ "$missing_files" = true ]; then
    echo "❌ Missing required files. Please ensure all files are present."
    exit 1
fi

# Check environment variables
echo "🔧 Checking environment variables..."
if [ -f ".env" ]; then
    echo "  ✅ .env file found"
    if grep -q "GOOGLE_API_KEY" .env && grep -q "PINECONE_API_KEY" .env; then
        echo "  ✅ Required API keys found in .env"
    else
        echo "  ⚠️  .env file exists but may be missing required keys"
        echo "     Make sure GOOGLE_API_KEY and PINECONE_API_KEY are set"
    fi
else
    echo "  ⚠️  .env file not found (this is OK for production deployment)"
    echo "     Remember to set environment variables in Vercel dashboard"
fi

# Test Gemini embeddings if possible
if [ -f ".env" ] && grep -q "GOOGLE_API_KEY" .env; then
    echo "🧪 Testing Gemini embeddings..."
    python test_gemini_embeddings.py
    if [ $? -eq 0 ]; then
        echo "  ✅ Gemini embeddings test passed"
    else
        echo "  ⚠️  Gemini embeddings test failed"
        echo "     This might be due to API key issues or network connectivity"
        echo "     Deployment will continue, but please verify your API keys"
    fi
else
    echo "🧪 Skipping embeddings test (no GOOGLE_API_KEY found)"
fi

# Deploy to Vercel
echo "🚀 Deploying to Vercel..."
vercel --prod

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Deployment successful!"
    echo ""
    echo "Next steps:"
    echo "1. Set environment variables in Vercel dashboard:"
    echo "   - GOOGLE_API_KEY"
    echo "   - PINECONE_API_KEY"
    echo ""
    echo "2. Test your deployed API:"
    echo "   curl https://your-project.vercel.app/health-check"
    echo ""
    echo "3. View API documentation:"
    echo "   https://your-project.vercel.app/docs"
    echo ""
    echo "📖 For detailed instructions, see DEPLOYMENT_GUIDE.md"
else
    echo "❌ Deployment failed"
    echo "Check the error messages above and try again"
    exit 1
fi 