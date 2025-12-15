# Step-by-Step AWS ECS Deployment

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Docker** installed locally
4. **GitHub** repository set up

## Step 1: Set Up AWS Infrastructure

### 1.1 Create ECR Repositories

```bash
# Create repository for backend
aws ecr create-repository \
    --repository-name ai-detector-backend \
    --region us-east-1

# Create repository for frontend
aws ecr create-repository \
    --repository-name ai-detector-frontend \
    --region us-east-1
```

### 1.2 Create ECS Cluster

```bash
aws ecs create-cluster \
    --cluster-name ai-detector-cluster \
    --region us-east-1
```

### 1.3 Create S3 Bucket for Models

```bash
# Create bucket
aws s3 mb s3://ai-detector-models-YOUR-ACCOUNT-ID

# Upload your model files
aws s3 cp Backend/Models/ s3://ai-detector-models-YOUR-ACCOUNT-ID/models/ --recursive
```

## Step 2: Build and Push Docker Images

### 2.1 Login to ECR

```bash
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin YOUR-ACCOUNT-ID.dkr.ecr.us-east-1.amazonaws.com
```

### 2.2 Build and Push Backend

```bash
cd Backend

# Build
docker build -t ai-detector-backend .

# Tag
docker tag ai-detector-backend:latest \
    YOUR-ACCOUNT-ID.dkr.ecr.us-east-1.amazonaws.com/ai-detector-backend:latest

# Push
docker push YOUR-ACCOUNT-ID.dkr.ecr.us-east-1.amazonaws.com/ai-detector-backend:latest
```

### 2.3 Build and Push Frontend

```bash
cd ../Frontend

# Build
docker build -t ai-detector-frontend .

# Tag
docker tag ai-detector-frontend:latest \
    YOUR-ACCOUNT-ID.dkr.ecr.us-east-1.amazonaws.com/ai-detector-frontend:latest

# Push
docker push YOUR-ACCOUNT-ID.dkr.ecr.us-east-1.amazonaws.com/ai-detector-frontend:latest
```

## Step 3: Create Task Definition

Create `task-definition.json`:

```json
{
  "family": "ai-detector-task",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "YOUR-ACCOUNT-ID.dkr.ecr.us-east-1.amazonaws.com/ai-detector-backend:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "FLASK_ENV",
          "value": "production"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ai-detector",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "backend"
        }
      }
    },
    {
      "name": "frontend",
      "image": "YOUR-ACCOUNT-ID.dkr.ecr.us-east-1.amazonaws.com/ai-detector-frontend:latest",
      "portMappings": [
        {
          "containerPort": 80,
          "protocol": "tcp"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ai-detector",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "frontend"
        }
      }
    }
  ]
}
```

Register the task definition:

```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

## Step 4: Create Application Load Balancer

### 4.1 Create ALB

```bash
aws elbv2 create-load-balancer \
    --name ai-detector-alb \
    --subnets subnet-xxxxx subnet-yyyyy \
    --security-groups sg-xxxxx \
    --scheme internet-facing \
    --type application
```

### 4.2 Create Target Groups

```bash
# Backend target group
aws elbv2 create-target-group \
    --name ai-detector-backend-tg \
    --protocol HTTP \
    --port 5000 \
    --vpc-id vpc-xxxxx \
    --target-type ip \
    --health-check-path /info

# Frontend target group
aws elbv2 create-target-group \
    --name ai-detector-frontend-tg \
    --protocol HTTP \
    --port 80 \
    --vpc-id vpc-xxxxx \
    --target-type ip \
    --health-check-path /
```

### 4.3 Create Listeners

```bash
# HTTP listener (redirect to HTTPS in production)
aws elbv2 create-listener \
    --load-balancer-arn arn:aws:elasticloadbalancing:... \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...
```

## Step 5: Create ECS Service

```bash
aws ecs create-service \
    --cluster ai-detector-cluster \
    --service-name ai-detector-service \
    --task-definition ai-detector-task \
    --desired-count 2 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx,subnet-yyyyy],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}" \
    --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=frontend,containerPort=80"
```

## Step 6: Set Up Auto Scaling

```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --resource-id service/ai-detector-cluster/ai-detector-service \
    --scalable-dimension ecs:service:DesiredCount \
    --min-capacity 1 \
    --max-capacity 5

# Create scaling policy
aws application-autoscaling put-scaling-policy \
    --service-namespace ecs \
    --resource-id service/ai-detector-cluster/ai-detector-service \
    --scalable-dimension ecs:service:DesiredCount \
    --policy-name cpu-scaling-policy \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration file://scaling-policy.json
```

## Step 7: Configure GitHub Secrets

Add these secrets to your GitHub repository:

1. Go to Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_ACCOUNT_ID`

## Step 8: Deploy via GitHub Actions

1. Push code to `main` branch
2. GitHub Actions will automatically:
   - Run tests
   - Build Docker images
   - Push to ECR
   - Deploy to ECS

## Step 9: Verify Deployment

```bash
# Check service status
aws ecs describe-services \
    --cluster ai-detector-cluster \
    --services ai-detector-service

# Get ALB DNS name
aws elbv2 describe-load-balancers \
    --names ai-detector-alb \
    --query 'LoadBalancers[0].DNSName'
```

## Step 10: Set Up Domain (Optional)

1. Register domain in Route 53
2. Create SSL certificate in ACM
3. Add HTTPS listener to ALB
4. Create Route 53 record pointing to ALB

## Monitoring

### CloudWatch Logs

```bash
# View logs
aws logs tail /ecs/ai-detector --follow
```

### CloudWatch Metrics

- CPU Utilization
- Memory Utilization
- Request Count
- Target Response Time

## Troubleshooting

### Check Task Status
```bash
aws ecs list-tasks --cluster ai-detector-cluster
aws ecs describe-tasks --cluster ai-detector-cluster --tasks TASK-ID
```

### View Logs
```bash
aws logs get-log-events \
    --log-group-name /ecs/ai-detector \
    --log-stream-name backend/backend/TASK-ID
```

## Cost Optimization

1. Use Fargate Spot for non-critical workloads
2. Enable auto-scaling to scale down during low traffic
3. Use S3 lifecycle policies for model versioning
4. Set up CloudWatch alarms for cost monitoring

## Cleanup (if needed)

```bash
# Delete service
aws ecs delete-service --cluster ai-detector-cluster --service ai-detector-service --force

# Delete cluster
aws ecs delete-cluster --cluster ai-detector-cluster

# Delete ECR repositories
aws ecr delete-repository --repository-name ai-detector-backend --force
aws ecr delete-repository --repository-name ai-detector-frontend --force
```

## Next Steps

1. Set up CloudFront for global distribution
2. Implement WAF for security
3. Add RDS for user data (if needed)
4. Set up backup and disaster recovery
5. Implement monitoring and alerting
