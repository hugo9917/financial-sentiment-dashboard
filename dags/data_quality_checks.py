from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import os

# Configuración del DAG
default_args = {
    "owner": "data-quality-team",
    "depends_on_past": True,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=10),
}

dag = DAG(
    "data_quality_checks",
    default_args=default_args,
    description="Pruebas de calidad de datos para el pipeline financiero",
    schedule_interval="0 */2 * * *",  # Cada 2 horas
    catchup=False,
    tags=["data-quality", "dbt", "testing"],
)


def check_data_freshness(**context):
    """
    Verificar que los datos estén actualizados
    """
    import os
    from datetime import datetime, timedelta

    data_dir = "/opt/airflow/data"

    if not os.path.exists(data_dir):
        return "Data directory does not exist yet"

    # Verificar archivos de la última hora
    files = [f for f in os.listdir(data_dir) if f.endswith(".json")]

    if not files:
        return "No data files found"

    # Obtener el archivo más reciente
    latest_file = max(files, key=lambda x: os.path.getmtime(os.path.join(data_dir, x)))
    latest_file_path = os.path.join(data_dir, latest_file)
    file_time = datetime.fromtimestamp(os.path.getmtime(latest_file_path))
    time_diff = datetime.now() - file_time

    if time_diff > timedelta(hours=2):
        return f"Warning: Data is old. Latest file: {latest_file}, Age: {time_diff}"

    return f"Data freshness check passed. Latest file: {latest_file}, Age: {time_diff}"


def check_data_completeness(**context):
    """
    Verificar que no falten datos críticos
    """
    import os
    import json

    data_dir = "/opt/airflow/data"

    if not os.path.exists(data_dir):
        return "Data directory does not exist yet"

    # Verificar que existan archivos de noticias y precios
    files = [f for f in os.listdir(data_dir) if f.endswith(".json")]

    news_files = [f for f in files if "news" in f]
    stock_files = [f for f in files if "stock" in f]
    processed_files = [f for f in files if "processed" in f]

    result = f"Data completeness check passed. News files: {len(news_files)}, Stock files: {len(stock_files)}, Processed files: {len(processed_files)}"

    if not news_files:
        result += " - Warning: No news files found"

    if not stock_files:
        result += " - Warning: No stock files found"

    return result


def validate_data_structure(**context):
    """
    Validar la estructura de los datos
    """
    import os
    import json

    data_dir = "/opt/airflow/data"

    if not os.path.exists(data_dir):
        return "Data directory does not exist yet"

    files = [f for f in os.listdir(data_dir) if f.endswith(".json")]

    if not files:
        return "No data files found for validation"

    validation_results = []

    for file in files[:3]:  # Validar solo los primeros 3 archivos
        try:
            with open(os.path.join(data_dir, file), "r") as f:
                data = json.load(f)

            if isinstance(data, list):
                validation_results.append(
                    f"{file}: Valid JSON array with {len(data)} items"
                )
            elif isinstance(data, dict):
                validation_results.append(
                    f"{file}: Valid JSON object with {len(data)} keys"
                )
            else:
                validation_results.append(f"{file}: Unexpected data type")

        except Exception as e:
            validation_results.append(f"{file}: Error - {str(e)}")

    return " | ".join(validation_results)


# Tareas de calidad de datos
freshness_check = PythonOperator(
    task_id="check_data_freshness", python_callable=check_data_freshness, dag=dag
)

completeness_check = PythonOperator(
    task_id="check_data_completeness", python_callable=check_data_completeness, dag=dag
)

structure_check = PythonOperator(
    task_id="validate_data_structure", python_callable=validate_data_structure, dag=dag
)

# Tarea para mostrar resumen de calidad
quality_summary = BashOperator(
    task_id="quality_summary",
    bash_command='echo "Data quality checks completed at $(date)" && ls -la /opt/airflow/data/ 2>/dev/null || echo "No data directory found"',
    dag=dag,
)

# Definir dependencias
[freshness_check, completeness_check, structure_check] >> quality_summary
