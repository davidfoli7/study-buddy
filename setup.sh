#!/bin/bash

# Study Buddy - Setup Script
# This script sets up the development environment for the Study Buddy project

set -e

echo "🎓 Setting up Study Buddy - AI-Powered Personalized Learning Platform"
echo "================================================================="

# Check if required tools are installed
check_requirements() {
    echo "🔍 Checking requirements..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is required but not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is required but not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js is required but not installed. Please install Node.js first."
        echo "Visit: https://nodejs.org/"
        exit 1
    fi
    
    # Check if Python is installed
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not installed. Please install Python 3 first."
        echo "Visit: https://www.python.org/"
        exit 1
    fi
    
    echo "✅ All requirements met!"
}

# Setup backend environment
setup_backend() {
    echo "🐍 Setting up Backend..."
    
    cd backend
    
    # Copy environment file
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "📝 Created backend/.env file. Please edit it with your configuration."
    fi
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo "🔧 Created Python virtual environment"
    fi
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "📦 Installed Python dependencies"
    
    # Create necessary directories
    mkdir -p uploads ml_models
    
    cd ..
}

# Setup mobile app
setup_mobile() {
    echo "📱 Setting up Mobile App..."
    
    cd mobile
    
    # Copy environment file
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "📝 Created mobile/.env file. Please edit it with your configuration."
    fi
    
    # Install dependencies
    npm install
    echo "📦 Installed Node.js dependencies"
    
    # Create necessary directories
    mkdir -p src/assets/images src/assets/fonts
    
    cd ..
}

# Setup database
setup_database() {
    echo "🗄️ Setting up Database..."
    
    # Create data directory
    mkdir -p data
    
    # Create sample database initialization script
    cat > data/init.sql << EOF
-- Study Buddy Database Initialization
-- This script is run when the PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes for better performance
-- These will be created automatically when tables are created by SQLAlchemy

-- Insert sample data (optional)
-- This can be populated later through the API or admin interface

EOF
    
    echo "📄 Created database initialization script"
}

# Start services
start_services() {
    echo "🚀 Starting Services..."
    
    # Start Docker services
    docker-compose up -d postgres redis
    
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    echo "✅ Database and Redis services started!"
    echo "🔗 PostgreSQL: localhost:5432"
    echo "🔗 Redis: localhost:6379"
}

# Display next steps
show_next_steps() {
    echo ""
    echo "🎉 Setup Complete!"
    echo "================="
    echo ""
    echo "📋 Next Steps:"
    echo "1. Edit configuration files:"
    echo "   - backend/.env (database, Redis, OpenAI API key, etc.)"
    echo "   - mobile/.env (API URL, feature flags, etc.)"
    echo ""
    echo "2. Start the backend API:"
    echo "   cd backend"
    echo "   source venv/bin/activate"
    echo "   uvicorn app.main:app --reload --port 8000"
    echo ""
    echo "3. Start the mobile app:"
    echo "   cd mobile"
    echo "   npm start"
    echo "   # Then run on device/emulator:"
    echo "   npm run android  # or npm run ios"
    echo ""
    echo "4. Access the services:"
    echo "   - API Documentation: http://localhost:8000/docs"
    echo "   - pgAdmin: http://localhost:5050 (admin@studybuddy.ai / admin_password)"
    echo "   - Flower (Celery monitoring): http://localhost:5555"
    echo ""
    echo "📚 Additional Commands:"
    echo "   - Start all services: docker-compose up -d"
    echo "   - Stop all services: docker-compose down"
    echo "   - View logs: docker-compose logs -f"
    echo "   - Reset database: docker-compose down -v && docker-compose up -d"
    echo ""
    echo "🔗 Useful Links:"
    echo "   - React Native Setup: https://reactnative.dev/docs/environment-setup"
    echo "   - FastAPI Documentation: https://fastapi.tiangolo.com/"
    echo "   - OpenAI API: https://platform.openai.com/docs/"
    echo ""
    echo "Happy coding! 🚀"
}

# Main setup flow
main() {
    check_requirements
    setup_backend
    setup_mobile
    setup_database
    start_services
    show_next_steps
}

# Run setup
main