FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY document_processor/ document_processor/
COPY config/ config/
COPY utils/ utils/

# Set environment variables
ENV PYTHONPATH=/app
ENV WATCH_FOLDER=/app/document_drop

# Create document drop folder
RUN mkdir -p /app/document_drop

# For Phase 1, we're just creating a placeholder service
# In Phase 2, this will be a working document processor
CMD ["python", "-c", "import time; print('Document processor service started (placeholder)'); time.sleep(3600)"]