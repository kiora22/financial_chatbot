.PHONY: build run stop clean setup test dev

# Default environment
ENV_FILE := .env

# Check if .env file exists, create if not
ifneq ($(wildcard $(ENV_FILE)),)
	include $(ENV_FILE)
else
	$(shell cp .env.example $(ENV_FILE))
	include $(ENV_FILE)
endif

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
	docker-compose run --rm backend python -m utils.init_db

# Run tests
test:
	docker-compose run --rm backend pytest

# Process documents in the drop folder
process-docs:
	docker-compose run --rm document_processor python -m document_processor.process_existing

# Generate sample data
generate-sample:
	docker-compose run --rm backend python -m utils.generate_sample_data

# Create a new user
create-user:
	@read -p "Username: " username; \
	read -p "Password: " password; \
	docker-compose run --rm backend python -m utils.create_user --username $$username --password $$password

# Setup the entire project
setup: build init-db generate-sample run

# Show logs
logs:
	docker-compose logs -f

# Open shell in container
shell:
	@read -p "Container (frontend/backend/document_processor): " container; \
	docker-compose exec $$container /bin/bash