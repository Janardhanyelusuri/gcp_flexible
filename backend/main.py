import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from google.cloud import secretmanager
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Enable CORS for frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Get environment configuration
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'development')
PROJECT_ID = os.environ.get('GCP_PROJECT_ID') or os.environ.get('GOOGLE_CLOUD_PROJECT')

# Initialize Secret Manager client
try:
    secret_client = secretmanager.SecretManagerServiceClient()
    logger.info(f"[{ENVIRONMENT}] Secret Manager client initialized")
except Exception as e:
    logger.error(f"[{ENVIRONMENT}] Failed to initialize Secret Manager: {str(e)}")
    secret_client = None

def get_secret(secret_name):
    """Retrieve secret from Google Secret Manager"""
    if not secret_client:
        logger.error(f"[{ENVIRONMENT}] Secret Manager client not available")
        return None
    
    try:
        if not PROJECT_ID:
            logger.error(f"[{ENVIRONMENT}] GCP_PROJECT_ID not set")
            return None
        
        name = f"projects/{PROJECT_ID}/secrets/{secret_name}/versions/latest"
        response = secret_client.access_secret_version(request={"name": name})
        secret_value = response.payload.data.decode('UTF-8')
        logger.info(f"[{ENVIRONMENT}] Successfully retrieved secret: {secret_name}")
        return secret_value
    except Exception as e:
        logger.error(f"[{ENVIRONMENT}] Error retrieving secret {secret_name}: {str(e)}")
        return None

# Cache secrets on startup
DB_PASSWORD = None
API_KEY = None

def initialize_secrets():
    """Load secrets on application startup"""
    global DB_PASSWORD, API_KEY
    logger.info(f"[{ENVIRONMENT}] Initializing secrets from Secret Manager...")
    
    DB_PASSWORD = get_secret('db-password')
    API_KEY = get_secret('api-key')
    
    if DB_PASSWORD:
        logger.info(f"[{ENVIRONMENT}] ✓ db-password loaded successfully")
    else:
        logger.warning(f"[{ENVIRONMENT}] ✗ db-password not loaded")
    
    if API_KEY:
        logger.info(f"[{ENVIRONMENT}] ✓ api-key loaded successfully")
    else:
        logger.warning(f"[{ENVIRONMENT}] ✗ api-key not loaded")

# Environment colors for UI
ENV_COLORS = {
    'dev': '#FFA500',       # Orange
    'development': '#FFA500',
    'qa': '#4169E1',        # Blue
    'staging': '#4169E1',
    'prod': '#228B22',      # Green
    'production': '#228B22'
}

@app.route("/api/health", methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "backend-api",
        "environment": ENVIRONMENT,
        "project": PROJECT_ID,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }), 200

@app.route("/api/status", methods=['GET'])
def api_status():
    """Detailed status endpoint"""
    return jsonify({
        "status": "operational",
        "service": "backend-api",
        "environment": ENVIRONMENT,
        "environment_color": ENV_COLORS.get(ENVIRONMENT.lower(), '#808080'),
        "project_id": PROJECT_ID,
        "secrets_configured": {
            "db_password": DB_PASSWORD is not None,
            "api_key": API_KEY is not None
        },
        "architecture": {
            "containerized": True,
            "runtime": "App Engine Flexible",
            "container_registry": "Artifact Registry"
        },
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }), 200

@app.route("/api/data", methods=['GET'])
def get_data():
    """Sample data endpoint"""
    # Different data per environment
    env_lower = ENVIRONMENT.lower()
    
    if env_lower in ['dev', 'development']:
        items = [
            {"id": 1, "name": "DEV Item 1", "value": 100, "status": "testing"},
            {"id": 2, "name": "DEV Item 2", "value": 200, "status": "testing"},
            {"id": 3, "name": "DEV Item 3", "value": 300, "status": "testing"}
        ]
    elif env_lower in ['qa', 'staging']:
        items = [
            {"id": 1, "name": "QA Item 1", "value": 150, "status": "validation"},
            {"id": 2, "name": "QA Item 2", "value": 250, "status": "validation"},
            {"id": 3, "name": "QA Item 3", "value": 350, "status": "validation"}
        ]
    else:  # production
        items = [
            {"id": 1, "name": "PROD Item 1", "value": 1000, "status": "active"},
            {"id": 2, "name": "PROD Item 2", "value": 2000, "status": "active"},
            {"id": 3, "name": "PROD Item 3", "value": 3000, "status": "active"}
        ]
    
    return jsonify({
        "message": f"Data from {ENVIRONMENT} environment",
        "environment": ENVIRONMENT,
        "items": items,
        "total_items": len(items),
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@app.route("/api/data", methods=['POST'])
def post_data():
    """Sample POST endpoint"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            "error": "No data provided",
            "environment": ENVIRONMENT
        }), 400
    
    logger.info(f"[{ENVIRONMENT}] Received POST data: {data}")
    
    return jsonify({
        "message": "Data received successfully",
        "environment": ENVIRONMENT,
        "received": data,
        "status": "processed",
        "timestamp": datetime.utcnow().isoformat()
    }), 201

@app.route("/api/env-info", methods=['GET'])
def env_info():
    """Environment information endpoint"""
    env_purposes = {
        'dev': "Active development and testing",
        'development': "Active development and testing",
        'qa': "Quality assurance and validation",
        'staging': "Quality assurance and validation",
        'prod': "Live production environment",
        'production': "Live production environment"
    }
    
    return jsonify({
        "environment": ENVIRONMENT,
        "environment_color": ENV_COLORS.get(ENVIRONMENT.lower(), '#808080'),
        "project_id": PROJECT_ID,
        "purpose": env_purposes.get(ENVIRONMENT.lower(), "Unknown environment"),
        "url": f"https://{PROJECT_ID}.uc.r.appspot.com" if PROJECT_ID else "unknown",
        "configuration": {
            "log_level": os.environ.get('LOG_LEVEL', 'INFO'),
            "debug_mode": ENVIRONMENT.lower() in ['dev', 'development']
        },
        "timestamp": datetime.utcnow().isoformat()
    }), 200

@app.route("/api/secret-test", methods=['GET'])
def secret_test():
    """Test endpoint to verify secret loading (don't expose actual values!)"""
    return jsonify({
        "environment": ENVIRONMENT,
        "secrets_status": {
            "db_password": {
                "loaded": DB_PASSWORD is not None,
                "length": len(DB_PASSWORD) if DB_PASSWORD else 0,
                "preview": DB_PASSWORD[:3] + "..." if DB_PASSWORD else None
            },
            "api_key": {
                "loaded": API_KEY is not None,
                "length": len(API_KEY) if API_KEY else 0,
                "preview": API_KEY[:3] + "..." if API_KEY else None
            }
        },
        "note": "Only showing first 3 characters for security",
        "timestamp": datetime.utcnow().isoformat()
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not Found",
        "message": "The requested API endpoint does not exist",
        "environment": ENVIRONMENT,
        "path": request.path
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"[{ENVIRONMENT}] Internal server error: {str(error)}")
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred",
        "environment": ENVIRONMENT
    }), 500

# Initialize secrets when app starts
with app.app_context():
    initialize_secrets()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    debug = ENVIRONMENT.lower() in ['dev', 'development']
    
    logger.info(f"Starting {ENVIRONMENT} backend on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Project ID: {PROJECT_ID}")
    
    app.run(host="0.0.0.0", port=port, debug=debug)
