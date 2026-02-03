# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port (Cloud providers usually expect 8080 or use $PORT)
ENV PORT=8080

# Command to run the app using the $PORT environment variable
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port $PORT"]
