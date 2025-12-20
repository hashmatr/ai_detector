# AWS Deployment Guide - AI Content Detector

## Architecture Overview

### Recommended AWS Architecture:
```
┌─────────────────────────────────────────────────────────────┐
│                        CloudFront (CDN)                      │
│                    SSL/TLS + Global Distribution             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    S3 Bucket (Frontend)                      │
│                  Static React App Hosting                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│              Application Load Balancer (ALB)                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│           ECS Fargate / EC2 (Backend Flask API)              │
│              Auto-scaling + Health Checks                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    S3 Bucket (Models)                        │
│              Store .joblib model files                       │
└─────────────────────────────────────────────────────────────┘
```

## Deployment Options

### Option 1: AWS Elastic Beanstalk (EASIEST - Recommended for Beginners)
- ✅ Automatic scaling
- ✅ Load balancing
- ✅ Easy deployment
- ✅ Managed infrastructure

### Option 2: AWS ECS with Fargate (RECOMMENDED - Production)
- ✅ Containerized deployment
- ✅ Better control
- ✅ Cost-effective
- ✅ Serverless containers

### Option 3: AWS EC2 (Manual Control)
- ✅ Full control
- ✅ Custom configuration
- ❌ More maintenance

## Cost Estimate (Monthly)

### Small Scale (Development/Testing):
- **EC2 t3.medium**: ~$30/month
- **S3 Storage**: ~$5/month
- **CloudFront**: ~$10/month
- **Total**: ~$45-60/month

### Medium Scale (Production):
- **ECS Fargate**: ~$50-100/month
- **ALB**: ~$20/month
- **S3 + CloudFront**: ~$20/month
- **Total**: ~$90-140/month

## Prerequisites

1. **AWS Account** (Free tier available)
2. **AWS CLI** installed
3. **Docker** installed (for containerization)
4. **GitHub Account** (for CI/CD)

## Quick Start - Option 1: Elastic Beanstalk

### Step 1: Install EB CLI
```bash
pip install awsebcli
```

### Step 2: Initialize Elastic Beanstalk
```bash
cd Backend
eb init -p python-3.11 ai-detector-api --region us-east-1
```

### Step 3: Create Environment
```bash
eb create ai-detector-env
```

### Step 4: Deploy
```bash
eb deploy
```

## Quick Start - Option 2: ECS Fargate (Recommended)

See detailed instructions in:
- `AWS_ECS_DEPLOYMENT.md`
- `DOCKER_SETUP.md`
- `CI_CD_PIPELINE.md`

## Frontend Deployment (S3 + CloudFront)

### Step 1: Build Frontend
```bash
cd Frontend
npm run build
```

### Step 2: Create S3 Bucket
```bash
aws s3 mb s3://ai-detector-frontend
```

### Step 3: Upload Build
```bash
aws s3 sync dist/ s3://ai-detector-frontend --acl public-read
```

### Step 4: Enable Static Website Hosting
```bash
aws s3 website s3://ai-detector-frontend --index-document index.html
```

### Step 5: Create CloudFront Distribution
- Use AWS Console or CloudFormation template

## Environment Variables

Create `.env` file in Backend:
```env
FLASK_ENV=production
MODEL_PATH=/app/models
AWS_REGION=us-east-1
S3_MODEL_BUCKET=ai-detector-models
```

## Security Considerations

1. **API Keys**: Use AWS Secrets Manager
2. **CORS**: Configure properly for your domain
3. **SSL/TLS**: Use AWS Certificate Manager
4. **IAM Roles**: Least privilege principle
5. **Security Groups**: Restrict access

## Model Storage Strategy

### Option 1: S3 (Recommended)
- Store models in S3
- Download on container startup
- Use S3 versioning

### Option 2: EFS (Elastic File System)
- Mount shared file system
- Better for frequent model updates

### Option 3: Container Image
- Include models in Docker image
- Faster startup
- Larger image size

## Monitoring & Logging

1. **CloudWatch Logs**: Application logs
2. **CloudWatch Metrics**: Performance metrics
3. **X-Ray**: Distributed tracing
4. **CloudWatch Alarms**: Alert on errors

## Auto-Scaling Configuration

```yaml
AutoScaling:
  MinSize: 1
  MaxSize: 5
  TargetCPU: 70%
  TargetMemory: 80%
```

## Next Steps

1. Choose deployment option
2. Set up Docker containers
3. Configure CI/CD pipeline
4. Deploy to AWS
5. Set up monitoring

## Detailed Guides

See the following files for step-by-step instructions:
- `AWS_ECS_DEPLOYMENT.md` - ECS Fargate deployment
- `DOCKER_SETUP.md` - Docker configuration
- `CI_CD_PIPELINE.md` - GitHub Actions pipeline
- `CLOUDFORMATION_TEMPLATE.yaml` - Infrastructure as Code
