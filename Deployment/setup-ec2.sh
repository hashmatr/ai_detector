#!/bin/bash

# AI Content Detector - Free Tier EC2 Setup Script
# Run this script on your EC2 t2.micro instance after SSH

set -e

echo "🚀 AI Content Detector - Free Tier Setup"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPO_URL="https://github.com/hashmatr/ai_detector.git"
APP_DIR="/home/ubuntu/ai_detector"
BACKEND_SERVICE="ai-detector-backend"

echo -e "${BLUE}Step 1: Updating system...${NC}"
sudo apt update && sudo apt upgrade -y

echo -e "${BLUE}Step 2: Installing dependencies...${NC}"
# Python
sudo apt install -y python3 python3-pip python3-venv

# Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Nginx
sudo apt install -y nginx

# Git
sudo apt install -y git

echo -e "${BLUE}Step 3: Cloning repository...${NC}"
cd /home/ubuntu
if [ -d "$APP_DIR" ]; then
    echo "Repository already exists, pulling latest changes..."
    cd $APP_DIR
    git pull origin main
else
    git clone $REPO_URL
    cd $APP_DIR
fi

echo -e "${BLUE}Step 4: Setting up Backend...${NC}"
cd Backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${BLUE}Step 5: Setting up Frontend...${NC}"
cd ../Frontend
npm install
npm run build

echo -e "${BLUE}Step 6: Configuring Nginx...${NC}"
# Get EC2 public IP
PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)

# Create Nginx configuration
sudo tee /etc/nginx/sites-available/ai-detector > /dev/null <<EOF
server {
    listen 80;
    server_name $PUBLIC_IP;

    # Frontend
    location / {
        root $APP_DIR/Frontend/dist;
        try_files \$uri \$uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:5000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/ai-detector /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test and restart Nginx
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

echo -e "${BLUE}Step 7: Creating Backend systemd service...${NC}"
sudo tee /etc/systemd/system/$BACKEND_SERVICE.service > /dev/null <<EOF
[Unit]
Description=AI Detector Backend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=$APP_DIR/Backend
Environment="PATH=$APP_DIR/Backend/venv/bin"
ExecStart=$APP_DIR/Backend/venv/bin/python app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Start and enable service
sudo systemctl daemon-reload
sudo systemctl start $BACKEND_SERVICE
sudo systemctl enable $BACKEND_SERVICE

echo -e "${BLUE}Step 8: Setting up swap space (for t2.micro)...${NC}"
if [ ! -f /swapfile ]; then
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "Swap created: 2GB"
else
    echo "Swap already exists"
fi

echo -e "${BLUE}Step 9: Creating update script...${NC}"
cat > $APP_DIR/update.sh <<'EOF'
#!/bin/bash
cd /home/ubuntu/ai_detector
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

sudo systemctl restart nginx
echo "✅ Update complete!"
EOF

chmod +x $APP_DIR/update.sh

echo -e "${BLUE}Step 10: Creating monitoring script...${NC}"
cat > $APP_DIR/monitor.sh <<'EOF'
#!/bin/bash
echo "=== AI Detector Status ==="
date
echo ""
echo "Backend Service:"
sudo systemctl status ai-detector-backend --no-pager | head -10
echo ""
echo "Nginx Status:"
sudo systemctl status nginx --no-pager | head -5
echo ""
echo "System Resources:"
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1
echo "Memory Usage:"
free -h | grep Mem | awk '{print "Used: " $3 " / Total: " $2}'
echo "Disk Usage:"
df -h / | tail -1 | awk '{print "Used: " $3 " / Total: " $2 " (" $5 " full)"}'
echo ""
echo "Recent Backend Logs:"
sudo journalctl -u ai-detector-backend -n 5 --no-pager
EOF

chmod +x $APP_DIR/monitor.sh

echo ""
echo -e "${GREEN}=========================================="
echo "✅ Setup Complete!"
echo "==========================================${NC}"
echo ""
echo "📍 Your application is accessible at:"
echo "   http://$PUBLIC_IP"
echo ""
echo "🔧 Useful Commands:"
echo "   Check status:    ./monitor.sh"
echo "   Update app:      ./update.sh"
echo "   View logs:       sudo journalctl -u ai-detector-backend -f"
echo "   Restart backend: sudo systemctl restart ai-detector-backend"
echo "   Restart nginx:   sudo systemctl restart nginx"
echo ""
echo "📊 Service Status:"
sudo systemctl status ai-detector-backend --no-pager | head -3
echo ""
echo "🎉 Happy deploying!"
