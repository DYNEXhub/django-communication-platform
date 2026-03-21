#!/bin/bash

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Django Communication Platform...${NC}"

# Wait for PostgreSQL to be ready
echo -e "${YELLOW}Waiting for PostgreSQL...${NC}"
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
    sleep 0.5
done
echo -e "${GREEN}PostgreSQL is ready!${NC}"

# Wait for Redis to be ready
echo -e "${YELLOW}Waiting for Redis...${NC}"
REDIS_HOST=$(echo $REDIS_URL | sed -E 's|redis://([^:]+):.*|\1|')
REDIS_PORT=$(echo $REDIS_URL | sed -E 's|redis://[^:]+:([0-9]+).*|\1|')
while ! nc -z $REDIS_HOST $REDIS_PORT; do
    sleep 0.5
done
echo -e "${GREEN}Redis is ready!${NC}"

# Run database migrations
echo -e "${YELLOW}Running database migrations...${NC}"
python manage.py migrate --noinput
echo -e "${GREEN}Migrations completed!${NC}"

# Collect static files
echo -e "${YELLOW}Collecting static files...${NC}"
python manage.py collectstatic --noinput --clear
echo -e "${GREEN}Static files collected!${NC}"

# Create superuser if it doesn't exist (optional, for development)
if [ "$DJANGO_DEBUG" = "True" ]; then
    echo -e "${YELLOW}Checking for superuser...${NC}"
    python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
END
fi

echo -e "${GREEN}Starting application...${NC}"

# Execute the main command (passed as arguments to entrypoint)
exec "$@"
