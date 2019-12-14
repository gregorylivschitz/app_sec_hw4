# Use an official Python runtime as an image
FROM python:3.6

EXPOSE 8080

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app
CMD python3 -m flask run -h 0.0.0.0 -p 8080
