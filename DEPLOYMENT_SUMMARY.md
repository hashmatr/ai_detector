# 🚀 AWS Deployment & CI/CD Pipeline - Complete Setup

## ✅ What Has Been Created

### 1. **Docker Configuration**
- ✅ `Backend/Dockerfile` - Production-ready Flask container
- ✅ `Frontend/Dockerfile` - Multi-stage React build with Nginx
- ✅ `docker-compose.yml` - Local testing environment
- ✅ `.dockerignore` files - Optimized build context

### 2. **CI/CD Pipeline**
- ✅ `.github/workflows/deploy.yml` - Automated GitHub Actions pipeline
  - Runs tests on push
  - Builds Docker images
  - Pushes to AWS ECR
  - Deploys to ECS automatically

### 3. **Deployment Guides**
- ✅ `AWS_DEPLOYMENT_GUIDE.md` - Architecture overview & options
- ✅ `AWS_ECS_DEPLOYMENT.md` - Step-by-step ECS deployment
- ✅ `DOCKER_QUICKSTART.md` - Local Docker testing
- ✅ `deploy.sh` - Automated deployment script

### 4. **Configuration Files**
- ✅ `Frontend/nginx.conf` - Nginx configuration with caching & security
- ✅ `Backend/requirements.txt` - Python dependencies

---

## 🎯 Deployment Options

### **Option 1: Quick Local Testing (Start Here)**
```bash
# Test everything locally first
docker-compose up --build

# Access at:
# Frontend: http://localhost
# Backend: http://localhost:5000
```

### **Option 2: AWS ECS Deployment (Recommended for Production)**

#### Prerequisites:
1. AWS Account
2. AWS CLI configured (`aws configure`)
3. Docker installed

#### Quick Deploy:
```bash
# Make script executable (Linux/Mac)
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

#### Manual Deploy:
Follow step-by-step guide in `AWS_ECS_DEPLOYMENT.md`

### **Option 3: Automated CI/CD (Best for Teams)**

1. **Set up GitHub Secrets:**
   - Go to: Repository → Settings → Secrets and variables → Actions
   - Add:
     - `AWS_ACCESS_KEY_ID`
     - `AWS_SECRET_ACCESS_KEY`

2. **Push to main branch:**
   ```bash
   git push origin main
   ```

3. **GitHub Actions will automatically:**
   - ✅ Run tests
   - ✅ Build Docker images
   - ✅ Push to AWS ECR
   - ✅ Deploy to ECS
   - ✅ Update running services

---

## 📊 Architecture

```
Internet
   ↓
CloudFront (CDN) ← Optional, for global distribution
   ↓
Application Load Balancer
   ↓
┌─────────────────┬─────────────────┐
│   Frontend      │    Backend      │
│   (Nginx)       │    (Flask)      │
│   Port 80       │    Port 5000    │
│   ECS Fargate   │    ECS Fargate  │
└─────────────────┴─────────────────┘
                      ↓
                  S3 Bucket
                  (Model Files)
```

---

## 💰 Cost Estimate

### Development/Testing:
- **ECS Fargate**: ~$30-50/month (1-2 tasks)
- **ALB**: ~$20/month
- **S3**: ~$5/month
- **ECR**: ~$5/month
- **Total**: ~$60-80/month

### Production (with auto-scaling):
- **ECS Fargate**: ~$100-200/month (2-5 tasks)
- **ALB**: ~$20/month
- **CloudFront**: ~$20/month
- **S3**: ~$10/month
- **Total**: ~$150-250/month

### Free Tier (First 12 months):
- Some services included in AWS Free Tier
- Estimated: ~$30-50/month

---

## 🔧 Configuration Steps

### 1. **Local Testing (Required First Step)**
```bash
# Clone repository
git clone https://github.com/hashmatr/ai_detector.git
cd ai_detector

# Test with Docker
docker-compose up --build

# Verify:
# - Frontend loads at http://localhost
# - Backend responds at http://localhost:5000/info
# - Can analyze text successfully
```

### 2. **AWS Account Setup**
```bash
# Install AWS CLI
# Windows: Download from aws.amazon.com/cli
# Mac: brew install awscli
# Linux: sudo apt install awscli

