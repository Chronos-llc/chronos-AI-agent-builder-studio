#!/bin/bash

# Playwright MCP Server Monitoring Script
# This script monitors the health and performance of the Playwright MCP server

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Configuration
LOG_FILE="${PROJECT_ROOT}/logs/playwright_monitor.log"
METRICS_FILE="${PROJECT_ROOT}/logs/playwright_metrics.json"
PID_FILE="${PROJECT_ROOT}/logs/playwright_monitor.pid"
ALERT_LOG="${PROJECT_ROOT}/logs/playwright_alerts.log"

# Monitoring thresholds
CPU_THRESHOLD=80
MEMORY_THRESHOLD=80
DISK_THRESHOLD=90
RESPONSE_TIME_THRESHOLD=5
ERROR_RATE_THRESHOLD=10

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create logs directory if it doesn't exist
mkdir -p "${PROJECT_ROOT}/logs"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_alert() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ALERT: $1" | tee -a "$ALERT_LOG"
}

# Function to check if Playwright service is running
check_service_health() {
    local service_name="$1"
    local port="$2"
    
    if nc -z localhost "$port" 2>/dev/null; then
        echo "running"
    else
        echo "stopped"
    fi
}

# Function to check API health
check_api_health() {
    local endpoint="$1"
    
    local response
    response=$(curl -s -w "%{http_code}" -o /dev/null "$endpoint" || echo "000")
    
    if [[ "$response" == "200" ]]; then
        echo "healthy"
    else
        echo "unhealthy"
    fi
}

# Function to get CPU usage
get_cpu_usage() {
    if command -v ps &> /dev/null; then
        ps aux | grep -E "(python|node|playwright)" | grep -v grep | awk '{sum+=$3} END {print sum}' | cut -d. -f1
    else
        echo "0"
    fi
}

# Function to get memory usage
get_memory_usage() {
    if command -v ps &> /dev/null; then
        ps aux | grep -E "(python|node|playwright)" | grep -v grep | awk '{sum+=$4} END {print sum}' | cut -d. -f1
    else
        echo "0"
    fi
}

# Function to get disk usage
get_disk_usage() {
    df "$PROJECT_ROOT" | tail -1 | awk '{print $5}' | sed 's/%//'
}

# Function to get active browser sessions
get_active_sessions() {
    local count=0
    if command -v ps &> /dev/null; then
        count=$(ps aux | grep -E "(chromium|firefox|webkit)" | grep -v grep | wc -l)
    fi
    echo "$count"
}

# Function to get queue size
get_queue_size() {
    if command -v redis-cli &> /dev/null; then
        redis-cli llen "playwright:queue" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

# Function to get response time
get_response_time() {
    local start_time=$(date +%s.%N)
    curl -s -o /dev/null "http://localhost:8000/api/v1/playwright/health" > /dev/null 2>&1 || echo "0"
    local end_time=$(date +%s.%N)
    local response_time=$(echo "$end_time - $start_time" | bc 2>/dev/null || echo "0")
    printf "%.2f" "$response_time"
}

# Function to send alert
send_alert() {
    local severity="$1"
    local message="$2"
    
    log_alert "[$severity] $message"
    
    # Here you can integrate with alerting systems like:
    # - Slack webhooks
    # - Email notifications
    # - PagerDuty
    # - Prometheus AlertManager
    
    case "$severity" in
        "CRITICAL")
            # Send critical alert (email, SMS, etc.)
            echo "CRITICAL ALERT: $message" | mail -s "Playwright MCP Critical Alert" admin@example.com 2>/dev/null || true
            ;;
        "WARNING")
            # Send warning alert (Slack, etc.)
            echo "WARNING: $message" | curl -X POST -H 'Content-type: application/json' \
                --data "{\"text\":\"WARNING: $message\"}" "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK" 2>/dev/null || true
            ;;
    esac
}

# Function to generate metrics report
generate_metrics() {
    local timestamp=$(date -Iseconds)
    local cpu_usage=$(get_cpu_usage)
    local memory_usage=$(get_memory_usage)
    local disk_usage=$(get_disk_usage)
    local active_sessions=$(get_active_sessions)
    local queue_size=$(get_queue_size)
    local response_time=$(get_response_time)
    local service_status=$(check_service_health "playwright" "8000")
    local api_status=$(check_api_health "http://localhost:8000/api/v1/playwright/health")
    
    # Create JSON metrics
    cat > "$METRICS_FILE" << EOF
{
    "timestamp": "$timestamp",
    "service_status": "$service_status",
    "api_status": "$api_status",
    "cpu_usage": $cpu_usage,
    "memory_usage": $memory_usage,
    "disk_usage": $disk_usage,
    "active_sessions": $active_sessions,
    "queue_size": $queue_size,
    "response_time": $response_time
}
EOF

    log "Metrics generated: CPU=${cpu_usage}%, Memory=${memory_usage}%, Disk=${disk_usage}%, Sessions=$active_sessions, Queue=$queue_size, ResponseTime=${response_time}s"
}

