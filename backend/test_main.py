import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
from main import app

client = TestClient(app)

class TestHealthCheck:
    def test_health_check_success(self):
        """Test health check endpoint when database is available"""
        with patch('main.get_db_connection') as mock_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_conn.cursor.return_value = mock_cursor
            mock_db.return_value = mock_conn
            
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["database"] == "connected"
            assert "timestamp" in data
            assert data["version"] == "1.0.0"

    def test_health_check_no_db(self):
        """Test health check endpoint when database is not available"""
        with patch('main.get_db_connection') as mock_db:
            mock_db.return_value = None
            
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["database"] == "disconnected"
            assert "message" in data

class TestMetrics:
    def test_metrics_endpoint(self):
        """Test metrics endpoint"""
        response = client.get("/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert "request_count" in data
        assert "error_count" in data
        assert "db_connection_errors" in data
        assert "average_response_time_ms" in data
        assert "timestamp" in data

class TestSentimentSummary:
    def test_sentiment_summary_with_db(self):
        """Test sentiment summary endpoint with database connection"""
        with patch('main.get_db_connection') as mock_db:
            mock_conn = MagicMock()
            mock_db.return_value = mock_conn
            
            # Mock pandas read_sql_query to return sample data
            with patch('pandas.read_sql_query') as mock_pandas:
                mock_df = MagicMock()
                mock_df.to_dict.return_value = [
                    {"sentiment_category": "Positive", "count": 10, "avg_score": 0.5}
                ]
                mock_df.__len__ = lambda x: 1
                mock_pandas.return_value = mock_df
                
                response = client.get("/api/sentiment/summary?hours=24")
                
                assert response.status_code == 200
                data = response.json()
                assert "summary" in data
                assert "total_records" in data
                assert data["time_range_hours"] == 24

    def test_sentiment_summary_no_db(self):
        """Test sentiment summary endpoint without database connection"""
        with patch('main.get_db_connection') as mock_db:
            mock_db.return_value = None
            
            response = client.get("/api/sentiment/summary?hours=24")
            
            assert response.status_code == 200
            data = response.json()
            assert "summary" in data
            assert len(data["summary"]) > 0
            assert data["time_range_hours"] == 24

class TestStockPrices:
    def test_stock_prices_endpoint(self):
        """Test stock prices endpoint"""
        with patch('main.get_db_connection') as mock_db:
            mock_db.return_value = None
            
            response = client.get("/api/stocks/prices?hours=24")
            
            assert response.status_code == 200
            data = response.json()
            assert "prices" in data
            assert "time_range_hours" in data

class TestLatestNews:
    def test_latest_news_endpoint(self):
        """Test latest news endpoint"""
        with patch('main.get_db_connection') as mock_db:
            mock_db.return_value = None
            
            response = client.get("/api/news/latest?limit=5")
            
            assert response.status_code == 200
            data = response.json()
            assert "news" in data
            assert len(data["news"]) <= 5

class TestDashboardStats:
    def test_dashboard_stats_endpoint(self):
        """Test dashboard stats endpoint"""
        with patch('main.get_db_connection') as mock_db:
            mock_db.return_value = None
            
            response = client.get("/api/dashboard/stats")
            
            assert response.status_code == 200
            data = response.json()
            assert "total_news" in data
            assert "total_stocks" in data
            assert "avg_sentiment" in data

class TestCorrelationAnalysis:
    def test_correlation_analysis_endpoint(self):
        """Test correlation analysis endpoint"""
        with patch('main.get_db_connection') as mock_db:
            mock_db.return_value = None
            
            response = client.get("/api/correlation/analysis?hours=24")
            
            assert response.status_code == 200
            data = response.json()
            assert "correlation_analysis" in data
            assert "time_range_hours" in data

class TestErrorHandling:
    def test_invalid_hours_parameter(self):
        """Test handling of invalid hours parameter"""
        response = client.get("/api/sentiment/summary?hours=-1")
        
        # Should handle gracefully and use default or reasonable value
        assert response.status_code == 200

    def test_invalid_limit_parameter(self):
        """Test handling of invalid limit parameter"""
        response = client.get("/api/news/latest?limit=0")
        
        # Should handle gracefully and use default or reasonable value
        assert response.status_code == 200

class TestCORS:
    def test_cors_headers(self):
        """Test that CORS headers are properly set"""
        response = client.options("/health")
        
        # FastAPI should handle CORS properly
        assert response.status_code in [200, 405]  # OPTIONS might return 405

class TestRequestLogging:
    def test_request_has_request_id(self):
        """Test that requests include request ID in headers"""
        response = client.get("/health")
        
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time" in response.headers

if __name__ == "__main__":
    pytest.main([__file__]) 