FROM python:3.8-slim

# membangun image postgres
RUN apt-get update && apt-get install -y postgresql-client-13 cron curl\
    wget \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# upgrade pip
RUN pip install --upgrade pip

# menjalakan instalasi pandas di image
RUN pip install pandas sqlalchemy psycopg2

# mengatur directori dalam container
WORKDIR /app


# melakukan copy terhadap etl_scripts
COPY start.sh /app/start.sh
COPY etl_scripts.py /app/etl_scripts.py

RUN echo "0 3 * * * python /app/elt_script.py" | crontab -

# berguna agar dijalankan di background
ENTRYPOINT [ "python", "etl_scripts.py" ]