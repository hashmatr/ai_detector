# Quick Start - Local Testing with Docker

## Prerequisites
- Docker installed
- Docker Compose installed

## Step 1: Build and Run Locally

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

## Step 2: Access the Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:5000
- **API Info**: http://localhost:5000/info

## Step 3: Test the Application

```bash
# Test backend health
curl http://localhost:5000/info

# Test prediction
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"This is a test text to analyze."}'
```

## Step 4: View Logs

```bash
# View all logs
docker-compose logs -f

# View backend logs only
docker-compose logs -f backend

# View frontend logs only
docker-compose logs -f frontend
```

## Step 5: Stop Services

```bash
# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Troubleshooting

### Backend not starting?
```bash
# Check backend logs
docker-compose logs backend

# Rebuild backend
docker-compose up --build backend
```

### Frontend not loading?
```bash
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up --build frontend
```

### Port conflicts?
Edit `docker-compose.yml` and change the port mappings:
```yaml
ports:
  - "8080:80"  # Change 80 to 8080
```

## Development Mode

For development with hot reload:

### Backend
```bash
cd Backend
python app.py
```

### Frontend
```bash
cd Frontend
npm run dev
```

## Production Deployment

See deployment guides:
- `AWS_DEPLOYMENT_GUIDE.md` - Overview
- `AWS_ECS_DEPLOYMENT.md` - Detailed ECS setup
- `deploy.sh` - Automated deployment script
