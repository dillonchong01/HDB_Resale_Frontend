# 1. Start from a lightweight Python image
FROM python:3.10-slim

# 2. Set a working directory in the container
WORKDIR /app

# 3. Copy dependency manifest and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy all your code into the container
COPY . .

# 5. Expose the port your FastAPI app uses
EXPOSE 8000

# 6. Tell Docker how to start your app
CMD ["uvicorn", "main:task_app", "--host", "0.0.0.0", "--port", "8000"]