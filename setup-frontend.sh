#!/bin/bash
# Frontend Setup Script for macOS
# Installs Node.js and starts the development server

set -e

echo "🚀 PhonemeSync Frontend Setup"
echo "=============================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "📦 Installing Node.js via Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew not found. Please install Homebrew first:"
        echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    brew install node
fi

echo "✓ Node.js version: $(node --version)"
echo "✓ npm version: $(npm --version)"

# Install pnpm globally
echo ""
echo "📦 Installing pnpm..."
npm install -g pnpm
echo "✓ pnpm version: $(pnpm --version)"

# Navigate to frontend directory
cd "$(dirname "$0")/phonemesync/frontend"
echo ""
echo "📁 Working directory: $(pwd)"

# Install dependencies
echo ""
echo "📦 Installing frontend dependencies..."
pnpm install

# Create .env.local if it doesn't exist
if [ ! -f .env.local ]; then
    echo ""
    echo "⚙️  Creating .env.local..."
    cp .env.example .env.local
fi

# Start development server
echo ""
echo "🎉 Starting development server..."
echo "📱 Frontend will be available at: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000"
echo ""
pnpm dev
