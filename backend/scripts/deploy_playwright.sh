#!/bin/bash

# Playwright MCP Server Deployment Script
# This script handles the deployment of Playwright MCP server components

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
LOG_FILE="$PROJECT_ROOT/logs/deployment-$(date +%Y%m%d_%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_info() {
    log "${BLUE}[INFO]${NC} $1"
}

log_success() {
    log "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    log "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    log "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    echo "Playwright MCP Server Deployment Script"
    echo ""
    echo "Usage: $0 [OPTIONS] COMMAND"
    echo ""
    echo "Commands:"
    echo "  install          Install dependencies and setup environment"
    echo "  build            Build Docker images"
    echo "  deploy           Deploy Playwright MCP server"
    echo "  start            Start Playwright services"
    echo "  stop             Stop Playwright services"
    echo "  restart          Restart Playwright services"
    echo "  status           Check service status"
    echo "  logs             Show service logs"
    echo "  cleanup          Clean up containers and images"
    echo "  health-check     Run health checks"
    echo "  backup           Backup database and artifacts"
    echo "  restore          Restore from backup"
    echo "  update           Update to latest version"
    echo "  rollback         Rollback to previous version"
    echo ""
    echo "Options:"
    echo "  -h, --help       Show this help message"
    echo "  -v, --verbose    Verbose output"
    echo "  -e, --env        Environment (development|production|staging)"
    echo "  -d, --debug      Enable debug mode"
    echo ""
}

# Parse command line arguments
VERBOSE=false
ENVIRONMENT="development"
DEBUG=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -d|--debug)
            DEBUG=true
            shift
            ;;
        install|build|deploy|start|stop|restart|status|logs|cleanup|health-check|backup|restore|update|rollback)
            COMMAND="$1"
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

if [ -z "$COMMAND" ]; then
    log_error "No command specified"
    show_help
    exit 1
fi

# Create directories
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/backups"
mkdir -p "$PROJECT_ROOT/playwright-browsers"
mkdir -p "$PROJECT_ROOT/playwright-artifacts"
mkdir -p "$PROJECT_ROOT/playwright-logs"
mkdir -p "$PROJECT_ROOT/playwright-temp"
mkdir -p "$PROJECT_ROOT/playwright-metrics"

