# 🔧 Apply Nginx Configuration for 51.21.253.28

## What Was Added

✅ **nginx-production.conf** - Production nginx config with your IP  
✅ **update-nginx.sh** - Script to apply the configuration  
✅ **PRODUCTION_CONFIG.md** - Complete documentation  

All files pushed to GitHub! ✅

---

## How to Apply on Your EC2 Server

### Step 1: SSH into Your Server

```bash
ssh -i ai-detector-key.pem ubuntu@51.21.253.28
```

### Step 2: Pull Latest Changes

```bash
cd /home/ubuntu/ai_detector
git pull origin main
```

### Step 3: Apply Nginx Configuration

```bash
chmod +x update-nginx.sh
./update-nginx.sh
```

You'll see:
```
🔧 Updating Nginx Configuration
================================
📦 Creating backup...
📝 Updating configuration...
🧪 Testing Nginx configuration...
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
✅ Configuration is valid
🔄 Reloading Nginx...
✅ Nginx configuration updated successfully!

📍 Your app is now configured for:
   http://51.21.253.28
```

---

## Step 4: Verify It's Working

### Test in Browser:
- **Frontend**: http://51.21.253.28
- **API Info**: http://51.21.253.28/info

### Test from Terminal:
```bash
# Test frontend
curl http://51.21.253.28

# Test API
curl http://51.21.253.28/info

# Test prediction
curl -X POST http://51.21.253.28/predict \
  -H "Content-Type: application/json" \
  -d '{"text":"Test text for analysis"}'
```

---

## What the Configuration Does

✅ **Server Name**: Set to `51.21.253.28`  
✅ **Frontend**: Serves React app from `/home/ubuntu/ai_detector/Frontend/dist`  
✅ **API Proxy**: Routes `/api/*` to backend on port 5000  
✅ **Direct Access**: `/predict`, `/info` endpoints work directly  
✅ **File Uploads**: Max 10MB  
✅ **Caching**: Static assets cached for 1 year  
✅ **Security Headers**: X-Frame-Options, XSS Protection, etc.  
✅ **Compression**: Gzip enabled  

---

## Troubleshooting

### If nginx test fails:
```bash
# Check syntax
sudo nginx -t

# View error details
sudo tail -f /var/log/nginx/error.log
```

### If app doesn't load:
```bash
# Check nginx is running
sudo systemctl status nginx

# Check backend is running
sudo systemctl status ai-detector-backend

# Restart both
sudo systemctl restart nginx
sudo systemctl restart ai-detector-backend
```

### View logs:
```bash
# Nginx access log
sudo tail -f /var/log/nginx/access.log

# Nginx error log
sudo tail -f /var/log/nginx/error.log

# Backend log
sudo journalctl -u ai-detector-backend -f
```

---

## Quick Commands

```bash
# Apply nginx config
./update-nginx.sh

# Check status
./monitor.sh

# Restart services
sudo systemctl restart nginx
sudo systemctl restart ai-detector-backend

# View logs
sudo journalctl -u ai-detector-backend -f
```

---

## ✅ Success!

Your app is now configured for:

**🌐 Frontend**: http://51.21.253.28  
**🔌 API**: http://51.21.253.28/api/  
**📊 Info**: http://51.21.253.28/info  

---

## Next Steps (Optional)

### 1. Get a Domain Name (Free)
- **Freenom**: Free .tk, .ml, .ga domains
- **DuckDNS**: Free subdomain (yourname.duckdns.org)
- **No-IP**: Free dynamic DNS

### 2. Add SSL Certificate (Free)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 3. Set Up Monitoring
- CloudWatch (AWS)
- Uptime monitoring
- Error alerts

---

**Your AI Content Detector is live at http://51.21.253.28** 🎉
