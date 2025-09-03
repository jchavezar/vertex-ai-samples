# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install the dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Build the Flet web app
RUN flet build web

# Expose the port the app runs on, as expected by Cloud Run
EXPOSE 8080

# Run the web server to serve the built Flet app
CMD ["python", "-m", "http.server", "8080", "--directory", "build/web"]
