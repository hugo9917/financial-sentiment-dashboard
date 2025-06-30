import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

NEWS_CSV = "news_with_sentiment.csv"
PRICES_CSV = "stock_prices.csv"

st.set_page_config(page_title="Sentimiento y Precios de Acciones", layout="wide")
st.title("📈 Dashboard de Sentimiento y Precios de Acciones")

@st.cache_data
def load_data():
    news = pd.read_csv(NEWS_CSV, parse_dates=["published_at", "ingested_at"], low_memory=False)
    prices = pd.read_csv(PRICES_CSV, parse_dates=["timestamp", "ingested_at"], low_memory=False)
    return news, prices

news, prices = load_data()

symbols = sorted(set(news['symbol']).union(prices['symbol']))
symbol = st.selectbox("Selecciona el símbolo de la acción:", symbols)

col1, col2 = st.columns(2)

with col1:
    min_date = news[news['symbol'] == symbol]['published_at'].min()
    max_date = news[news['symbol'] == symbol]['published_at'].max()
    date_range = st.date_input("Rango de fechas (noticias)", [min_date, max_date])

with col2:
    min_date_p = prices[prices['symbol'] == symbol]['timestamp'].min()
    max_date_p = prices[prices['symbol'] == symbol]['timestamp'].max()
    date_range_p = st.date_input("Rango de fechas (precios)", [min_date_p, max_date_p], key="pr")

# Filtrar datos
news_f = news[(news['symbol'] == symbol) & (news['published_at'] >= str(date_range[0])) & (news['published_at'] <= str(date_range[1]))]
prices_f = prices[(prices['symbol'] == symbol) & (prices['timestamp'] >= str(date_range_p[0])) & (prices['timestamp'] <= str(date_range_p[1]))]

# Forzar conversión a datetime antes de usar .dt
news_f['published_at'] = pd.to_datetime(news_f['published_at'], errors='coerce')
prices_f['timestamp'] = pd.to_datetime(prices_f['timestamp'], errors='coerce')

# --- MEJORA: Ordenar y limpiar precios ---
if not prices_f.empty:
    prices_f = prices_f.sort_values('timestamp')
    # Si hay varios precios por día, promediar (opcional)
    # prices_f['date'] = prices_f['timestamp'].dt.date
    # prices_f = prices_f.groupby('date', as_index=False').agg({'close':'mean', 'timestamp':'first'})
    # Eliminar duplicados exactos de timestamp
    prices_f = prices_f.drop_duplicates(subset=['timestamp'])

# Gráfico de sentimiento
st.subheader("Sentimiento de Noticias")
if not news_f.empty:
    fig_sent = px.scatter(news_f, x="published_at", y="sentiment", hover_data=["title", "description"], color="sentiment", color_continuous_scale="RdYlGn", title="Sentimiento de Noticias a lo largo del tiempo")
    st.plotly_chart(fig_sent, use_container_width=True)
else:
    st.info("No hay noticias para este rango.")

# Gráfico de precios
st.subheader("Precio de la Acción")
if not prices_f.empty:
    fig_price = px.line(prices_f, x="timestamp", y="close", title="Precio de Cierre a lo largo del tiempo")
    st.plotly_chart(fig_price, use_container_width=True)
else:
    st.info("No hay precios para este rango.")

# Correlación
st.subheader("Correlación entre Sentimiento y Precio")
if not news_f.empty and not prices_f.empty:
    # Unir por fecha más cercana
    news_f['date'] = news_f['published_at'].dt.date
    prices_f['date'] = prices_f['timestamp'].dt.date
    merged = pd.merge_asof(news_f.sort_values('published_at'), prices_f.sort_values('timestamp'), left_on='published_at', right_on='timestamp', by='symbol', direction='nearest', tolerance=pd.Timedelta('1D'))
    merged = merged.dropna(subset=['close', 'sentiment'])
    if not merged.empty:
        fig_corr = px.scatter(merged, x="sentiment", y="close", trendline="ols", title="Sentimiento vs Precio de Cierre")
        st.plotly_chart(fig_corr, use_container_width=True)
        corr = merged['sentiment'].corr(merged['close'])
        st.metric("Correlación Pearson", f"{corr:.2f}")
    else:
        st.info("No hay datos suficientes para correlación.")
else:
    st.info("No hay datos suficientes para correlación.") 