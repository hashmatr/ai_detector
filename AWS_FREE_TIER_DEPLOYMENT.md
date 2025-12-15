# 🆓 AWS Free Tier Deployment Guide

## 💰 Cost: ~$0-15/month (Mostly FREE!)

This guide shows you how to deploy your AI Content Detector using **AWS Free Tier** services to minimize costs.

---

## 🎯 Free Tier Architecture

```
Internet
   ↓
EC2 t2.micro (FREE for 12 months)
   ├── Frontend (Nginx on port 80)
   └── Backend (Flask on port 5000)
        └── S3 (FREE 5GB storage)
```

**What's FREE:**
- ✅ EC2 t2.micro: 750 hours/month (1 instance 24/7)
- ✅ S3: 5GB storage
- ✅ Data Transfer: 15GB/month outbound
- ✅ Elastic IP: 1 free (when attached to running instance)

**What Costs Money:**
- ❌ Load Balancer: ~$16/month (we'll skip this)
- ❌ ECS Fargate: Not free tier eligible
- ❌ CloudFront: Not needed for small projects

**Estimated Cost: $0-5/month** (within free tier limits)

---

## 📋 Prerequisites

1. **AWS Account** (Free tier eligible - first 12 months)
2. **AWS CLI** installed
3. **SSH key pair** for EC2 access

---

## 🚀 Step-by-Step Deployment

### Step 1: Create EC2 Instance

#### 1.1 Launch Instance via AWS Console

1. Go to **EC2 Dashboard** → **Launch Instance**
2. **Name**: `ai-detector-server`
3. **AMI**: Ubuntu Server 22.04 LTS (Free tier eligible)
4. **Instance Type**: `t2.micro` (FREE - 1GB RAM, 1 vCPU)
5. **Key Pair**: Create new or select existing
6. **Network Settings**:
   - Allow SSH (port 22)
   - Allow HTTP (port 80)
   - Allow Custom TCP (port 5000) for API
7. **Storage**: 30GB gp3 (FREE tier: 30GB)
8. Click **Launch Instance**

#### 1.2 Or Use AWS CLI

```bash
# Create security group
aws ec2 create-security-group \
    --group-name ai-detector-sg \
    --description "AI Detector Security Group"

# Add rules
aws ec2 authorize-security-group-ingress \
    --group-name ai-detector-sg \
    --protocol tcp --port 22 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-name ai-detector-sg \
    --protocol tcp --port 80 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-name ai-detector-sg \
    --protocol tcp --port 5000 --cidr 0.0.0.0/0

# Launch instance
aws ec2 run-instances \
    --image-id ami-0c7217cdde317cfec \
    --instance-type t2.micro \
    --key-name YOUR-KEY-NAME \
    --security-groups ai-detector-sg \
    --block-device-mappings DeviceName=/dev/sda1,Ebs={VolumeSize=30}
```

### Step 2: Connect to EC2 Instance

```bash
# Get instance public IP
aws ec2 describe-instances \
    --filters "Name=tag:Name,Values=ai-detector-server" \
    --query 'Reservations[0].Instances[0].PublicIpAddress'

# SSH into instance
ssh -i your-key.pem ubuntu@YOUR-EC2-PUBLIC-IP
```

### Step 3: Install Dependencies on EC2

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv

# Install Node.js and npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Nginx
sudo apt install -y nginx

# Install Git
sudo apt install -y git

# Install Docker (optional, for easier deployment)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu
```

### Step 4: Clone and Setup Application

```bash
# Clone repository
cd /home/ubuntu
git clone https://github.com/hashmatr/ai_detector.git
cd ai_detector

# Setup Backend
cd Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Note: Model files need to be uploaded separately (see Step 5)

# Setup Frontend
cd ../Frontend
npm install
npm run build
```

### Step 5: Upload Model Files to S3 (FREE)

```bash
# On your local machine
# Create S3 bucket (FREE 5GB)
aws s3 mb s3://ai-detector-models-YOUR-NAME

# Upload model files
aws s3 cp Backend/Models/ s3://ai-detector-models-YOUR-NAME/models/ --recursive

# On EC2, download models when needed
# Add to Backend startup script:
aws s3 sync s3://ai-detector-models-YOUR-NAME/models/ /home/ubuntu/ai_detector/Backend/Models/
```

### Step 6: Configure Nginx

```bash
# Create Nginx config
sudo nano /etc/nginx/sites-available/ai-detector
```

Add this configuration:

```nginx
server {
    listen 80;
    server_name YOUR-EC2-PUBLIC-IP;

    # Frontend
    location / {
        root /home/ubuntu/ai_detector/Frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:5000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Enable the site:

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/ai-detector /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### Step 7: Setup Backend as System Service

```bash
# Create systemd service
sudo nano /etc/systemd/system/ai-detector-backend.service
```

Add this content:

```ini
[Unit]
Description=AI Detector Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai_detector/Backend
Environment="PATH=/home/ubuntu/ai_detector/Backend/venv/bin"
ExecStart=/home/ubuntu/ai_detector/Backend/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start service
sudo systemctl start ai-detector-backend

# Enable on boot
sudo systemctl enable ai-detector-backend

# Check status
sudo systemctl status ai-detector-backend
```

### Step 8: Update Frontend API URL

On your local machine, update Frontend to use EC2 IP:

```javascript
// Frontend/src/App.jsx or config file
const API_URL = 'http://YOUR-EC2-PUBLIC-IP/api';
```

Rebuild and upload:

```bash
cd Frontend
npm run build

# Upload to EC2
scp -i your-key.pem -r dist/* ubuntu@YOUR-EC2-PUBLIC-IP:/home/ubuntu/ai_detector/Frontend/dist/
```

### Step 9: Access Your Application

```
http://YOUR-EC2-PUBLIC-IP
```

---

## 🔒 Optional: Add Free SSL Certificate

Use **Let's Encrypt** (FREE):

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate (requires domain name)
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is configured automatically
```

---

## 📊 Monitoring (FREE)

### CloudWatch Logs (FREE within limits)

```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure to send logs
```

### Simple Monitoring Script

```bash
# Create monitoring script
nano ~/monitor.sh
```

```bash
#!/bin/bash
# Simple monitoring
echo "=== System Status ==="
date
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)"
echo "Memory Usage:"
free -h
echo "Disk Usage:"
df -h
echo "Backend Status:"
systemctl status ai-detector-backend --no-pager
```

```bash
chmod +x ~/monitor.sh
# Run: ./monitor.sh
```

---

## 🔄 Easy Update Script

Create `update.sh` on EC2:

```bash
#!/bin/bash
cd /home/ubuntu/ai_detector

# Pull latest code
git pull origin main

# Update Backend
cd Backend
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart ai-detector-backend

# Update Frontend
cd ../Frontend
npm install
npm run build

# Restart Nginx
sudo systemctl restart nginx

echo "✅ Update complete!"
```

Make it executable:

```bash
chmod +x update.sh
```

---

## 💰 Cost Breakdown (FREE TIER)

| Service | Free Tier | Usage | Cost |
|---------|-----------|-------|------|
| EC2 t2.micro | 750 hrs/month | 24/7 | **$0** |
| EBS Storage | 30GB | 30GB | **$0** |
| S3 Storage | 5GB | ~2GB models | **$0** |
| Data Transfer | 15GB/month | ~5GB | **$0** |
| Elastic IP | 1 free | 1 | **$0** |
| **Total** | | | **$0/month** |

**After 12 months:**
- EC2 t2.micro: ~$8.50/month
- EBS 30GB: ~$3/month
- S3: ~$0.50/month
- **Total: ~$12/month**

---

## 🎯 Optimization Tips

### 1. Reduce Memory Usage

```python
# In Backend/app.py, add:
import gc
gc.collect()  # Force garbage collection
```

### 2. Use Swap Space (if needed)

```bash
# Create 2GB swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 3. Optimize Model Loading

```python
# Load models only when needed
# Cache predictions
# Use smaller model variants if available
```

---

## 🚨 Troubleshooting

### Backend won't start

```bash
# Check logs
sudo journalctl -u ai-detector-backend -f

# Check if port is in use
sudo netstat -tulpn | grep 5000

# Restart service
sudo systemctl restart ai-detector-backend
```

### Out of Memory

```bash
# Check memory
free -h

# Add swap (see optimization tips)
# Or reduce model size
```

### Can't access from browser

```bash
# Check security group allows port 80
# Check Nginx is running
sudo systemctl status nginx

# Check firewall
sudo ufw status
```

---

## 📝 Maintenance Checklist

- [ ] Monitor disk space: `df -h`
- [ ] Check memory usage: `free -h`
- [ ] Review logs: `sudo journalctl -u ai-detector-backend`
- [ ] Update system: `sudo apt update && sudo apt upgrade`
- [ ] Backup models to S3
- [ ] Monitor AWS Free Tier usage in console

---

## 🎉 Success!

Your AI Content Detector is now running on AWS Free Tier!

**Access**: `http://YOUR-EC2-PUBLIC-IP`

**Costs**: $0/month (within free tier)

**Next Steps**:
1. Get a free domain from Freenom or use Route 53
2. Add SSL with Let's Encrypt (FREE)
3. Set up automatic backups
4. Monitor usage to stay within free tier

---

## 🔗 Useful Links

- **AWS Free Tier**: https://aws.amazon.com/free/
- **EC2 Pricing**: https://aws.amazon.com/ec2/pricing/
- **Let's Encrypt**: https://letsencrypt.org/
- **Monitor Free Tier Usage**: AWS Console → Billing Dashboard

---

**Need help?** Check logs with `sudo journalctl -u ai-detector-backend -f`