# Function to check thresholds and alerts
check_thresholds() {
    local cpu_usage=$(get_cpu_usage)
    local memory_usage=$(get_memory_usage)
    local disk_usage=$(get_disk_usage)
    local response_time=$(get_response_time)
    local service_status=$(check_service_health "playwright" "8000")
    local api_status=$(check_api_health "http://localhost:8000/api/v1/playwright/health")
    
    # Check service status
    if [[ "$service_status" == "stopped" ]]; then
        send_alert "CRITICAL" "Playwright MCP server is not running"
    fi
    
    # Check API status
    if [[ "$api_status" == "unhealthy" ]]; then
        send_alert "CRITICAL" "Playwright MCP API is unhealthy"
    fi
    
    # Check CPU usage
    if [[ "$cpu_usage" -gt "$CPU_THRESHOLD" ]]; then
        send_alert "WARNING" "High CPU usage: ${cpu_usage}%"
    fi
    
    # Check memory usage
    if [[ "$memory_usage" -gt "$MEMORY_THRESHOLD" ]]; then
        send_alert "WARNING" "High memory usage: ${memory_usage}%"
    fi
    
    # Check disk usage
    if [[ "$disk_usage" -gt "$DISK_THRESHOLD" ]]; then
        send_alert "WARNING" "High disk usage: ${disk_usage}%"
    fi
    
    # Check response time
    if [[ $(echo "$response_time > $RESPONSE_TIME_THRESHOLD" | bc 2>/dev/null || echo "0") -eq 1 ]]; then
        send_alert "WARNING" "High response time: ${response_time}s"
    fi
}

# Function to display status
display_status() {
    echo -e "${GREEN}=== Playwright MCP Server Status ===${NC}"
    echo "Timestamp: $(date)"
    
    local service_status=$(check_service_health "playwright" "8000")
    local api_status=$(check_api_health "http://localhost:8000/api/v1/playwright/health")
    local cpu_usage=$(get_cpu_usage)
    local memory_usage=$(get_memory_usage)
    local disk_usage=$(get_disk_usage)
    local active_sessions=$(get_active_sessions)
    local queue_size=$(get_queue_size)
    local response_time=$(get_response_time)
    
    echo -e "Service Status: ${service_status^^}"
    echo -e "API Status: ${api_status^^}"
    echo "CPU Usage: ${cpu_usage}%"
    echo "Memory Usage: ${memory_usage}%"
    echo "Disk Usage: ${disk_usage}%"
    echo "Active Browser Sessions: $active_sessions"
    echo "Task Queue Size: $queue_size"
    echo "Response Time: ${response_time}s"
    
    # Status indicators
    if [[ "$service_status" == "running" && "$api_status" == "healthy" ]]; then
        echo -e "Overall Status: ${GREEN}HEALTHY${NC}"
    else
        echo -e "Overall Status: ${RED}UNHEALTHY${NC}"
    fi
}

# Function to cleanup old logs
cleanup_logs() {
    # Keep only last 7 days of logs
    find "${PROJECT_ROOT}/logs" -name "*.log" -mtime +7 -delete 2>/dev/null || true
    # Compress logs older than 1 day
    find "${PROJECT_ROOT}/logs" -name "*.log" -mtime +1 -exec gzip {} \; 2>/dev/null || true
}

# Function to restart service if needed
restart_service_if_needed() {
    local service_status=$(check_service_health "playwright" "8000")
    
    if [[ "$service_status" == "stopped" ]]; then
        log "Service is down, attempting to restart..."
        
        # Try to restart using systemd if available
        if command -v systemctl &> /dev/null; then
            systemctl restart chronos-playwright 2>/dev/null || true
        fi
        
        # Try docker-compose restart
        if [[ -f "${PROJECT_ROOT}/docker-compose.playwright.yml" ]]; then
            cd "$PROJECT_ROOT"
            docker-compose -f docker-compose.playwright.yml restart playwright-server 2>/dev/null || true
        fi
        
        sleep 5
        local new_status=$(check_service_health "playwright" "8000")
        
        if [[ "$new_status" == "running" ]]; then
            log "Service successfully restarted"
        else
            send_alert "CRITICAL" "Failed to restart Playwright MCP server"
        fi
    fi
}

# Function to start monitoring loop
start_monitoring() {
    log "Starting Playwright MCP server monitoring..."
    
    # Save PID
    echo $$ > "$PID_FILE"
    
    while true; do
        generate_metrics
        check_thresholds
        cleanup_logs
        restart_service_if_needed
        
        sleep 30  # Check every 30 seconds
    done
}

# Function to stop monitoring
stop_monitoring() {
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            log "Monitoring stopped (PID: $pid)"
        fi
        rm -f "$PID_FILE"
    fi
}

# Function to show help
show_help() {
    echo "Playwright MCP Server Monitoring Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  status    Show current status"
    echo "  metrics   Show metrics only"
    echo "  start     Start monitoring loop"
    echo "  stop      Stop monitoring loop"
    echo "  restart   Restart monitoring"
    echo "  logs      Show recent logs"
    echo "  help      Show this help"
    echo ""
    echo "Configuration:"
    echo "  CPU threshold: ${CPU_THRESHOLD}%"
    echo "  Memory threshold: ${MEMORY_THRESHOLD}%"
    echo "  Disk threshold: ${DISK_THRESHOLD}%"
    echo "  Response time threshold: ${RESPONSE_TIME_THRESHOLD}s"
    echo ""
    echo "Files:"
    echo "  Log file: $LOG_FILE"
    echo "  Metrics file: $METRICS_FILE"
    echo "  Alert log: $ALERT_LOG"
    echo "  PID file: $PID_FILE"
}

# Main script logic
case "${1:-help}" in
    "status")
        display_status
        ;;
    "metrics")
        if [[ -f "$METRICS_FILE" ]]; then
            cat "$METRICS_FILE"
        else
            echo "No metrics file found. Run with 'start' first."
        fi
        ;;
    "start")
        if [[ -f "$PID_FILE" ]]; then
            echo "Monitoring is already running (PID: $(cat "$PID_FILE"))"
        else
            start_monitoring &
        fi
        ;;
    "stop")
        stop_monitoring
        ;;
    "restart")
        stop_monitoring
        sleep 2
        start_monitoring &
        ;;
    "logs")
        if [[ -f "$LOG_FILE" ]]; then
            tail -n 50 "$LOG_FILE"
        else
            echo "No log file found."
        fi
        ;;
    "help"|*)
        show_help
        ;;
esac