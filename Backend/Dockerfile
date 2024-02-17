# Use an official Python runtime as a parent image
FROM python:3.10.4

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install openai --upgrade
# Make port 80 available to the world outside this container
EXPOSE 80

# Load environment variables from .env file
ARG ENV_FILE_PATH="./.env"

# Define environment variable
ENV OPENAI_API_KEY=$OPENAI_API_KEY
ENV DB=$DB

# Run app.py when the container launches
CMD ["python", "main.py"]