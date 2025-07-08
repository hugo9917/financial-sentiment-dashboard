import psycopg2

conn = psycopg2.connect(
    host="postgres",
    database="financial_sentiment",
    user="postgres",
    password="password",
)
cur = conn.cursor()
cur.execute(
    "SELECT hour FROM financial_sentiment_correlation ORDER BY hour DESC LIMIT 5;"
)
print("Últimos 5 valores de hour:", cur.fetchall())
cur.execute(
    "SELECT COUNT(*) FROM financial_sentiment_correlation WHERE hour >= NOW() - INTERVAL '8760 hours';"
)
print("Registros en el rango:", cur.fetchone()[0])
cur.execute("SELECT MIN(hour), MAX(hour) FROM financial_sentiment_correlation;")
print("Rango de datos:", cur.fetchone())
cur.close()
conn.close()
