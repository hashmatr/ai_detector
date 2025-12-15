# 🚀 Complete AWS Free Tier Deployment - Step by Step

## Part 1: Launch EC2 Instance (Detailed)

### Step 1.1: Go to AWS Console

1. **Sign in** to AWS Console: https://console.aws.amazon.com/
2. **Select Region**: Top-right corner → Choose **US East (N. Virginia)** or closest to you
3. **Go to EC2**: Search bar → Type "EC2" → Click **EC2**

### Step 1.2: Launch Instance

1. Click **"Launch Instance"** (orange button)

2. **Name your instance**:
   ```
   Name: ai-detector-server
   ```

3. **Application and OS Images (AMI)**:
   - Click: **Ubuntu**
   - Select: **Ubuntu Server 22.04 LTS (HVM), SSD Volume Type**
   - Make sure it says: **"Free tier eligible"** ✅

4. **Instance Type**:
   - Select: **t2.micro**
   - Should show: **"Free tier eligible"** ✅
   - Specs: 1 vCPU, 1 GiB Memory

5. **Key Pair (login)**:
   - Click: **"Create new key pair"**
   - Key pair name: `ai-detector-key`
   - Key pair type: **RSA**
   - Private key file format: **`.pem`** (for Mac/Linux) or **`.ppk`** (for Windows/PuTTY)
   - Click: **"Create key pair"**
   - **IMPORTANT**: File will download automatically - **SAVE IT SAFELY!**
   - File name: `ai-detector-key.pem`

6. **Network Settings**:
   - Click: **"Edit"** (top right of Network settings)
   - **Firewall (security groups)**: Select **"Create security group"**
   - Security group name: `ai-detector-sg`
   - Description: `Security group for AI Detector`
   
   **Add these rules** (click "Add security group rule" for each):
   
   | Type | Protocol | Port | Source | Description |
   |------|----------|------|--------|-------------|
   | SSH | TCP | 22 | 0.0.0.0/0 | SSH access |
   | HTTP | TCP | 80 | 0.0.0.0/0 | Web access |
   | Custom TCP | TCP | 5000 | 0.0.0.0/0 | API access |

7. **Configure Storage**:
   - Size: **30 GiB** (default)
   - Volume type: **gp3** (default)
   - Should show: **"Free tier eligible"** ✅

8. **Review Summary** (right panel):
   - Number of instances: **1**
   - Instance type: **t2.micro**
   - Free tier: **750 Hours per month**

9. Click **"Launch Instance"** (orange button)

10. **Success Screen**:
    - You'll see: "Successfully initiated launch of instance"
    - Click: **"View all instances"**

### Step 1.3: Get Instance Details

1. **Wait for instance to start** (2-3 minutes)
   - **Instance State**: Should change from "Pending" to **"Running"** ✅
   - **Status Check**: Should show **"2/2 checks passed"** ✅

2. **Get your Public IP**:
   - Click on your instance (checkbox)
   - Bottom panel → **"Details"** tab
   - Find: **"Public IPv4 address"**
   - Example: `3.85.123.456`
   - **COPY THIS IP** - you'll need it!

