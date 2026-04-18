FROM python:3.11

WORKDIR /app

# Copy python requirements and install them
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose the default Fly.io and Flask port
EXPOSE 8080

# Start the Flask app using Gunicorn for better stability than Flask dev server
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "4", "app:app"]
