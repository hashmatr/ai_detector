# 🔧 Fix: Nginx Configuration Not Found

## The Issue
You're in the home directory (`~`), but the files are in `/home/ubuntu/ai_detector/`

## Solution - Run These Commands:

```bash
# Step 1: Navigate to the project directory
cd /home/ubuntu/ai_detector

# Step 2: Pull latest changes from GitHub
git pull origin main

# Step 3: Make the script executable
chmod +x update-nginx.sh

# Step 4: Run the update script
./update-nginx.sh
```

## If Git Pull Fails

If you get an error like "repository not found" or "not a git repository":

```bash
# Check if you're in the right directory
pwd
# Should show: /home/ubuntu/ai_detector

# If the directory doesn't exist, clone it:
cd /home/ubuntu
git clone https://github.com/hashmatr/ai_detector.git
cd ai_detector

# Then run the update script
chmod +x update-nginx.sh
./update-nginx.sh
```

## Manual Method (If Script Still Not Found)

If the script still isn't there, create it manually:

```bash
# Navigate to project directory
cd /home/ubuntu/ai_detector

# Create the nginx config file
sudo nano /etc/nginx/sites-available/ai-detector
```

Then paste this configuration:

```nginx
server {
    listen 80;
    server_name 51.21.253.28;

    # Frontend
    location / {
        root /home/ubuntu/ai_detector/Frontend/dist;
        try_files $uri $uri/ /index.html;
        index index.html;
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
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Direct backend endpoints
    location /predict {
        proxy_pass http://localhost:5000/predict;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        client_max_body_size 10M;
    }

    location /predict-file {
        proxy_pass http://localhost:5000/predict-file;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        client_max_body_size 10M;
    }

    location /info {
        proxy_pass http://localhost:5000/info;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
```

Save with `Ctrl+X`, then `Y`, then `Enter`.

Then:
```bash
# Test the configuration
sudo nginx -t

# If test passes, reload nginx
sudo systemctl reload nginx
```

## Verify It's Working

```bash
# Test from EC2
curl http://51.21.253.28

# Check nginx status
sudo systemctl status nginx

# Check backend status
sudo systemctl status ai-detector-backend
```

## Quick Troubleshooting

### Check if files exist:
```bash
ls -la /home/ubuntu/ai_detector/
```

### Check current directory:
```bash
pwd
```

### Check if git repository exists:
```bash
cd /home/ubuntu/ai_detector
git status
```

## Complete Fresh Start (If Needed)

If nothing works, start fresh:

```bash
# Go to home directory
cd /home/ubuntu

# Remove old directory (if exists)
rm -rf ai_detector

# Clone fresh from GitHub
git clone https://github.com/hashmatr/ai_detector.git

# Navigate to directory
cd ai_detector

# Run setup script
chmod +x setup-ec2.sh
./setup-ec2.sh
```

This will set up everything from scratch!
