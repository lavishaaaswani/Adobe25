# Use lightweight Python image for small size
FROM python:3.9-slim

# Set working directory inside container
WORKDIR /app

# Copy only necessary files
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Make sure output directory exists
RUN mkdir -p /app/output

# Set entrypoint
CMD ["python3", "main.py"]
