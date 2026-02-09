# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (needed for some python packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Note: We don't use the --target option here as we want global installation in the container
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory
COPY . .

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Define environment variable
ENV PYTHONUNBUFFERED=1

# Run streamlit when the container launches
CMD ["streamlit", "run", "btc_stock_predictor_ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
