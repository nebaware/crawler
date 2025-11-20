#!/bin/bash

echo "========================================"
echo "Starting Web Crawler Application"
echo "========================================"
echo

echo "Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed or not running"
    echo "Please install Docker from https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo
echo "Starting services with Docker Compose..."
docker-compose up -d

echo
echo "Waiting for services to start..."
sleep 5

echo
echo "Running database migrations..."
docker-compose exec -T web python manage.py migrate

echo
echo "========================================"
echo "Application started successfully!"
echo "========================================"
echo
echo "Dashboard: http://localhost:8081"
echo
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo
