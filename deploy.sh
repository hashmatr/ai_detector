#!/bin/bash

# AI Content Detector - Quick AWS Deployment Script
# This script automates the deployment process

set -e

echo "🚀 AI Content Detector - AWS Deployment Script"
echo "================================================"

# Configuration
AWS_REGION="us-east-1"
CLUSTER_NAME="ai-detector-cluster"
SERVICE_NAME="ai-detector-service"
BACKEND_REPO="ai-detector-backend"
FRONTEND_REPO="ai-detector-frontend"

# Get AWS Account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "✅ AWS Account ID: $AWS_ACCOUNT_ID"

# Step 1: Create ECR Repositories
echo ""
echo "📦 Step 1: Creating ECR Repositories..."
aws ecr create-repository --repository-name $BACKEND_REPO --region $AWS_REGION 2>/dev/null || echo "Backend repo already exists"
aws ecr create-repository --repository-name $FRONTEND_REPO --region $AWS_REGION 2>/dev/null || echo "Frontend repo already exists"

# Step 2: Login to ECR
echo ""
echo "🔐 Step 2: Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Step 3: Build and Push Backend
echo ""
echo "🏗️  Step 3: Building and pushing Backend..."
cd Backend
docker build -t $BACKEND_REPO .
docker tag $BACKEND_REPO:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$BACKEND_REPO:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$BACKEND_REPO:latest
cd ..

# Step 4: Build and Push Frontend
echo ""
echo "🏗️  Step 4: Building and pushing Frontend..."
cd Frontend
docker build -t $FRONTEND_REPO .
docker tag $FRONTEND_REPO:latest $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$FRONTEND_REPO:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$FRONTEND_REPO:latest
cd ..

# Step 5: Create ECS Cluster (if not exists)
echo ""
echo "🏢 Step 5: Creating ECS Cluster..."
aws ecs create-cluster --cluster-name $CLUSTER_NAME --region $AWS_REGION 2>/dev/null || echo "Cluster already exists"

# Step 6: Update/Create Service
echo ""
echo "🔄 Step 6: Updating ECS Service..."
aws ecs update-service --cluster $CLUSTER_NAME --service $SERVICE_NAME --force-new-deployment --region $AWS_REGION 2>/dev/null || echo "Service needs to be created manually (first time)"

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "📝 Next Steps:"
echo "1. Check ECS Console: https://console.aws.amazon.com/ecs"
echo "2. Verify service is running"
echo "3. Get ALB DNS name for access"
echo ""
echo "🔍 Useful Commands:"
echo "  - Check service: aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME"
echo "  - View logs: aws logs tail /ecs/ai-detector --follow"
echo ""
