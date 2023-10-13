FROM python:3.9

WORKDIR /app

RUN pip install gunicorn==20.1.0

COPY requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir 

COPY . .

COPY run.sh .

RUN chmod +x run.sh

ENTRYPOINT ["/app/run.sh"]

# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram_backend.wsgi"]
