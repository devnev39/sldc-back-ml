# FROM python:3.11.0
FROM tensorflow/tensorflow:2.15.0

WORKDIR /app

COPY requirements.txt /app/

RUN apt update

RUN apt install -y cmake

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8080

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]

