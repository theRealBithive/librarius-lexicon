#!/bin/sh

# Stoppt das Skript, wenn ein Befehl fehlschlägt
set -e

echo "Running Database Migrations..."

python manage.py migrate

echo "Starting Server..."

exec "$@"