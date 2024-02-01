FROM python:3.10.8

# Copy all files from the current directory to the Docker image
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Run the server
CMD "flask run --host=0.0.0.0 --port=5000"