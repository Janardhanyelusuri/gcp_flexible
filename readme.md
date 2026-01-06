markdown# Containerized Microservices Application

Production-grade containerized microservices using Docker, App Engine Flexible, and Artifact Registry.

## Architecture

- **Frontend**: Nginx serving static content in Docker container
- **Backend**: Flask API in Docker container with Secret Manager integration
- **Deployment**: Automated CI/CD via Cloud Build triggers
- **Container Registry**: Google Artifact Registry
- **Infrastructure**: Google App Engine Flexible

## Project Structure
├── backend/              # Backend Flask API service
│   ├── Dockerfile       # Backend container definition
│   ├── app.yaml         # App Engine configuration
│   ├── main.py          # Flask application
│   └── requirements.txt # Python dependencies
├── frontend/            # Frontend Nginx service
│   ├── Dockerfile       # Frontend container definition
│   ├── app.yaml         # App Engine configuration
│   ├── nginx.conf       # Nginx configuration
│   └── public/
│       └── index.html   # Main HTML page
├── dispatch.yaml        # Path-based routing
└── cloudbuild-*.yaml    # CI/CD pipeline definitions

## Deployment

### Automatic Deployment

Pushes to the main branch automatically trigger deployments:
- Changes to `backend/` → Deploys backend service
- Changes to `frontend/` → Deploys frontend service

### Manual Deployment
```bash
# Deploy backend
gcloud app deploy backend/app.yaml

# Deploy frontend
gcloud app deploy frontend/app.yaml

# Deploy routing rules
gcloud app deploy dispatch.yaml
```

## URLs

- **Application**: https://YOUR-PROJECT-ID.uc.r.appspot.com
- **API Health**: https://YOUR-PROJECT-ID.uc.r.appspot.com/api/health
- **API Status**: https://YOUR-PROJECT-ID.uc.r.appspot.com/api/status

## Environment Variables

Configured in `backend/app.yaml`:
- `ENVIRONMENT`: dev/qa/production
- `GCP_PROJECT_ID`: Your GCP project ID
- `LOG_LEVEL`: INFO/DEBUG

## Secrets

Stored in Secret Manager:
- `db-password`: Database password
- `api-key`: API key for external services

## Development

### Local Testing (Optional)
```bash
# Build backend image
cd backend
docker build -t backend-local .
docker run -p 8080:8080 -e PORT=8080 backend-local

# Build frontend image
cd frontend
docker build -t frontend-local .
docker run -p 8080:8080 frontend-local
```

## Monitoring

- **Logs**: Cloud Logging
- **Metrics**: Cloud Monitoring
- **Health Checks**: /api/health (backend), /health (frontend)

## Cost Estimate

- **Minimum**: ~$80-100/month (1 frontend + 1 backend instance)
- **Moderate**: ~$150-200/month (with auto-scaling)
- **High Traffic**: ~$300-400/month (max scaling)

---

**Version**: 2.0.0  
**Last Updated**: 2024-12-24
