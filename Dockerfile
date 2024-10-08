FROM python:3.9-slim
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
ENV PG_SCRIPT_DIRECTORY=/app/pg_scripts
COPY . /app/
CMD ["python", "main.py"]
