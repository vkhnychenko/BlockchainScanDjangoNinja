FROM python:3.9

WORKDIR /app

COPY requirements.txt /app

RUN pip install --upgrade pip
RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY . /app