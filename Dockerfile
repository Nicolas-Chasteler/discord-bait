FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
ENV PG_SCRIPT_DIRECTORY=/app/pg_scripts
RUN python -m pip install git+https://github.com/Nicolas-Chasteler/pygres.git
COPY . /app/
CMD ["python", "main.py"]
