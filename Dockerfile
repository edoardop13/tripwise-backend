# Use the AWS Lambda Python base image
FROM public.ecr.aws/lambda/python:3.12-arm64

# Set the working directory inside the container
WORKDIR /var/task

# Copy the requirements file
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .
