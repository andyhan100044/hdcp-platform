#!/bin/bash

# HDCP Platform Quick Setup Script
# This script automates the initial setup process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║        HDCP Platform - Quick Setup Script                 ║"
echo "║        Universal Data Platform Template                    ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Check prerequisites
print_info "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi
print_success "Docker is installed"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi
print_success "Docker Compose is installed"

# Check available ports
print_info "Checking available ports..."

PORTS=(3000 8000 1337 5432 6379)
PORT_CONFLICTS=()

for port in "${PORTS[@]}"; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        PORT_CONFLICTS+=($port)
    fi
done

if [ ${#PORT_CONFLICTS[@]} -gt 0 ]; then
    print_warning "The following ports are already in use: ${PORT_CONFLICTS[*]}"
    echo "This may cause conflicts. Please free these ports or continue anyway."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Setup cancelled by user"
        exit 1
    fi
else
    print_success "All required ports are available"
fi

# Setup environment file
print_info "Setting up environment file..."

if [ ! -f .env ]; then
    cp .env.example .env
    print_success "Created .env file from template"
    print_warning "Please edit .env file to customize your configuration"
    print_info "Key settings to review:"
    echo "  - SECRET_KEY (change in production)"
    echo "  - ACTIVE_SCENARIO (choose: stock, iot, ecommerce, carbon)"
    echo "  - Database credentials"
else
    print_warning ".env file already exists, skipping..."
fi

# Choose scenario
echo ""
print_info "Choose a scenario to activate:"
echo "1) stock     - Stock price monitoring"
echo "2) iot       - IoT sensor data"
echo "3) ecommerce - E-commerce price tracking"
echo "4) carbon    - Carbon credit tracking"
echo "5) all       - All scenarios (development only)"
echo ""

read -p "Select scenario (1-5) [default: 1]: " choice
choice=${choice:-1}

case $choice in
    1) SCENARIO="stock";;
    2) SCENARIO="iot";;
    3) SCENARIO="ecommerce";;
    4) SCENARIO="carbon";;
    5) SCENARIO="all";;
    *) print_error "Invalid choice"; exit 1;;
esac

print_info "Selected scenario: $SCENARIO"

# Update settings file
print_info "Updating scenario configuration..."

SETTINGS_FILE="apps/api/app/config/settings.py"

if [ -f "$SETTINGS_FILE" ]; then
    # Update ACTIVE_SCENARIO in settings file
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/ACTIVE_SCENARIO = .*/ACTIVE_SCENARIO = \"$SCENARIO\"/" "$SETTINGS_FILE"
    else
        # Linux
        sed -i "s/ACTIVE_SCENARIO = .*/ACTIVE_SCENARIO = \"$SCENARIO\"/" "$SETTINGS_FILE"
    fi
    print_success "Updated scenario to: $SCENARIO"
else
    print_warning "Settings file not found at $SETTINGS_FILE"
    print_warning "Please manually set ACTIVE_SCENARIO = \"$SCENARIO\""
fi

# Build and start services
echo ""
print_info "Building and starting services..."
print_warning "This may take a few minutes on first run..."

docker-compose build --no-cache
docker-compose up -d

# Wait for services to be ready
print_info "Waiting for services to start..."

MAX_WAIT=60
ELAPSED=0

while [ $ELAPSED -lt $MAX_WAIT ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "API is ready!"
        break
    fi
    sleep 2
    ELAPSED=$((ELAPSED + 2))
    echo -n "."
done

if [ $ELAPSED -ge $MAX_WAIT ]; then
    print_warning "API is taking longer than expected to start"
    print_info "Check logs with: docker-compose logs api"
fi

# Display service status
echo ""
print_info "Service Status:"
echo ""
docker-compose ps
echo ""

# Display URLs
print_success "Setup complete! 🎉"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Access your services:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Web Frontend:    http://localhost:3000"
echo "🔌 API:             http://localhost:8000"
echo "📚 API Docs:        http://localhost:8000/docs"
echo "🎛️  CMS Admin:      http://localhost:1337/admin"
echo "🔍 GraphQL:         http://localhost:8000/graphql"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_info "Next steps:"
echo "  1. Visit http://localhost:3000 to see the frontend"
echo "  2. Visit http://localhost:8000/docs to explore the API"
echo "  3. Visit http://localhost:1337/admin to manage content"
echo ""
print_info "Useful commands:"
echo "  View logs:           docker-compose logs -f"
echo "  Stop services:       docker-compose down"
echo "  Restart services:    docker-compose restart"
echo "  Run tests:          ./scripts/test.sh"
echo ""
print_warning "Remember to:"
echo "  - Review and update .env file for production"
echo "  - Change SECRET_KEY and other credentials"
echo "  - Read the documentation at docs/README.md"
echo ""

# Offer to open browser
read -p "Open frontend in browser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:3000
    elif command -v open &> /dev/null; then
        open http://localhost:3000
    else
        print_info "Please open http://localhost:3000 in your browser"
    fi
fi

print_success "Happy coding! 🚀"
