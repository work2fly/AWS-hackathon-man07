# Deployment Guide - AI Therapy Platform

🏆 **Breaking Barriers UK 2026 - AWS Hackathon**

## Quick Deployment Checklist

### ⚠️ Critical Reminders
- **Account Termination**: 23:00 on 15th January 2026
- **Region Constraint**: us-west-2 only
- **Save Everything**: Ensure all code is in Git repositories

### 1. Pre-deployment Verification

```bash
# Check build works
npm run build

# Verify TypeScript
npm run type-check

# Test locally
npm run dev
```

### 2. AWS Amplify Deployment (Recommended)

**Option A: Amplify Console**
1. Go to AWS Amplify Console (us-west-2)
2. Connect your Git repository
3. Configure build settings:
   ```yaml
   version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - npm ci
       build:
         commands:
           - npm run build
     artifacts:
       baseDirectory: .next
       files:
         - '**/*'
     cache:
       paths:
         - node_modules/**/*
   ```

**Option B: Amplify CLI**
```bash
# Install Amplify CLI
npm install -g @aws-amplify/cli

# Initialize project
amplify init

# Add hosting
amplify add hosting

# Deploy
amplify publish
```

### 3. S3 + CloudFront Deployment

**Step 1: Build for static export**
```bash
npm run build
```

**Step 2: Create S3 bucket**
```bash
aws s3 mb s3://ai-therapy-frontend-hackathon --region us-west-2
```

**Step 3: Upload files**
```bash
aws s3 sync .next/static s3://ai-therapy-frontend-hackathon/static --region us-west-2
aws s3 sync out s3://ai-therapy-frontend-hackathon --region us-west-2
```

**Step 4: Configure CloudFront**
- Create CloudFront distribution
- Point to S3 bucket
- Configure custom error pages for SPA routing

### 4. Environment Configuration

**Production Environment Variables**
```bash
# Copy example file
cp .env.example .env.production

# Update for production (if needed)
NEXT_PUBLIC_DEBUG_MODE=false
NEXT_PUBLIC_ENABLE_LOGGING=false
```

### 5. Domain Configuration (Optional)

**Custom Domain Setup**
1. **Route 53**: Create hosted zone (if using custom domain)
2. **Certificate Manager**: Request SSL certificate (us-east-1 for CloudFront)
3. **CloudFront**: Configure custom domain and certificate
4. **Route 53**: Create A record pointing to CloudFront

### 6. Monitoring Setup

**CloudWatch Configuration**
```bash
# Create log group
aws logs create-log-group --log-group-name /aws/amplify/ai-therapy-frontend --region us-west-2

# Set up alarms
aws cloudwatch put-metric-alarm \
  --alarm-name "AI-Therapy-Frontend-Errors" \
  --alarm-description "Frontend error rate" \
  --metric-name ErrorRate \
  --namespace AWS/Amplify \
  --statistic Average \
  --period 300 \
  --threshold 5.0 \
  --comparison-operator GreaterThanThreshold \
  --region us-west-2
```

### 7. Security Configuration

**Content Security Policy**
Add to `next.config.js`:
```javascript
const nextConfig = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: "default-src 'self'; connect-src 'self' https://*.amazonaws.com wss://*.amazonaws.com; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          }
        ]
      }
    ];
  }
};
```

### 8. Performance Optimization

**Build Optimization**
```javascript
// next.config.js
const nextConfig = {
  compress: true,
  poweredByHeader: false,
  generateEtags: false,
  
  // Image optimization
  images: {
    domains: ['amazonaws.com'],
    formats: ['image/webp', 'image/avif']
  },
  
  // Bundle analyzer (development only)
  ...(process.env.ANALYZE === 'true' && {
    webpack: (config) => {
      config.plugins.push(new BundleAnalyzerPlugin());
      return config;
    }
  })
};
```

### 9. Testing Deployment

**Deployment Verification Checklist**
- [ ] Application loads successfully
- [ ] Authentication flow works
- [ ] WebSocket connections establish
- [ ] Audio permissions request properly
- [ ] Responsive design on mobile/desktop
- [ ] HTTPS enforced
- [ ] Error pages display correctly
- [ ] Performance metrics acceptable

**Load Testing**
```bash
# Install artillery for load testing
npm install -g artillery

# Create load test config
cat > load-test.yml << EOF
config:
  target: 'https://your-domain.com'
  phases:
    - duration: 60
      arrivalRate: 10
scenarios:
  - name: "Homepage load"
    requests:
      - get:
          url: "/"
EOF

# Run load test
artillery run load-test.yml
```

### 10. Rollback Plan

**Quick Rollback Steps**
1. **Amplify**: Use console to rollback to previous deployment
2. **S3/CloudFront**: 
   ```bash
   # Restore from backup
   aws s3 sync s3://backup-bucket s3://ai-therapy-frontend-hackathon --region us-west-2
   
   # Invalidate CloudFront cache
   aws cloudfront create-invalidation --distribution-id EDFDVBD6EXAMPLE --paths "/*"
   ```

### 11. Post-Deployment

**Monitoring Dashboard**
- Set up CloudWatch dashboard
- Configure error alerting
- Monitor performance metrics
- Track user engagement

**Documentation Update**
- Update README with production URLs
- Document any configuration changes
- Create user guide for judges/demo

### 12. Demo Preparation

**Demo Environment Setup**
```bash
# Create demo user accounts
aws cognito-idp admin-create-user \
  --user-pool-id us-west-2_ASOPUuOOV \
  --username demo-client \
  --user-attributes Name=email,Value=demo-client@example.com \
  --temporary-password TempPass123! \
  --region us-west-2

# Test all functionality
npm run dev
# Manual testing checklist...
```

**Demo Script**
1. Show landing page and features
2. Demonstrate user registration/login
3. Start therapy session
4. Show real-time audio communication
5. Demonstrate role-based interfaces
6. Highlight security and compliance features

## Troubleshooting

### Common Deployment Issues

**Build Failures**
```bash
# Clear cache and rebuild
rm -rf .next node_modules
npm install
npm run build
```

**WebSocket Connection Issues**
- Verify API Gateway WebSocket endpoint
- Check CORS configuration
- Ensure proper authentication headers

**Audio Not Working**
- Verify HTTPS deployment (required for microphone access)
- Check browser compatibility
- Test audio permissions

### Emergency Contacts
- **London**: Mevlit (mevlit@), Rama (ramaknat@)
- **Manchester**: Basheer Ahmed (basheerz@), Robert Bradley (rbradaws@)
- **Dublin**: Shane Adams (shaadas@), Sherin Chandy (chandys@), Eduarda Siqueira (edds@)

---

**🏆 Breaking Barriers UK 2026 Compliant Deployment**

Remember: Save all work before 23:00 on 15th January 2026!