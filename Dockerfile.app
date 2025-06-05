FROM python:3.9-slim-buster  # Choose a Python version supported by Cloud Run

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY app/python .

# Specify the command to run on container start
CMD ["python3", "fetch_us_sock_time_series.py"]
