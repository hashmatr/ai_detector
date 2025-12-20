# 🚀 Quick Reference - AWS Deployment

## 📋 Prerequisites Checklist
- [ ] AWS Account created
- [ ] AWS CLI installed (`aws --version`)
- [ ] Docker installed (`docker --version`)
- [ ] Git repository cloned

## ⚡ Quick Start (3 Options)

### Option 1: Local Testing (Start Here!)
```bash
docker-compose up --build
# Access: http://localhost
```

### Option 2: One-Command Deploy
```bash
chmod +x deploy.sh
./deploy.sh
```

### Option 3: Automated CI/CD
```bash
# 1. Add GitHub Secrets: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
# 2. Push to main
git push origin main
```

## 🔑 Essential Commands

### AWS Setup
```bash
# Configure AWS
aws configure

# Get Account ID
aws sts get-caller-identity
```

### Docker Commands
```bash
# Build and run locally
docker-compose up --build

# Stop services
docker-compose down

# View logs
docker-compose logs -f
```

### Deployment Commands
```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build & Push Backend
cd Backend
docker build -t ai-detector-backend .
docker tag ai-detector-backend:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-detector-backend:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-detector-backend:latest

# Update ECS Service
aws ecs update-service --cluster ai-detector-cluster --service ai-detector-service --force-new-deployment
```

### Monitoring Commands
```bash
# View logs
aws logs tail /ecs/ai-detector --follow

# Check service status
aws ecs describe-services --cluster ai-detector-cluster --services ai-detector-service

# Get ALB URL
aws elbv2 describe-load-balancers --names ai-detector-alb --query 'LoadBalancers[0].DNSName'
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `DEPLOYMENT_SUMMARY.md` | Complete deployment guide |
| `AWS_ECS_DEPLOYMENT.md` | Step-by-step ECS setup |
| `DOCKER_QUICKSTART.md` | Local Docker testing |
| `deploy.sh` | Automated deployment |
| `docker-compose.yml` | Local environment |

## 💰 Cost Estimate
- **Development**: ~$60-80/month
- **Production**: ~$150-250/month
- **Free Tier**: ~$30-50/month (first 12 months)

## 🆘 Troubleshooting

### Docker Issues
```bash
docker-compose down -v
docker-compose up --build
```

### AWS Issues
```bash
# Check credentials
aws sts get-caller-identity

# View ECS logs
aws logs tail /ecs/ai-detector --follow
```

### GitHub Actions Issues
- Verify GitHub Secrets are set
- Check workflow logs in Actions tab

## 📞 Support Resources
- **Detailed Guides**: See `DEPLOYMENT_SUMMARY.md`
- **AWS Docs**: https://docs.aws.amazon.com/ecs/
- **Docker Docs**: https://docs.docker.com/

## ✅ Success Checklist
- [ ] Local Docker test passed
- [ ] AWS CLI configured
- [ ] Images pushed to ECR
- [ ] ECS service running
- [ ] Application accessible
- [ ] CI/CD pipeline working

---

**Start Here**: Test locally with `docker-compose up --build`
**Then**: Choose deployment option from `DEPLOYMENT_SUMMARY.md`
