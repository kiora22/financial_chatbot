.PHONY: build run stop clean setup test dev

# Default environment
ENV_FILE := .env

# Build all containers
build:
	docker-compose build

# Run the application
run:
	docker-compose up -d

# Run in development mode with logs
dev:
	docker-compose up

# Stop the application
stop:
	docker-compose down

# Clean up containers and volumes
clean:
	docker-compose down -v
	rm -rf data/uploads/*
	rm -rf data/documents/*
	rm -rf data/document_drop/*

# Initialize the database
init-db:
	if not exist data mkdir data
	docker-compose run --rm backend python -m utils.init_db

# Run tests
test:
	docker-compose run --rm backend pytest

# Process documents in the drop folder
process-docs:
	docker-compose run --rm document_processor python -m document_processor.process_existing

# Generate sample data
generate-sample:
	docker-compose run --rm backend python -c "from utils.init_db import init_database, populate_sample_data; engine = init_database(); populate_sample_data(engine)"

# Create a new user
create-user:
	@read -p "Username: " username; \
	read -p "Password: " password; \
	docker-compose run --rm backend python -m utils.create_user --username $$username --password $$password

# Setup the entire project
setup:
# Check if .env file exists, create if not
#	ifneq ($(wildcard $(ENV_FILE)),)
#		include $(ENV_FILE)
#	else
#		$(shell cp .env.example $(ENV_FILE))
#		include $(ENV_FILE)
#	endif
	$(MAKE) build
	$(MAKE) init-db
	$(MAKE) generate-sample
	$(MAKE) run

# Show logs
logs:
	docker-compose logs -f

# Open shell in container
shell:
	@read -p "Container (frontend/backend/document_processor): " container; \
	docker-compose exec $$container /bin/bash