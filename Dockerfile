# Base python package
FROM python:3.6

# Working directory
WORKDIR /app

COPY requirements.txt ./


RUN python3 -m pip install -r requirements.txt

# Copy the files
COPY . .

# Expose correct port
EXPOSE 5000

# Executable commands
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=3500"]