# Configure AWS
aws configure
# Enter: Access Key, Secret Key, Region (us-east-1), Output (json)
```

### 3. **Deploy to AWS**

#### Option A: Automated Script
```bash
./deploy.sh
```

#### Option B: Manual Steps
See `AWS_ECS_DEPLOYMENT.md` for detailed instructions

### 4. **Set Up CI/CD**
```bash
# 1. Get AWS credentials
aws iam create-access-key --user-name github-actions

# 2. Add to GitHub Secrets (see above)

# 3. Push to trigger deployment
git push origin main
```

---

## 📝 Important Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Local development environment |
| `Backend/Dockerfile` | Backend container configuration |
| `Frontend/Dockerfile` | Frontend container configuration |
| `deploy.sh` | Automated deployment script |
| `.github/workflows/deploy.yml` | CI/CD pipeline |
| `AWS_ECS_DEPLOYMENT.md` | Detailed deployment guide |

---

## 🔍 Monitoring & Debugging

### View Logs
```bash
# Docker (local)
docker-compose logs -f

# AWS ECS
aws logs tail /ecs/ai-detector --follow
```

### Check Service Status
```bash
# ECS Service
aws ecs describe-services \
  --cluster ai-detector-cluster \
  --services ai-detector-service

# Task Status
aws ecs list-tasks --cluster ai-detector-cluster
```

### Access Application
```bash
# Get Load Balancer URL
aws elbv2 describe-load-balancers \
  --names ai-detector-alb \
  --query 'LoadBalancers[0].DNSName' \
  --output text
```

---

## 🛡️ Security Best Practices

1. **Environment Variables**: Use AWS Secrets Manager for sensitive data
2. **HTTPS**: Set up SSL/TLS certificate in ACM
3. **IAM Roles**: Use least privilege principle
4. **Security Groups**: Restrict access to necessary ports only
5. **WAF**: Consider AWS WAF for DDoS protection

---

## 🚨 Troubleshooting

### Docker Build Fails
```bash
# Check Docker is running
docker ps

# Clean and rebuild
docker-compose down -v
docker-compose up --build
```

### AWS Deployment Fails
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify ECR login
aws ecr get-login-password --region us-east-1

# Check ECS task logs
aws logs tail /ecs/ai-detector --follow
```

### GitHub Actions Fails
- Check GitHub Secrets are set correctly
- Verify AWS credentials have necessary permissions
- Review workflow logs in GitHub Actions tab

---

## 📚 Next Steps

### After Successful Deployment:

1. **Set Up Custom Domain**
   - Register domain in Route 53
   - Create SSL certificate in ACM
   - Point domain to ALB

2. **Enable Monitoring**
   - Set up CloudWatch dashboards
   - Configure alarms for errors
   - Enable X-Ray tracing

3. **Optimize Performance**
   - Enable CloudFront CDN
   - Configure auto-scaling policies
   - Implement caching strategies

4. **Implement Backups**
   - S3 versioning for models
   - Database backups (if added)
   - Disaster recovery plan

5. **Security Hardening**
   - Enable AWS WAF
   - Set up VPC endpoints
   - Implement API rate limiting

---

## 🎓 Learning Resources

- **AWS ECS**: https://docs.aws.amazon.com/ecs/
- **Docker**: https://docs.docker.com/
- **GitHub Actions**: https://docs.github.com/actions
- **Flask Deployment**: https://flask.palletsprojects.com/deployment/

---

## ✅ Deployment Checklist

- [ ] Tested locally with `docker-compose up`
- [ ] AWS CLI installed and configured
- [ ] AWS account has necessary permissions
- [ ] GitHub Secrets configured (for CI/CD)
- [ ] Reviewed cost estimates
- [ ] Chosen deployment option
- [ ] Followed deployment guide
- [ ] Verified application is accessible
- [ ] Set up monitoring and alerts
- [ ] Configured custom domain (optional)
- [ ] Implemented security best practices

---

## 🎉 Success Criteria

Your deployment is successful when:
- ✅ Frontend loads without errors
- ✅ Backend API responds to requests
- ✅ Can analyze text and files
- ✅ Auto-scaling works correctly
- ✅ Logs are accessible
- ✅ Health checks pass
- ✅ CI/CD pipeline runs automatically

---

**Need Help?** 
- Check the detailed guides in the repository
- Review AWS CloudWatch logs
- Verify all configuration files are correct

**Ready to Deploy?** Start with local testing, then choose your deployment option!
