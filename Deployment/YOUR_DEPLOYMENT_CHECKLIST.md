# 🚀 YOUR DEPLOYMENT CHECKLIST

## ✅ What to Do After Launching EC2 Instance

### 📥 Step 1: Download SSH Key (IMPORTANT!)

When creating your EC2 instance, you'll create a key pair:
- **Key name**: `ai-detector-key`
- **File downloads**: `ai-detector-key.pem`
- **SAVE THIS FILE!** You can't download it again!
- **Save location**: `C:\Users\YourName\Downloads\ai-detector-key.pem`

---

### 🔌 Step 2: Connect to EC2

**Using Git Bash (Recommended for Windows):**
```bash
# Open Git Bash
cd ~/Downloads

# Set permissions
chmod 400 ai-detector-key.pem

# Connect (replace with YOUR EC2 IP)
ssh -i ai-detector-key.pem ubuntu@YOUR-EC2-IP
```

**Using PowerShell:**
```powershell
# Open PowerShell
cd $HOME\Downloads

# Connect (replace with YOUR EC2 IP)
ssh -i ai-detector-key.pem ubuntu@YOUR-EC2-IP
```

**First time?** Type `yes` when asked about authenticity.

---

### 🤖 Step 3: Run Setup Script

**Copy and paste these commands ONE BY ONE:**

```bash
# Download setup script
curl -o setup.sh https://raw.githubusercontent.com/hashmatr/ai_detector/main/setup-ec2.sh

# Make executable
chmod +x setup.sh

# Run setup (takes 10-15 minutes)
./setup.sh
```

**Wait for**: "✅ Setup Complete!"

---

### 🌐 Step 4: Access Your App

Open browser and go to:
```
http://YOUR-EC2-IP
```

Replace `YOUR-EC2-IP` with the actual IP from AWS Console.

**Example**: `http://3.85.123.456`

---

## 🎨 How to Change App Name

### Option 1: Manual (Simple)

**On your local machine**, edit these files:

1. **`Frontend/index.html`** (Line ~7):
   ```html
   <title>Your Custom Name</title>
   ```

2. **`Frontend/src/App.jsx`** (Line ~313):
   ```javascript
   <h1 className="header-title">Your Custom Name</h1>
   ```

3. **`Frontend/src/AppEnhanced.jsx`** (Line ~323):
   ```javascript
   <h1 className="header-title">Your Custom Name</h1>
   ```

4. **`README.md`** (Line 1):
   ```markdown
   # Your Custom Name
   ```

Then:
```bash
cd Frontend
npm run build
git add .
git commit -m "Change app name to Your Custom Name"
git push origin main
```

On EC2:
```bash
./update.sh
```

### Option 2: Automated Script (Easier!)

**Windows (PowerShell):**
```powershell
.\customize-name.ps1 "Your Custom Name"
cd Frontend
npm run build
git add .
git commit -m "Customize app name"
git push origin main
```

**Linux/Mac:**
```bash
chmod +x customize-name.sh
./customize-name.sh "Your Custom Name"
cd Frontend
npm run build
git add .
git commit -m "Customize app name"
git push origin main
```

Then on EC2:
```bash
./update.sh
```

---

## 📋 Complete Deployment Steps

### Before You Start:
- [ ] AWS Account created
- [ ] Credit card added (won't be charged with free tier)
- [ ] Chosen a region (e.g., US East N. Virginia)

### Launch EC2:
- [ ] Go to EC2 Dashboard
- [ ] Click "Launch Instance"
- [ ] Name: `ai-detector-server`
- [ ] AMI: Ubuntu 22.04 LTS (Free tier)
- [ ] Instance type: t2.micro (Free tier)
- [ ] Create key pair: `ai-detector-key`
- [ ] **DOWNLOAD AND SAVE THE .pem FILE!**
- [ ] Security group: Allow ports 22, 80, 5000
- [ ] Storage: 30GB
- [ ] Click "Launch Instance"

### After Launch:
- [ ] Wait for "Running" status (2-3 min)
- [ ] Copy Public IPv4 address
- [ ] Save it somewhere: `YOUR-EC2-IP = _______________`

### Connect:
- [ ] Open Git Bash or PowerShell
- [ ] Navigate to Downloads folder
- [ ] Run: `chmod 400 ai-detector-key.pem` (Git Bash)
- [ ] Connect: `ssh -i ai-detector-key.pem ubuntu@YOUR-EC2-IP`
- [ ] Type `yes` when prompted

### Deploy:
- [ ] Run: `curl -o setup.sh https://raw.githubusercontent.com/hashmatr/ai_detector/main/setup-ec2.sh`
- [ ] Run: `chmod +x setup.sh`
- [ ] Run: `./setup.sh`
- [ ] Wait 10-15 minutes
- [ ] See "✅ Setup Complete!"

### Test:
- [ ] Open browser
- [ ] Go to: `http://YOUR-EC2-IP`
- [ ] See your AI Content Detector!
- [ ] Test text analysis
- [ ] Test file upload

### Customize (Optional):
- [ ] Choose a custom name
- [ ] Run customization script
- [ ] Rebuild frontend
- [ ] Push to GitHub
- [ ] Run `./update.sh` on EC2

### Optional Enhancements:
- [ ] Get free domain (Freenom, DuckDNS)
- [ ] Add SSL certificate (Let's Encrypt)
- [ ] Set up billing alerts

---

## 🆘 Troubleshooting

### Can't SSH?
```bash
# Check key permissions
chmod 400 ai-detector-key.pem

# Try with full path
ssh -i C:/Users/YourName/Downloads/ai-detector-key.pem ubuntu@YOUR-EC2-IP
```

### Setup fails?
```bash
# Run again
./setup.sh

# Or check logs
cat /var/log/cloud-init-output.log
```

### Can't access app?
1. Check security group allows port 80
2. Check services: `./monitor.sh`
3. Check logs: `sudo journalctl -u ai-detector-backend -f`

---

## 🔧 Useful Commands (On EC2)

```bash
# Check status
./monitor.sh

# Update app (after pushing to GitHub)
./update.sh

# View logs
sudo journalctl -u ai-detector-backend -f

# Restart backend
sudo systemctl restart ai-detector-backend

# Restart Nginx
sudo systemctl restart nginx

# Check disk space
df -h

# Check memory
free -h
```

---

## 💰 Cost Reminder

**Free Tier (12 months):**
- EC2 t2.micro: 750 hours/month = **$0**
- Storage 30GB: **$0**
- Data transfer 15GB: **$0**
- **TOTAL: $0/month** ✅

**After 12 months:**
- ~$12-15/month

**Monitor usage:**
AWS Console → Billing Dashboard → Free Tier

---

## 📞 Need Help?

**Detailed Guides:**
- `STEP_BY_STEP_DEPLOYMENT.md` - Complete walkthrough
- `AWS_FREE_TIER_DEPLOYMENT.md` - Detailed free tier guide
- `FREE_TIER_QUICKSTART.md` - Quick 3-step guide

**Quick Commands:**
- `QUICK_REFERENCE.md` - Command cheat sheet

---

## ✅ Success Criteria

Your deployment is successful when:
- ✅ Can SSH into EC2
- ✅ Setup script completes without errors
- ✅ App loads at `http://YOUR-EC2-IP`
- ✅ Can analyze text
- ✅ Can upload files
- ✅ Backend API responds at `/api/info`

---

## 🎉 You're Done!

**Your App**: `http://YOUR-EC2-IP`  
**Cost**: $0/month (Free Tier)  
**Time**: 15 minutes  

**Customize it, share it, enjoy it!** 🚀
