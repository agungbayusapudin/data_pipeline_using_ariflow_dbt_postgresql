FROM apache/airflow:latest

USER airflow

RUN pip install apache-airflow-providers-docker  