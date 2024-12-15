# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install wkhtmltopdf (adjust the version if needed)
RUN apt-get update && apt-get install -y libcairo2-dev libjpeg-dev libpng-dev libtiff5-dev libwebp-dev libxrender1 libxtst6 libcups2-dev libpq-dev
RUN apt-get install -y wkhtmltopdf

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install CORS extension for Flask (or your framework)
RUN pip install flask-cors

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variables
#ENV DATABASE_URL="postgres://user:password@host:port/database"
#ENV API_KEY="your_api_key"
ENV PORT=8080

# Run writebook-api.py when the container launches
#CMD ["python", "app.py"]

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 --forwarded-allow-ips='*' app:app
# Run writebook-api.py when the container launches
#CMD ["gunicorn", "--bind", ":$PORT", "--workers", "1", "--threads", "8", "--timeout", "0", "app:app"]