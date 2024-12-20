from datetime import datetime
import subprocess
from docker.types import Mount

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.docker.operators.docker import DockerOperator

# default argumen
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False
}

# menjalankan etl-script.py
def run_etl_scripts():
    script_path = "/opt/airflow/etl/etl_scripts.py"
    result = subprocess.run(["python", script_path], capture_output=True, text= True)

    if result.returncode != 0:
        raise Exception(f"error {result.stderr}")
    else:
        print(result.stdout)

dag = DAG(
    "etl_and_dbt",
    default_args = default_args,
    description = "An ETL workflow using dbt",
    start_date = datetime(2024, 12, 17),
    catchup = False
)

task1 = PythonOperator(
    task_id = "run_etl_script",
    python_callable = run_etl_scripts,
    dag = dag
)

task2 = DockerOperator(
    task_id = "run_dbt",
    image ="ghcr.io/dbt-labs/dbt-postgres:1.4.7",
    command = [
        "run",
        "--profiles-dir",
        "/root",
        "--project-dir",
        "/dbt"
    ],
    auto_remove = True,
    docker_url = "unix://var/run/docker.sock",
    network_mode = "bridge",
    mounts = [
        Mount(source = "/Users/macbook/Documents/data-engginering-study/docker-data-engginer/api-postgres-etl/api_postgres",
              target = "/dbt" , type= "bind"),
        Mount(source = "/Users/macbook/.dbt",
              target = "/root" , type= "bind")
    ],
    dag = dag
)

task1 >> task2


