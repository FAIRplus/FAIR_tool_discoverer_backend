# Base python package
FROM python:3.8

# Working directory
WORKDIR /app

COPY requirements.txt ./

RUN python3 -m pip install -r requirements.txt

# Copy the files
COPY . .

# Expose correct port
EXPOSE 3500

# Executable commands
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3500"]
