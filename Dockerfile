FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 17787

CMD ["sh", "-c", "python -c 'from main import create_db_and_tables; create_db_and_tables()' && uvicorn main:app --host 0.0.0.0 --port 17787"]
