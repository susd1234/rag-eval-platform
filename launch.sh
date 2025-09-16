#!/bin/bash

# SME Evaluation Platform Launch Script
# This script starts both backend and frontend applications in separate terminals

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
BACKEND_DIR="agen-sme-eval-be"
FRONTEND_DIR="agen-sme-eval-ui"
BACKEND_PORT=9777
FRONTEND_PORT=3000
HEALTH_CHECK_TIMEOUT=30
HEALTH_CHECK_INTERVAL=2

# Function to print colored output
print_status() {
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

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local timeout=$3
    local interval=$4
    
    print_status "Waiting for $service_name to be ready at $url..."
    
    local elapsed=0
    while [ $elapsed -lt $timeout ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        sleep $interval
        elapsed=$((elapsed + interval))
        echo -n "."
    done
    
    print_error "$service_name failed to start within ${timeout}s"
    return 1
}

# Function to start backend
start_backend() {
    print_header "Starting Backend Service"
    
    cd "$BACKEND_DIR"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Install dependencies
    print_status "Installing backend dependencies..."
    pip install -r requirements.txt >/dev/null 2>&1
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_warning "No .env file found. Creating from template..."
        cp env.example .env
        print_warning "Please edit .env file with your API keys before running the service."
        print_warning "Required: OPENAI_API_KEY or ANTHROPIC_API_KEY"
    fi
    
    # Start backend in new terminal
    print_status "Starting backend service on port $BACKEND_PORT..."
    
    # Use osascript to open new Terminal window for backend
    osascript -e "tell application \"Terminal\" to do script \"cd '$(pwd)' && source venv/bin/activate && echo '🚀 Backend starting on port $BACKEND_PORT...' && python app.py\""
    
    cd ..
}

# Function to start frontend
start_frontend() {
    print_header "Starting Frontend Service"
    
    cd "$FRONTEND_DIR"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    # Start frontend in new terminal
    print_status "Starting frontend service on port $FRONTEND_PORT..."
    
    # Use osascript to open new Terminal window for frontend
    osascript -e "tell application \"Terminal\" to do script \"cd '$(pwd)' && echo '🎨 Frontend starting on port $FRONTEND_PORT...' && npm run dev\""
    
    cd ..
}

# Function to check if services are running
check_services() {
    print_header "Checking Service Status"
    
    # Check backend
    if check_port $BACKEND_PORT; then
        print_success "Backend is running on port $BACKEND_PORT"
    else
        print_error "Backend is not running on port $BACKEND_PORT"
        return 1
    fi
    
    # Check frontend
    if check_port $FRONTEND_PORT; then
        print_success "Frontend is running on port $FRONTEND_PORT"
    else
        print_error "Frontend is not running on port $FRONTEND_PORT"
        return 1
    fi
    
    return 0
}

# Function to display final status
display_final_status() {
    print_header "Application Status"
    
    echo -e "${CYAN}Backend:${NC} http://localhost:$BACKEND_PORT"
    echo -e "${CYAN}Frontend:${NC} http://localhost:$FRONTEND_PORT"
    echo -e "${CYAN}API Docs:${NC} http://localhost:$BACKEND_PORT/docs"
    echo -e "${CYAN}Health Check:${NC} http://localhost:$BACKEND_PORT/health"
    echo ""
    print_success "Both services are running in separate Terminal windows!"
    print_status "You can now access the SME Evaluation Platform at http://localhost:$FRONTEND_PORT"
}

# Main execution
main() {
    print_header "SME Evaluation Platform Launcher"
    
    # Check if we're in the right directory
    if [ ! -d "$BACKEND_DIR" ] || [ ! -d "$FRONTEND_DIR" ]; then
        print_error "Please run this script from the project root directory"
        print_error "Expected directories: $BACKEND_DIR and $FRONTEND_DIR"
        exit 1
    fi
    
    # Check if ports are already in use
    if check_port $BACKEND_PORT; then
        print_warning "Port $BACKEND_PORT is already in use. Backend might already be running."
    fi
    
    if check_port $FRONTEND_PORT; then
        print_warning "Port $FRONTEND_PORT is already in use. Frontend might already be running."
    fi
    
    # Start services
    start_backend
    sleep 2  # Give backend a moment to start
    start_frontend
    
    print_status "Services are starting in separate Terminal windows..."
    print_status "Waiting for services to be ready..."
    
    # Wait for services to be ready
    sleep 5  # Initial delay for services to start
    
    # Check if services are running
    if check_services; then
        display_final_status
    else
        print_warning "Some services may still be starting up. Please check the Terminal windows."
        print_status "Backend should be available at: http://localhost:$BACKEND_PORT"
        print_status "Frontend should be available at: http://localhost:$FRONTEND_PORT"
    fi
}

# Handle script interruption
trap 'print_warning "Launch script interrupted. Services may still be running in Terminal windows."; exit 1' INT

# Run main function
main "$@"
