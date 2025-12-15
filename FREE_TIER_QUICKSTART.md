# 🎯 Free Tier Deployment - Quick Start

## Total Cost: **$0/month** (First 12 months)

This is the **simplest and cheapest** way to deploy your AI Content Detector on AWS.

---

## 🚀 Quick Deploy (3 Steps)

### Step 1: Launch EC2 Instance (5 minutes)

1. **Go to AWS Console** → EC2 → Launch Instance
2. **Settings**:
   - Name: `ai-detector`
   - AMI: **Ubuntu 22.04 LTS** (Free tier)
   - Instance type: **t2.micro** (Free tier - 1GB RAM)
   - Key pair: Create new (download .pem file)
   - Security group: Allow ports **22, 80, 5000**
   - Storage: **30GB** (Free tier)
3. Click **Launch Instance**

### Step 2: Run Setup Script (10 minutes)

```bash
# SSH into your instance
ssh -i your-key.pem ubuntu@YOUR-EC2-IP

# Download and run setup script
curl -o setup.sh https://raw.githubusercontent.com/hashmatr/ai_detector/main/setup-ec2.sh
chmod +x setup.sh
./setup.sh
```

### Step 3: Access Your App

```
http://YOUR-EC2-IP
```

**That's it!** ✅

---

## 📋 What You Need

- [ ] AWS Account (Free tier eligible)
- [ ] 15 minutes of time
- [ ] SSH key pair

---

## 💰 Cost Breakdown

| Service | Free Tier | Your Usage | Cost |
|---------|-----------|------------|------|
| EC2 t2.micro | 750 hrs/month | 24/7 | **$0** |
| Storage (30GB) | 30GB | 30GB | **$0** |
| Data Transfer | 15GB/month | ~5GB | **$0** |
| **TOTAL** | | | **$0/month** |

**After 12 months**: ~$12/month

---

## 🔧 Management Commands

After setup, use these commands on your EC2 instance:

```bash
# Check status
./monitor.sh

# Update application
./update.sh

# View logs
sudo journalctl -u ai-detector-backend -f

# Restart services
sudo systemctl restart ai-detector-backend
sudo systemctl restart nginx
```

---

## 🎯 Features Included

✅ **Automatic Setup** - One script does everything  
✅ **Auto-restart** - Services restart on failure  
✅ **Monitoring** - Built-in status checker  
✅ **Easy Updates** - One command to update  
✅ **Optimized** - Swap space for t2.micro  
✅ **Production Ready** - Nginx + systemd  

---

## 📊 Performance

**t2.micro specs:**
- 1 vCPU
- 1 GB RAM
- 2 GB Swap (added by script)
- Can handle: ~10-50 concurrent users

**Good for:**
- ✅ Personal projects
- ✅ Demos
- ✅ Small-scale testing
- ✅ Portfolio projects

**Not suitable for:**
- ❌ High traffic (>100 concurrent users)
- ❌ Large file processing
- ❌ Production at scale

---

## 🔒 Optional: Add Free SSL

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate (requires domain)
sudo certbot --nginx -d yourdomain.com

# Auto-renewal configured automatically
```

**Free domain options:**
- Freenom (free .tk, .ml, .ga domains)
- DuckDNS (free subdomain)
- No-IP (free dynamic DNS)

---

## 🆙 Upgrade Path

When you outgrow free tier:

1. **t2.small** (~$17/month) - 2GB RAM
2. **t3.small** (~$15/month) - 2GB RAM, better performance
3. **Add Load Balancer** - For high availability
4. **Use RDS** - For database (if needed)

---

## 🚨 Troubleshooting

### Can't SSH?
```bash
# Check security group allows port 22
# Verify key permissions
chmod 400 your-key.pem
```

### Setup script fails?
```bash
# Check logs
cat /var/log/cloud-init-output.log

# Run script again
./setup.sh
```

### App not accessible?
```bash
# Check services
sudo systemctl status ai-detector-backend
sudo systemctl status nginx

# Check security group allows port 80
```

---

## 📝 Maintenance

**Weekly:**
- Check disk space: `df -h`
- Review logs: `./monitor.sh`

**Monthly:**
- Update system: `sudo apt update && sudo apt upgrade`
- Check AWS Free Tier usage in console

**As needed:**
- Update app: `./update.sh`

---

## 🎉 Success Checklist

- [ ] EC2 instance launched
- [ ] Setup script completed
- [ ] App accessible at http://YOUR-EC2-IP
- [ ] Backend API working
- [ ] Can analyze text successfully
- [ ] Services auto-restart on reboot

---

## 📚 Full Documentation

For detailed information, see:
- `AWS_FREE_TIER_DEPLOYMENT.md` - Complete guide
- `setup-ec2.sh` - Setup script
- `DEPLOYMENT_SUMMARY.md` - All deployment options

---

## 💡 Pro Tips

1. **Elastic IP**: Allocate one (free when attached) so IP doesn't change
2. **Backups**: Create AMI snapshot monthly
3. **Monitoring**: Set up CloudWatch alarms (free tier: 10 alarms)
4. **Domain**: Use Route 53 or free alternatives
5. **SSL**: Always use HTTPS in production

---

**Ready?** Launch your EC2 instance and run the setup script!

**Questions?** Check `AWS_FREE_TIER_DEPLOYMENT.md` for detailed instructions.
