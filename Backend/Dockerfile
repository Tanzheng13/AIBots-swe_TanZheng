# Use an official Python runtime as a parent image
FROM python:3.10.4

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install openai --upgrade
RUN pip install "pymongo[srv]"

# RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install uvicorn pip install uvicorn[standard]
# RUN pip install openai --upgrade
# RUN pip install "fastapi[all]
# RUN pip install pip install pymongo
# RUN pip install "pymongo[srv]"
# RUN pip install timeout-decorator
# RUN pip install beanie
# RUN pip install pytest

# Make port 80 available to the world outside this container
EXPOSE 80

# Load environment variables from .env file
ARG ENV_FILE_PATH="./.env"

# Define environment variable
ENV OPENAI_API_KEY=$OPENAI_API_KEY
ENV DB=$DB

# Test environment variables using curl
# RUN echo "Testing OPENAI_API_KEY: " && curl $OPENAI_API_KEY
# RUN echo "Testing DB: " && curl $DB

# Run app.py when the container launches
CMD ["python", "main.py"]