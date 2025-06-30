from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
import os

# Configuración del DAG
default_args = {
    'owner': 'financial-sentiment-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'financial_data_pipeline',
    default_args=default_args,
    description='Pipeline completo de datos financieros y análisis de sentimiento',
    schedule_interval='*/15 * * * *',  # Cada 15 minutos
    catchup=False,
    tags=['financial', 'sentiment', 'data-pipeline']
)

def ingest_financial_data(**context):
    """
    Función para ingesta de datos financieros desde APIs
    """
    import requests
    import pandas as pd
    from datetime import datetime
    import os
    
    # Crear directorio temporal si no existe
    os.makedirs('/tmp/financial_data', exist_ok=True)
    
    # Configuración de APIs (usar variables de entorno en producción)
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "demo_key")
    ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY", "demo_key")
    
    try:
        # Obtener noticias financieras (usando demo key si no hay API key real)
        if NEWS_API_KEY == "demo_key":
            # Datos de ejemplo para desarrollo
            news_data = {
                'articles': [
                    {
                        'title': 'Sample Financial News 1',
                        'description': 'This is a sample financial news article for testing purposes.',
                        'publishedAt': datetime.now().isoformat()
                    },
                    {
                        'title': 'Sample Financial News 2',
                        'description': 'Another sample financial news article for testing.',
                        'publishedAt': datetime.now().isoformat()
                    }
                ]
            }
        else:
            news_url = f"https://newsapi.org/v2/everything?q=finance&apiKey={NEWS_API_KEY}&pageSize=50"
            news_response = requests.get(news_url)
            news_data = news_response.json()
        
        # Obtener precios de acciones (datos de ejemplo)
        stock_data = {
            'Time Series (1min)': {
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'): {
                    '1. open': '150.00',
                    '2. high': '151.00',
                    '3. low': '149.00',
                    '4. close': '150.50',
                    '5. volume': '1000000'
                }
            }
        }
        
        # Procesar y guardar datos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Guardar noticias
        if news_data.get('articles'):
            news_df = pd.DataFrame(news_data['articles'])
            news_df.to_json(f"/tmp/financial_data/news_{timestamp}.json", orient='records')
        
        # Guardar precios
        if stock_data.get('Time Series (1min)'):
            stock_df = pd.DataFrame.from_dict(stock_data['Time Series (1min)'], orient='index')
            stock_df.to_json(f"/tmp/financial_data/stock_{timestamp}.json", orient='records')
        
        return f"Data ingested at {timestamp}"
    
    except Exception as e:
        print(f"Error in data ingestion: {str(e)}")
        return f"Error: {str(e)}"

def process_sentiment(**context):
    """
    Función para procesar análisis de sentimiento
    """
    import pandas as pd
    import json
    from datetime import datetime
    import os
    
    try:
        # Crear directorio si no existe
        os.makedirs('/tmp/financial_data', exist_ok=True)
        
        # Cargar datos de noticias
        news_files = [f for f in os.listdir('/tmp/financial_data') if f.startswith('news_')]
        
        if not news_files:
            return "No news files found to process"
        
        for file in news_files:
            with open(f'/tmp/financial_data/{file}', 'r') as f:
                news_data = json.load(f)
            
            # Aplicar análisis de sentimiento simple
            for article in news_data:
                text = article.get('title', '') + ' ' + article.get('description', '')
                # Análisis de sentimiento simple basado en palabras clave
                positive_words = ['positive', 'growth', 'profit', 'success', 'up', 'gain']
                negative_words = ['negative', 'loss', 'decline', 'down', 'fall', 'risk']
                
                text_lower = text.lower()
                positive_count = sum(1 for word in positive_words if word in text_lower)
                negative_count = sum(1 for word in negative_words if word in text_lower)
                
                if positive_count > negative_count:
                    sentiment_score = 0.3
                elif negative_count > positive_count:
                    sentiment_score = -0.3
                else:
                    sentiment_score = 0.0
                
                article['sentiment_score'] = sentiment_score
                article['sentiment_subjectivity'] = 0.5  # Valor por defecto
            
            # Guardar datos procesados
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            with open(f'/tmp/financial_data/processed_news_{timestamp}.json', 'w') as f:
                json.dump(news_data, f)
        
        return "Sentiment analysis completed"
    
    except Exception as e:
        print(f"Error in sentiment processing: {str(e)}")
        return f"Error: {str(e)}"

def save_to_local_storage(**context):
    """
    Función para guardar datos en almacenamiento local
    """
    import shutil
    import os
    from datetime import datetime
    
    try:
        # Crear directorio de almacenamiento
        storage_dir = '/opt/airflow/data'
        os.makedirs(storage_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Copiar archivos procesados
        source_dir = '/tmp/financial_data'
        if os.path.exists(source_dir):
            for file in os.listdir(source_dir):
                if file.startswith(('news_', 'stock_', 'processed_')):
                    source_path = os.path.join(source_dir, file)
                    dest_path = os.path.join(storage_dir, f"{timestamp}_{file}")
                    shutil.copy2(source_path, dest_path)
        
        return f"Files saved to local storage at {timestamp}"
    
    except Exception as e:
        print(f"Error in local storage: {str(e)}")
        return f"Error: {str(e)}"

# Definir tareas
ingest_task = PythonOperator(
    task_id='ingest_financial_data',
    python_callable=ingest_financial_data,
    dag=dag
)

sentiment_task = PythonOperator(
    task_id='process_sentiment',
    python_callable=process_sentiment,
    dag=dag
)

save_task = PythonOperator(
    task_id='save_to_local_storage',
    python_callable=save_to_local_storage,
    dag=dag
)

# Tarea para mostrar información del pipeline
info_task = BashOperator(
    task_id='pipeline_info',
    bash_command='echo "Financial Data Pipeline completed successfully at $(date)"',
    dag=dag
)

# Definir dependencias
ingest_task >> sentiment_task >> save_task >> info_task 