#!/bin/bash

# WorkWale.ai Setup Script
echo "🚀 Setting up WorkWale.ai - AI-Powered Job Discovery Platform"
echo "============================================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update the .env file with your API keys and configuration"
    echo "   Required: OPENAI_API_KEY, TWILIO_*, SENDGRID_API_KEY"
    echo ""
fi

# Create uploads directory
echo "📁 Creating uploads directory..."
mkdir -p uploads/resumes
chmod 755 uploads/resumes

# Create logs directory
echo "📄 Creating logs directory..."
mkdir -p logs
chmod 755 logs

# Pull latest images
echo "📦 Pulling Docker images..."
docker-compose pull

# Build custom images
echo "🔨 Building application images..."
docker-compose build

# Start the services
echo "🚀 Starting WorkWale.ai services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose exec backend python -c "
from database.database import engine, Base
Base.metadata.create_all(bind=engine)
print('✅ Database tables created successfully')
"

echo ""
echo "🎉 WorkWale.ai setup completed!"
echo ""
echo "📱 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "📋 Services running:"
echo "   - PostgreSQL Database (port 5432)"
echo "   - Redis Cache (port 6379)"
echo "   - FastAPI Backend (port 8000)"
echo "   - Next.js Frontend (port 3000)"
echo "   - Celery Worker (background tasks)"
echo "   - Celery Beat (scheduled tasks)"
echo ""
echo "🔧 To configure the application:"
echo "   1. Update .env file with your API keys"
echo "   2. Restart services: docker-compose restart"
echo ""
echo "📖 For more information, check the README.md file"
echo ""
echo "🛑 To stop services: docker-compose down"
echo "🔄 To restart services: docker-compose restart"
echo "📊 To view logs: docker-compose logs -f [service_name]"