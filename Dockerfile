FROM python:3.13.3-bookworm
RUN pip install --upgrade pip
COPY requirements.txt /temp/requirements.txt
COPY service /service
WORKDIR /service
EXPOSE 8000
RUN pip install -r /temp/requirements.txt
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* && apt update
RUN adduser --disabled-password service-user
USER service-user