3. **Optional: Allocate Elastic IP** (so IP doesn't change):
   ```
   Left menu → Network & Security → Elastic IPs
   → Allocate Elastic IP address
   → Allocate
   → Actions → Associate Elastic IP address
   → Select your instance → Associate
   ```

---

## Part 2: Connect to EC2 Instance

### Step 2.1: Prepare SSH Key (Windows)

**Option A: Using Git Bash (Recommended)**
```bash
# Open Git Bash
# Navigate to where you downloaded the key
cd ~/Downloads

# Set correct permissions
chmod 400 ai-detector-key.pem

# Connect
ssh -i ai-detector-key.pem ubuntu@YOUR-EC2-PUBLIC-IP
```

**Option B: Using PowerShell**
```powershell
# Open PowerShell as Administrator
# Navigate to key location
cd $HOME\Downloads

# Connect (Windows 10/11 has built-in SSH)
ssh -i ai-detector-key.pem ubuntu@YOUR-EC2-PUBLIC-IP
```

**Option C: Using PuTTY (if you downloaded .ppk)**
1. Open PuTTY
2. Host Name: `ubuntu@YOUR-EC2-PUBLIC-IP`
3. Connection → SSH → Auth → Browse for your `.ppk` file
4. Click "Open"

### Step 2.2: First Connection

When you connect for the first time:
```
The authenticity of host 'X.X.X.X' can't be established.
Are you sure you want to continue connecting (yes/no)?
```
Type: **`yes`** and press Enter

You should see:
```
Welcome to Ubuntu 22.04 LTS
ubuntu@ip-XXX-XXX-XXX-XXX:~$
```

✅ **You're connected!**

---

## Part 3: Run Automated Setup

### Step 3.1: Download and Run Setup Script

Copy and paste these commands **one by one**:

```bash
# Download the setup script
curl -o setup.sh https://raw.githubusercontent.com/hashmatr/ai_detector/main/setup-ec2.sh

# Make it executable
chmod +x setup.sh

# Run the setup (this takes 10-15 minutes)
./setup.sh
```

### Step 3.2: What the Script Does

You'll see output like this:
```
🚀 AI Content Detector - Free Tier Setup
==========================================
Step 1: Updating system...
Step 2: Installing dependencies...
Step 3: Cloning repository...
Step 4: Setting up Backend...
Step 5: Setting up Frontend...
Step 6: Configuring Nginx...
Step 7: Creating Backend systemd service...
Step 8: Setting up swap space...
Step 9: Creating update script...
Step 10: Creating monitoring script...

==========================================
✅ Setup Complete!
==========================================

📍 Your application is accessible at:
   http://YOUR-EC2-IP

🔧 Useful Commands:
   Check status:    ./monitor.sh
   Update app:      ./update.sh
   View logs:       sudo journalctl -u ai-detector-backend -f
```

### Step 3.3: Verify Installation

```bash
# Check if backend is running
sudo systemctl status ai-detector-backend

# Check if Nginx is running
sudo systemctl status nginx

# Run monitoring script
./monitor.sh
```

---

## Part 4: Access Your Application

### Step 4.1: Open in Browser

1. Open your web browser
2. Go to: `http://YOUR-EC2-PUBLIC-IP`
3. You should see your **AI Content Detector**! 🎉

### Step 4.2: Test the Application

1. **Test Text Analysis**:
   - Paste some text
   - Click "Analyze Content"
   - Should show results

2. **Test File Upload**:
   - Upload a PDF or DOCX file
   - Should analyze the file

3. **Check Backend API**:
   - Go to: `http://YOUR-EC2-IP/api/info`
   - Should show model information

---

## Part 5: Customize App Name

### Option 1: Change "AI Content Detector" to Your Name

**On your local machine**, update these files:

#### 1. Frontend Title (`Frontend/index.html`):
```html
<!-- Change line ~7 -->
<title>Your Custom Name</title>
```

#### 2. Frontend Header (`Frontend/src/App.jsx`):
```javascript
// Change line ~313
<h1 className="header-title">Your Custom Name</h1>
```

#### 3. Frontend Header (`Frontend/src/AppEnhanced.jsx`):
```javascript
// Change line ~323
<h1 className="header-title">Your Custom Name</h1>
```

#### 4. README.md:
```markdown
# Your Custom Name

A sophisticated AI content detection system...
```

### Option 2: Use Automated Script

I'll create a script for you:

```bash
# On your local machine
# Run this script to change all instances
./customize-name.sh "Your Custom Name"
```

Then push to GitHub:
```bash
git add .
git commit -m "Customize app name"
git push origin main
```

Then on EC2:
```bash
# Update the deployed app
./update.sh
```

---

## Part 6: Management Commands

### On EC2 Instance:

```bash
# Check application status
./monitor.sh

# Update application (after pushing changes to GitHub)
./update.sh

# View backend logs (live)
sudo journalctl -u ai-detector-backend -f

# Restart backend
sudo systemctl restart ai-detector-backend

# Restart Nginx
sudo systemctl restart nginx

# Check disk space
df -h

# Check memory usage
free -h
```

---

## Part 7: Optional Enhancements

### Add Free Domain Name

**Option A: Freenom (Free .tk, .ml, .ga domains)**
1. Go to: https://www.freenom.com
2. Search for available domain
3. Register for free (12 months)
4. Point to your EC2 IP

**Option B: DuckDNS (Free subdomain)**
1. Go to: https://www.duckdns.org
2. Sign in with GitHub/Google
3. Create subdomain: `yourname.duckdns.org`
4. Point to your EC2 IP

### Add Free SSL Certificate

```bash
# On EC2 instance
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com

# Certificate auto-renews automatically!
```

Now access via: `https://yourdomain.com` 🔒

---

## Troubleshooting

### Can't SSH to EC2?
```bash
# Check key permissions
chmod 400 ai-detector-key.pem

# Verify security group allows port 22
# Check EC2 Console → Security Groups → Inbound rules
```

### Setup script fails?
```bash
# Check if you have internet
ping google.com

# Try running script again
./setup.sh
```

### Can't access app in browser?
```bash
# Check if services are running
sudo systemctl status ai-detector-backend
sudo systemctl status nginx

# Check security group allows port 80
# EC2 Console → Security Groups → Inbound rules

# Check logs
sudo journalctl -u ai-detector-backend -n 50
```

### Backend not starting?
```bash
# Check logs
sudo journalctl -u ai-detector-backend -f

# Check if port 5000 is in use
sudo netstat -tulpn | grep 5000

# Restart service
sudo systemctl restart ai-detector-backend
```

---

## Cost Monitoring

### Check Free Tier Usage

1. **AWS Console** → **Billing Dashboard**
2. Click: **"Free Tier"** (left menu)
3. Monitor:
   - EC2 hours used (750/month free)
   - Data transfer (15GB/month free)
   - Storage (30GB free)

### Set Up Billing Alert

1. **Billing Dashboard** → **Billing Preferences**
2. Enable: **"Receive Free Tier Usage Alerts"**
3. Enable: **"Receive Billing Alerts"**
4. Set alert at: **$1** (to catch any charges early)

---

## Summary Checklist

- [ ] AWS account created
- [ ] EC2 t2.micro instance launched
- [ ] Security group configured (ports 22, 80, 5000)
- [ ] SSH key downloaded and saved
- [ ] Connected to EC2 via SSH
- [ ] Setup script executed successfully
- [ ] App accessible at http://EC2-IP
- [ ] Backend API working
- [ ] Can analyze text
- [ ] Can upload files
- [ ] (Optional) Custom domain configured
- [ ] (Optional) SSL certificate installed
- [ ] Billing alerts set up

---

## Quick Reference

| What | Command/URL |
|------|-------------|
| **Access App** | `http://YOUR-EC2-IP` |
| **SSH Connect** | `ssh -i ai-detector-key.pem ubuntu@YOUR-EC2-IP` |
| **Check Status** | `./monitor.sh` |
| **Update App** | `./update.sh` |
| **View Logs** | `sudo journalctl -u ai-detector-backend -f` |
| **Restart Backend** | `sudo systemctl restart ai-detector-backend` |

---

**🎉 Congratulations! Your AI Content Detector is live on AWS!**

**Total Cost**: $0/month (Free Tier)  
**Total Time**: ~15 minutes  
**Your App**: `http://YOUR-EC2-IP`
