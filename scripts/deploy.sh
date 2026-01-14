#!/bin/bash
# deploy.sh - Deployment script for Reddit Agent
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="${PROJECT_DIR}/.env"

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    if [[ ! -f "$ENV_FILE" ]]; then
        log_error ".env file not found at $ENV_FILE"
        log_info "Copy .env.example to .env and configure it"
        exit 1
    fi
    
    log_info "✓ Prerequisites check passed"
}

# Validate environment
validate_env() {
    log_info "Validating environment configuration..."
    
    source "$ENV_FILE"
    
    required_vars=(
        "REDDIT_CLIENT_ID"
        "REDDIT_CLIENT_SECRET"
        "REDDIT_USERNAME"
        "REDDIT_PASSWORD"
        "REDDIT_USER_AGENT"
        "ALLOWED_SUBREDDITS"
        "WEBHOOK_URL"
        "WEBHOOK_SECRET"
    )
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            log_error "Missing required environment variable: $var"
            exit 1
        fi
    done
    
    log_info "✓ Environment validation passed"
}

# Build images
build() {
    log_info "Building Docker images..."
    cd "$PROJECT_DIR"
    docker compose build --no-cache
    log_info "✓ Build completed"
}

# Run database migrations
migrate() {
    log_info "Running database migrations..."
    cd "$PROJECT_DIR"
    docker compose run --rm agent python -c "
from models.database import init_db
init_db()
print('Migrations completed')
"
    log_info "✓ Migrations completed"
}

# Start services
start() {
    log_info "Starting services..."
    cd "$PROJECT_DIR"
    docker compose up -d
    log_info "✓ Services started"
    
    # Wait for health checks
    sleep 5
    docker compose ps
}

# Stop services
stop() {
    log_info "Stopping services..."
    cd "$PROJECT_DIR"
    docker compose down
    log_info "✓ Services stopped"
}

# View logs
logs() {
    cd "$PROJECT_DIR"
    docker compose logs -f "${1:-}"
}

# Run tests
test() {
    log_info "Running tests..."
    cd "$PROJECT_DIR"
    docker compose run --rm agent pytest tests/ -v
}

# Health check
health() {
    log_info "Checking service health..."
    cd "$PROJECT_DIR"
    
    # Check callback server
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health | grep -q "200"; then
        log_info "✓ Callback server: healthy"
    else
        log_warn "✗ Callback server: unhealthy"
    fi
    
    # Check database
    if docker compose exec -T db pg_isready -U postgres &> /dev/null; then
        log_info "✓ Database: healthy"
    else
        log_warn "✗ Database: unhealthy"
    fi
}

# Full deployment
deploy() {
    check_prerequisites
    validate_env
    build
    stop
    start
    migrate
    health
    
    log_info "🚀 Deployment completed successfully!"
}

# Show usage
usage() {
    echo "Usage: $0 {deploy|build|start|stop|logs|test|health|migrate}"
    echo ""
    echo "Commands:"
    echo "  deploy  - Full deployment (build, start, migrate)"
    echo "  build   - Build Docker images"
    echo "  start   - Start all services"
    echo "  stop    - Stop all services"
    echo "  logs    - View logs (optionally specify service)"
    echo "  test    - Run test suite"
    echo "  health  - Check service health"
    echo "  migrate - Run database migrations"
}

# Main
case "${1:-}" in
    deploy)  deploy ;;
    build)   build ;;
    start)   start ;;
    stop)    stop ;;
    logs)    logs "${2:-}" ;;
    test)    test ;;
    health)  health ;;
    migrate) migrate ;;
    *)       usage ;;
esac
