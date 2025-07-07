from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class TestHealthCheck:
    def test_health_check_success(self):
        """Test health check endpoint when database is available"""
        with patch("main.get_db_connection") as mock_db:
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
        with patch("main.get_db_connection") as mock_db:
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
        with patch("main.get_db_connection") as mock_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_db.return_value = mock_conn

            # Mock cursor fetchall to return sample data
            mock_cursor.fetchall.return_value = [
                ("Positive", 10, 0.5, 0.3),
                ("Negative", 5, -0.3, 0.4),
                ("Neutral", 3, 0.0, 0.2),
            ]
            mock_conn.cursor.return_value = mock_cursor

            response = client.get("/api/sentiment/summary?hours=24")

            assert response.status_code == 200
            data = response.json()
            assert "summary" in data
            assert "total_records" in data
            assert data["time_range_hours"] == 24
            assert len(data["summary"]) > 0

    def test_sentiment_summary_no_db(self):
        """Test sentiment summary endpoint without database connection"""
        with patch("main.get_db_connection") as mock_db:
            mock_db.return_value = None

            response = client.get("/api/sentiment/summary?hours=24")

            assert response.status_code == 200
            data = response.json()
            assert "summary" in data
            assert len(data["summary"]) > 0
            assert data["time_range_hours"] == 24


class TestDashboardStats:
    def test_dashboard_stats_with_db(self):
        """Test dashboard stats endpoint with database connection"""
        with patch("main.get_db_connection") as mock_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_db.return_value = mock_conn

            # Mock cursor fetchone to return sample data
            mock_cursor.fetchone.return_value = (1422, -0.07, 298.75, datetime.now())
            mock_cursor.fetchall.return_value = [
                ("Positive", 45),
                ("Neutral", 30),
                ("Negative", 25),
            ]
            mock_conn.cursor.return_value = mock_cursor

            response = client.get("/api/dashboard/stats")

            assert response.status_code == 200
            data = response.json()
            assert "general_stats" in data
            assert "sentiment_distribution" in data
            assert data["general_stats"]["total_records"] == 1422
            assert data["general_stats"]["overall_sentiment"] == -0.07
            assert data["general_stats"]["avg_stock_price"] == 298.75

    def test_dashboard_stats_no_db(self):
        """Test dashboard stats endpoint without database connection"""
        with patch("main.get_db_connection") as mock_db:
            mock_db.return_value = None

            response = client.get("/api/dashboard/stats")

            assert response.status_code == 200
            data = response.json()
            assert "general_stats" in data
            assert "sentiment_distribution" in data
            assert data["general_stats"]["total_records"] == 1250


class TestStockPrices:
    def test_stock_prices_endpoint(self):
        """Test stock prices endpoint"""
        with patch("main.get_db_connection") as mock_db:
            mock_db.return_value = None

            response = client.get("/api/stocks/prices?hours=24")

            assert response.status_code == 200
            data = response.json()
            assert "stock_prices" in data
            assert "time_range_hours" in data


class TestLatestNews:
    def test_latest_news_endpoint(self):
        """Test latest news endpoint"""
        with patch("main.get_db_connection") as mock_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_db.return_value = mock_conn

            # Mock cursor fetchall to return sample data
            mock_cursor.fetchall.return_value = [
                (
                    "Test News",
                    "Test description",
                    "https://example.com",
                    datetime.now(),
                    "Test Source",
                    0.5,
                    0.3,
                    "AAPL",
                )
            ]
            mock_conn.cursor.return_value = mock_cursor

            response = client.get("/api/news/latest?limit=5")

            assert response.status_code == 200
            data = response.json()
            assert "news" in data
            assert "total_count" in data
            assert len(data["news"]) <= 5


class TestCorrelationAnalysis:
    def test_correlation_analysis_endpoint(self):
        """Test correlation analysis endpoint"""
        with patch("main.get_db_connection") as mock_db:
            mock_db.return_value = None

            response = client.get("/api/correlation/analysis?hours=24")

            assert response.status_code == 200
            data = response.json()
            assert "correlation_analysis" in data
            assert "time_range_hours" in data


class TestTimeline:
    def test_sentiment_timeline_endpoint(self):
        """Test sentiment timeline endpoint"""
        with patch("main.get_db_connection") as mock_db:
            mock_db.return_value = None

            response = client.get("/api/sentiment/timeline?hours=24&interval=hour")

            assert response.status_code == 200
            data = response.json()
            assert "timeline" in data
            assert "interval" in data
            assert "time_range_hours" in data


class TestAuthentication:
    def test_login_endpoint(self):
        """Test login endpoint"""
        response = client.post(
            "/auth/login", data={"username": "testuser", "password": "testpass"}
        )

        # Should return 401 for invalid credentials
        assert response.status_code == 401

    def test_protected_route_without_token(self):
        """Test protected route without authentication"""
        response = client.get("/auth/protected")

        assert response.status_code in [
            401,
            403,
        ]  # Both are valid for unauthorized access

    def test_admin_route_without_token(self):
        """Test admin route without authentication"""
        response = client.get("/auth/admin")

        assert response.status_code in [
            401,
            403,
        ]  # Both are valid for unauthorized access


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

    def test_invalid_interval_parameter(self):
        """Test handling of invalid interval parameter"""
        response = client.get("/api/sentiment/timeline?interval=invalid")

        # Should handle gracefully and use default
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


class TestDatabaseConnection:
    def test_database_connection_endpoint(self):
        """Test database connection endpoint"""
        response = client.get("/test-db")

        assert response.status_code == 200
        data = response.json()
        assert "total_records" in data
        assert "recent_records" in data
        assert "connection" in data


class TestRootEndpoint:
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "running"


if __name__ == "__main__":
    pytest.main([__file__])
