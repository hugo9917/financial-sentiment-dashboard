#!/usr/bin/env python3
"""
Script para probar la conexión a PostgreSQL.
"""

import psycopg2
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv("config.env")

# Configuración de la base de datos
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'financial_sentiment')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_PORT = int(os.getenv('DB_PORT', '5432'))

def test_connection():
    """Probar la conexión a PostgreSQL."""
    print("🔍 Probando conexión a PostgreSQL...")
    print(f"Host: {DB_HOST}")
    print(f"Puerto: {DB_PORT}")
    print(f"Base de datos: {DB_NAME}")
    print(f"Usuario: {DB_USER}")
    
    try:
        # Intentar conectar
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        print("✅ Conexión exitosa!")
        
        # Crear cursor
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"\n📋 Tablas encontradas: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Verificar datos en news_with_sentiment
        cursor.execute("SELECT COUNT(*) FROM news_with_sentiment;")
        news_count = cursor.fetchone()[0]
        print(f"\n📰 Noticias en la base: {news_count}")
        
        # Verificar datos en stock_prices
        cursor.execute("SELECT COUNT(*) FROM stock_prices;")
        prices_count = cursor.fetchone()[0]
        print(f"📈 Precios en la base: {prices_count}")
        
        # Verificar datos en correlation_data
        cursor.execute("SELECT COUNT(*) FROM correlation_data;")
        correlation_count = cursor.fetchone()[0]
        print(f"📊 Correlaciones en la base: {correlation_count}")
        
        # Mostrar algunas noticias recientes
        if news_count > 0:
            print(f"\n📰 Últimas 3 noticias:")
            cursor.execute("""
                SELECT symbol, title, sentiment_score, published_at 
                FROM news_with_sentiment 
                ORDER BY published_at DESC 
                LIMIT 3;
            """)
            
            for row in cursor.fetchall():
                symbol, title, sentiment, date = row
                print(f"  - {symbol}: {title[:50]}... (sentimiento: {sentiment})")
        
        cursor.close()
        conn.close()
        print("\n✅ Prueba completada exitosamente!")
        
    except psycopg2.OperationalError as e:
        print(f"❌ Error de conexión PostgreSQL: {e}")
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Detalles de conexión:")
        print(f"  Host: {DB_HOST}")
        print(f"  Puerto: {DB_PORT}")
        print(f"  Base: {DB_NAME}")
        print(f"  Usuario: {DB_USER}")
        print(f"  Contraseña: {'*' * len(DB_PASSWORD) if DB_PASSWORD else 'No configurada'}")
        
        # Mostrar más información de debug
        import traceback
        print(f"\nTraceback completo:")
        traceback.print_exc()
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Detalles de conexión:")
        print(f"  Host: {DB_HOST}")
        print(f"  Puerto: {DB_PORT}")
        print(f"  Base: {DB_NAME}")
        print(f"  Usuario: {DB_USER}")
        print(f"  Contraseña: {'*' * len(DB_PASSWORD) if DB_PASSWORD else 'No configurada'}")
        
        # Mostrar más información de debug
        import traceback
        print(f"\nTraceback completo:")
        traceback.print_exc()

if __name__ == "__main__":
    test_connection() 