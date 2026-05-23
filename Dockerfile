FROM python:3.13-alpine

WORKDIR /app



ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["poetry", "run", "python", "main.py"]
