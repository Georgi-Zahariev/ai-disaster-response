#!/bin/bash
# Quick setup script for the frontend

echo "🚀 Setting up AI Disaster Response Frontend..."
echo ""

# Check if we're in the frontend directory
if [ ! -f "package.json" ]; then
  echo "❌ Error: Run this script from the frontend/ directory"
  exit 1
fi

echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
  echo "❌ npm install failed"
  exit 1
fi

echo ""
echo "✅ Frontend setup complete!"
echo ""
echo "To start the development server:"
echo "  npm run dev"
echo ""
echo "The app will be available at http://localhost:3000"
echo ""
