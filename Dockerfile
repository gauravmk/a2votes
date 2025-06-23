# Use an official Python runtime as a base image
FROM python:3-slim

RUN apt-get update &&\
    apt-get install -y binutils libproj-dev gdal-bin libgdal-dev g++

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . .

# Expose the port your application will run on (if applicable)
EXPOSE 8000

# Define the command to run your application
CMD ["python", "app.py"]

