#!/bin/bash

# Script to update Nginx configuration on EC2
# Run this on your EC2 instance after deployment

echo "🔧 Updating Nginx Configuration"
echo "================================"

# Backup existing config
echo "📦 Creating backup..."
sudo cp /etc/nginx/sites-available/ai-detector /etc/nginx/sites-available/ai-detector.backup.$(date +%Y%m%d_%H%M%S)

# Copy new configuration
echo "📝 Updating configuration..."
sudo cp /home/ubuntu/ai_detector/nginx-production.conf /etc/nginx/sites-available/ai-detector

# Test configuration
echo "🧪 Testing Nginx configuration..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Configuration is valid"
    
    # Reload Nginx
    echo "🔄 Reloading Nginx..."
    sudo systemctl reload nginx
    
    echo ""
    echo "✅ Nginx configuration updated successfully!"
    echo ""
    echo "📍 Your app is now configured for:"
    echo "   http://51.21.253.28"
    echo ""
    echo "🔍 Test endpoints:"
    echo "   Frontend:  http://51.21.253.28"
    echo "   API Info:  http://51.21.253.28/info"
    echo "   API Test:  http://51.21.253.28/api/info"
    echo ""
else
    echo "❌ Configuration test failed!"
    echo "Restoring backup..."
    sudo cp /etc/nginx/sites-available/ai-detector.backup.* /etc/nginx/sites-available/ai-detector
    echo "Please check the configuration file for errors."
    exit 1
fi