# Load environment variables
load_env() {
    if [ -f "$PROJECT_ROOT/.env.$ENVIRONMENT" ]; then
        log_info "Loading environment variables from .$ENVIRONMENT"
        set -a
        source "$PROJECT_ROOT/.env.$ENVIRONMENT"
        set +a
    elif [ -f "$PROJECT_ROOT/.env" ]; then
        log_info "Loading environment variables from .env"
        set -a
        source "$PROJECT_ROOT/.env"
        set +a
    else
        log_warning "No environment file found, using defaults"
    fi
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker is not running"
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if required directories exist
    if [ ! -d "$BACKEND_DIR" ]; then
        log_error "Backend directory not found: $BACKEND_DIR"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Install dependencies
install_dependencies() {
    log_info "Installing dependencies..."
    
    cd "$BACKEND_DIR"
    
    # Install Python dependencies
    if [ -f "requirements.txt" ]; then
        log_info "Installing Python dependencies..."
        pip install -r requirements.txt
    fi
    
    # Install Playwright browsers
    log_info "Installing Playwright browsers..."
    python -m playwright install chromium firefox webkit
    
    # Install Playwright system dependencies
    log_info "Installing Playwright system dependencies..."
    python -m playwright install-deps
    
    log_success "Dependencies installed successfully"
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    
    cd "$PROJECT_ROOT"
    
    # Set build arguments
    export DOCKER_TARGET="$ENVIRONMENT"
    export PLAYWRIGHT_BROWSERS_PATH="/ms-playwright"
    
    # Build the Playwright MCP server image
    docker build -f "$BACKEND_DIR/Dockerfile.playwright" \
        --target "$ENVIRONMENT" \
        --build-arg ENVIRONMENT="$ENVIRONMENT" \
        --build-arg PLAYWRIGHT_BROWSERS_PATH="$PLAYWRIGHT_BROWSERS_PATH" \
        -t chronos-playwright-mcp:"$ENVIRONMENT" \
        "$BACKEND_DIR"
    
    log_success "Docker images built successfully"
}

# Deploy services
deploy() {
    log_info "Deploying Playwright MCP server..."
    
    cd "$PROJECT_ROOT"
    
    # Create network if it doesn't exist
    if ! docker network ls | grep -q chronos-network; then
        log_info "Creating Docker network..."
        docker network create chronos-network
    fi
    
    # Start services
    docker-compose -f docker-compose.playwright.yml --env-file .env."$ENVIRONMENT" up -d
    
    log_success "Playwright MCP server deployed successfully"
}

# Start services
start_services() {
    log_info "Starting Playwright services..."
    
    cd "$PROJECT_ROOT"
    
    docker-compose -f docker-compose.playwright.yml --env-file .env."$ENVIRONMENT" start
    
    log_success "Playwright services started"
}

# Stop services
stop_services() {
    log_info "Stopping Playwright services..."
    
    cd "$PROJECT_ROOT"
    
    docker-compose -f docker-compose.playwright.yml --env-file .env."$ENVIRONMENT" stop
    
    log_success "Playwright services stopped"
}

# Restart services
restart_services() {
    log_info "Restarting Playwright services..."
    
    cd "$PROJECT_ROOT"
    
    docker-compose -f docker-compose.playwright.yml --env-file .env."$ENVIRONMENT" restart
    
    log_success "Playwright services restarted"
}

# Check service status
check_status() {
    log_info "Checking service status..."
    
    cd "$PROJECT_ROOT"
    
    docker-compose -f docker-compose.playwright.yml --env-file .env."$ENVIRONMENT" ps
    
    # Check if services are healthy
    if docker-compose -f docker-compose.playwright.yml --env-file .env."$ENVIRONMENT" ps | grep -q "Up (healthy)"; then
        log_success "All services are healthy"
    else
        log_warning "Some services are not healthy"
    fi
}

# Show logs
show_logs() {
    log_info "Showing service logs..."
    
    cd "$PROJECT_ROOT"
    
    if [ "$VERBOSE" = true ]; then
        docker-compose -f docker-compose.playwright.yml --env-file .env."$ENVIRONMENT" logs -f
    else
        docker-compose -f docker-compose.playwright.yml --env-file .env."$ENVIRONMENT" logs --tail=100 -f
    fi
}

# Cleanup
cleanup() {
    log_info "Cleaning up containers and images..."
    
    cd "$PROJECT_ROOT"
    
    # Stop and remove containers
    docker-compose -f docker-compose.playwright.yml --env-file .env."$ENVIRONMENT" down
    
    # Remove unused images
    docker image prune -f
    
    log_success "Cleanup completed"
}

# Health check
health_check() {
    log_info "Running health checks..."
    
    # Check if containers are running
    if ! docker ps | grep -q chronos-playwright-mcp; then
        log_error "Playwright MCP container is not running"
        return 1
    fi
    
    # Check HTTP health endpoint
    if command -v curl &> /dev/null; then
        local health_url="http://localhost:${PLAYWRIGHT_MCP_PORT:-8003}/health"
        if curl -f -s "$health_url" > /dev/null; then
            log_success "Health check passed"
        else
            log_error "Health check failed"
            return 1
        fi
    else
        log_warning "curl not available, skipping HTTP health check"
    fi
    
    # Check database connection
    cd "$BACKEND_DIR"
    python -c "
import sys
sys.path.append('.')
from app.core.database import engine
try:
    with engine.connect() as conn:
        conn.execute('SELECT 1')
    print('Database connection: OK')
except Exception as e:
    print(f'Database connection: FAILED - {e}')
    sys.exit(1)
"
    
    log_success "Health checks completed"
}

# Backup
backup() {
    log_info "Creating backup..."
    
    local backup_dir="$PROJECT_ROOT/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup database
    if command -v pg_dump &> /dev/null; then
        pg_dump "${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/chronos_ai}" \
            > "$backup_dir/database.sql"
        log_info "Database backed up to $backup_dir/database.sql"
    fi
    
    # Backup artifacts
    if [ -d "$PROJECT_ROOT/playwright-artifacts" ]; then
        tar -czf "$backup_dir/artifacts.tar.gz" -C "$PROJECT_ROOT" playwright-artifacts/
        log_info "Artifacts backed up to $backup_dir/artifacts.tar.gz"
    fi
    
    # Backup logs
    if [ -d "$PROJECT_ROOT/playwright-logs" ]; then
        tar -czf "$backup_dir/logs.tar.gz" -C "$PROJECT_ROOT" playwright-logs/
        log_info "Logs backed up to $backup_dir/logs.tar.gz"
    fi
    
    log_success "Backup completed: $backup_dir"
}

# Restore
restore() {
    if [ -z "$1" ]; then
        log_error "Backup directory not specified"
        exit 1
    fi
    
    local backup_dir="$1"
    
    if [ ! -d "$backup_dir" ]; then
        log_error "Backup directory not found: $backup_dir"
        exit 1
    fi
    
    log_info "Restoring from backup: $backup_dir"
    
    # Stop services
    stop_services
    
    # Restore database
    if [ -f "$backup_dir/database.sql" ] && command -v psql &> /dev/null; then
        psql "${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/chronos_ai}" \
            < "$backup_dir/database.sql"
        log_info "Database restored from $backup_dir/database.sql"
    fi
    
    # Restore artifacts
    if [ -f "$backup_dir/artifacts.tar.gz" ]; then
        tar -xzf "$backup_dir/artifacts.tar.gz" -C "$PROJECT_ROOT"
        log_info "Artifacts restored from $backup_dir/artifacts.tar.gz"
    fi
    
    # Restore logs
    if [ -f "$backup_dir/logs.tar.gz" ]; then
        tar -xzf "$backup_dir/logs.tar.gz" -C "$PROJECT_ROOT"
        log_info "Logs restored from $backup_dir/logs.tar.gz"
    fi
    
    # Start services
    start_services
    
    log_success "Restore completed"
}

# Update
update() {
    log_info "Updating Playwright MCP server..."
    
    # Pull latest changes
    git pull origin main || log_warning "Could not pull latest changes"
    
    # Rebuild images
    build_images
    
    # Redeploy
    deploy
    
    log_success "Update completed"
}

# Rollback
rollback() {
    log_info "Rolling back Playwright MCP server..."
    
    # This would require a more sophisticated rollback mechanism
    # For now, just restart services
    restart_services
    
    log_success "Rollback completed"
}

# Main execution
main() {
    log_info "Starting Playwright MCP Server Deployment - Command: $COMMAND, Environment: $ENVIRONMENT"
    
    load_env
    check_prerequisites
    
    case $COMMAND in
        install)
            install_dependencies
            ;;
        build)
            build_images
            ;;
        deploy)
            build_images
            deploy
            ;;
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        status)
            check_status
            ;;
        logs)
            show_logs
            ;;
        cleanup)
            cleanup
            ;;
        health-check)
            health_check
            ;;
        backup)
            backup
            ;;
        restore)
            restore "$1"
            ;;
        update)
            update
            ;;
        rollback)
            rollback
            ;;
        *)
            log_error "Unknown command: $COMMAND"
            show_help
            exit 1
            ;;
    esac
    
    log_success "Deployment script completed successfully"
}

# Execute main function
main "$@"