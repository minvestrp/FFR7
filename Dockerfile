# Base image with system dependencies for WeasyPrint and Python
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       gcc \
       libcairo2 \
       libpango-1.0-0 \
       libgdk-pixbuf2.0-0 \
       libffi-dev \
       libxml2 \
       libxslt1-dev \
       libjpeg62-turbo-dev \
       zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy only requirements first to cache installs
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy application
COPY . /app

# create data dir for sqlite and outputs
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["uvicorn", "interface.api:app", "--host", "0.0.0.0", "--port", "8000"]
