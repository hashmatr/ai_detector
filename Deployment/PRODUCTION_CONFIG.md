# Production Environment Configuration

## Your Server Details
- **Server IP**: 51.21.253.28
- **Frontend URL**: http://51.21.253.28
- **Backend API**: http://51.21.253.28/api/
- **Direct API**: http://51.21.253.28/predict

## After Deployment

### 1. Update Nginx Configuration

On your EC2 instance, run:
```bash
cd /home/ubuntu/ai_detector
chmod +x update-nginx.sh
./update-nginx.sh
```

This will:
- ✅ Backup existing nginx config
- ✅ Apply new config with your IP (51.21.253.28)
- ✅ Test configuration
- ✅ Reload nginx

### 2. Access Your Application

**Frontend**: http://51.21.253.28  
**API Info**: http://51.21.253.28/info  
**API via proxy**: http://51.21.253.28/api/info

### 3. Test Endpoints

```bash
# Test frontend
curl http://51.21.253.28

# Test API directly
curl http://51.21.253.28/info

# Test API via proxy
curl http://51.21.253.28/api/info

# Test prediction
curl -X POST http://51.21.253.28/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"This is a test text to analyze for AI content detection."}'
```

### 4. Verify Services

```bash
# Check nginx status
sudo systemctl status nginx

# Check backend status
sudo systemctl status ai-detector-backend

# View nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# View backend logs
sudo journalctl -u ai-detector-backend -f
```

## Configuration Files

- **Nginx Config**: `nginx-production.conf`
- **Update Script**: `update-nginx.sh`
- **Vite Config** (dev only): `Frontend/vite.config.js`

## Notes

- The frontend is built as static files and served by Nginx
- Backend API runs on port 5000 (localhost only)
- Nginx proxies `/api/` requests to `http://localhost:5000/`
- Direct endpoints (`/predict`, `/info`) also proxied for compatibility
- Max file upload size: 10MB

## Security

Current setup:
- ✅ HTTP on port 80
- ✅ Backend not directly exposed (only via Nginx proxy)
- ✅ Security headers configured
- ⚠️ No HTTPS yet (add SSL certificate for production)

### To Add HTTPS (Optional):

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get free SSL certificate (requires domain name)
sudo certbot --nginx -d yourdomain.com

# Or use your IP with self-signed cert (not recommended for production)
```

## Troubleshooting

### Frontend not loading?
```bash
# Check nginx
sudo systemctl status nginx
sudo nginx -t

# Check if files exist
ls -la /home/ubuntu/ai_detector/Frontend/dist/
```

### API not responding?
```bash
# Check backend
sudo systemctl status ai-detector-backend
sudo journalctl -u ai-detector-backend -n 50

# Test backend directly
curl http://localhost:5000/info
```

### 502 Bad Gateway?
```bash
# Backend is probably not running
sudo systemctl restart ai-detector-backend

# Check logs
sudo journalctl -u ai-detector-backend -f
```

## Quick Commands

```bash
# Update nginx config
./update-nginx.sh

# Restart backend
sudo systemctl restart ai-detector-backend

# Restart nginx
sudo systemctl restart nginx

# Check all services
./monitor.sh

# Update application
./update.sh
```
