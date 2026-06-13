FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including curl for system healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application files
COPY . .

# Ensure script_location in alembic.ini points to the local alembic folder
RUN sed -i 's/script_location = .*/script_location = .\/alembic/g' alembic.ini

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
