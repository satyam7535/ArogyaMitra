// Backend test environment setup
// Injects test-only mock configuration into process.env before app/serverConfig evaluation
process.env.NODE_ENV = "test";
if (!process.env.PORT) process.env.PORT = "5000";
if (!process.env.DB_URL) process.env.DB_URL = "mongodb://127.0.0.1:27017/arogyamitra_test";
if (!process.env.JWT_SECRET) process.env.JWT_SECRET = "mock_jwt_secret_for_test_runs_must_be_over_32_characters!";
if (!process.env.INTERNAL_SERVICE_SECRET) process.env.INTERNAL_SERVICE_SECRET = "mock_internal_secret_for_test_runs_32_chars!";
if (!process.env.ENCRYPTION_KEY) process.env.ENCRYPTION_KEY = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef";
if (!process.env.FRONTEND_URL) process.env.FRONTEND_URL = "http://localhost:5173";
if (!process.env.ML_API_URL) process.env.ML_API_URL = "http://localhost:8000";
if (!process.env.GRAPH_API_URL) process.env.GRAPH_API_URL = "http://localhost:8001";

