# AWS Amplify Deployment Guide - Summoners Reunion AI Chat

This guide provides step-by-step instructions for deploying the Summoners Reunion AI Chat application to AWS using Amplify for the frontend and Lambda for the backend.

## Architecture Overview

- **Frontend**: Static site (HTML/CSS/JS) hosted on AWS Amplify
- **Backend**: Python FastAPI application running on AWS Lambda
- **API**: AWS API Gateway (HTTP API or REST API)
- **AI Service**: AWS Bedrock with Knowledge Base
- **Authentication**: IAM roles (no hardcoded credentials)

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Python 3.9+ installed locally (for testing)
- Git repository (GitHub, GitLab, or Bitbucket)
- AWS Bedrock access enabled in your region
- AWS Bedrock Knowledge Base created (see KNOWLEDGE_BASE_GUIDE.md)

## Part 1: Backend Deployment (AWS Lambda + API Gateway)

### Step 1: Prepare Lambda Deployment Package

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies locally:**
   ```bash
   pip install -r requirements.txt -t ./package
   ```

3. **Copy your application code to the package:**
   ```bash
   cp -r agents config models main.py ./package/
   ```

4. **Create deployment ZIP:**
   ```bash
   cd package
   zip -r ../lambda-deployment.zip .
   cd ..
   ```

### Step 2: Create Lambda Function

1. **Go to AWS Lambda Console:**
   - Navigate to: https://console.aws.amazon.com/lambda

2. **Create a new function:**
   - Click "Create function"
   - Choose "Author from scratch"
   - Function name: `summoners-reunion-api`
   - Runtime: `Python 3.9` (or later)
   - Architecture: `x86_64`
   - Click "Create function"

3. **Upload deployment package:**
   - In the "Code" tab, click "Upload from"
   - Select ".zip file"
   - Upload `lambda-deployment.zip`

4. **Configure function settings:**
   - Handler: `main.handler`
   - Timeout: `30 seconds` (increase to 60s if needed)
   - Memory: `512 MB` (increase if needed for better performance)

### Step 3: Configure Lambda Environment Variables

In the Lambda function "Configuration" > "Environment variables", add:

```
BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
KNOWLEDGE_BASE_ID=<your-knowledge-base-id>
KNOWLEDGE_BASE_ENABLED=true
AWS_REGION=us-east-1
CORS_ORIGINS=https://main.xxxxxx.amplifyapp.com
MAX_TOKENS=4096
TEMPERATURE=0.7
STREAMING_ENABLED=true
DEBUG=false
APP_NAME=Summoners Reunion AI
MAX_CONVERSATION_HISTORY=10
KB_MAX_RESULTS=5
TOP_P=0.9
```

**Note:** Update `CORS_ORIGINS` after deploying the frontend (Step 5).

### Step 4: Configure IAM Role for Lambda

1. **Go to Lambda function "Configuration" > "Permissions"**

2. **Click on the execution role name** (opens IAM console)

3. **Add Bedrock permissions:**
   - Click "Add permissions" > "Attach policies"
   - Click "Create policy"
   - Use JSON editor:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": "arn:aws:bedrock:*::foundation-model/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:Retrieve"
            ],
            "Resource": "arn:aws:bedrock:*:*:knowledge-base/*"
        }
    ]
}
```

   - Name the policy: `BedrockAccessPolicy`
   - Attach the policy to your Lambda execution role

### Step 5: Create API Gateway

1. **Go to API Gateway Console:**
   - Navigate to: https://console.aws.amazon.com/apigateway

2. **Create HTTP API:**
   - Click "Create API"
   - Choose "HTTP API" > "Build"
   - Add integration: "Lambda"
   - Select your Lambda function: `summoners-reunion-api`
   - API name: `summoners-reunion-api-gateway`
   - Click "Next"

3. **Configure routes:**
   - Keep the default route: `ANY /{proxy+}`
   - This will forward all requests to Lambda
   - Click "Next"

4. **Configure CORS:**
   - Click "Configure CORS"
   - Access-Control-Allow-Origin: `*` (or your specific Amplify domain)
   - Access-Control-Allow-Methods: `GET, POST, OPTIONS`
   - Access-Control-Allow-Headers: `Content-Type, Authorization`
   - Click "Next"

5. **Review and create:**
   - Review settings
   - Click "Create"

6. **Note your API URL:**
   - After creation, you'll see the "Invoke URL"
   - Example: `https://abc123def.execute-api.us-east-1.amazonaws.com`
   - **Save this URL** - you'll need it for frontend deployment

### Step 6: Test Backend API

Test your Lambda function using the API Gateway URL:

```bash
# Health check
curl https://YOUR-API-URL/api/health

# Test chat endpoint
curl -X POST https://YOUR-API-URL/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "conversation_history": []
  }'
```

---

## Part 2: Frontend Deployment (AWS Amplify)

### Step 1: Prepare Repository

1. **Ensure all changes are committed:**
   ```bash
   git status
   git add .
   git commit -m "Prepare for AWS Amplify deployment"
   git push origin master
   ```

2. **Verify amplify.yml exists** in the project root (already created)

### Step 2: Create Amplify App

1. **Go to AWS Amplify Console:**
   - Navigate to: https://console.aws.amazon.com/amplify

2. **Create new app:**
   - Click "New app" > "Host web app"
   - Choose your Git provider (GitHub, GitLab, Bitbucket)
   - Authorize AWS Amplify to access your repository
   - Select your repository: `summoners-reunion`
   - Select branch: `master` (or `main`)
   - Click "Next"

3. **Configure build settings:**
   - App name: `summoners-reunion`
   - The build configuration should auto-detect `amplify.yml`
   - If not, paste the contents of `amplify.yml`
   - Click "Advanced settings"

4. **Add environment variable:**
   - Key: `API_BASE_URL`
   - Value: `https://YOUR-API-GATEWAY-URL` (from Step 5 above)
   - Example: `https://abc123def.execute-api.us-east-1.amazonaws.com`
   - Click "Next"

5. **Review and deploy:**
   - Review all settings
   - Click "Save and deploy"

### Step 3: Monitor Deployment

1. **Watch the build process:**
   - Provision (download code)
   - Build (run amplify.yml commands)
   - Deploy (upload to Amplify hosting)

2. **Deployment should complete in 2-5 minutes**

3. **Note your Amplify URL:**
   - After deployment, you'll see the app URL
   - Example: `https://main.d1a2b3c4d5e6f7.amplifyapp.com`

### Step 4: Update CORS Configuration

1. **Update Lambda environment variables:**
   - Go back to Lambda Console
   - Update `CORS_ORIGINS` to your Amplify URL
   - Example: `https://main.d1a2b3c4d5e6f7.amplifyapp.com`

2. **Optionally update API Gateway CORS:**
   - Go to API Gateway Console
   - Select your API
   - Go to "CORS" settings
   - Update "Access-Control-Allow-Origin" to your Amplify URL
   - Click "Save"

### Step 5: Test Deployment

1. **Open your Amplify URL** in a browser

2. **Verify functionality:**
   - Check status indicator shows "Online" (green)
   - Send a test message
   - Verify streaming response works
   - Check browser console for errors

---

## Troubleshooting

### Frontend Issues

**Problem: Status shows "Offline"**
- Check that `API_BASE_URL` environment variable is set correctly in Amplify
- Verify API Gateway URL is accessible
- Check browser console for CORS errors
- Verify Lambda function is running

**Problem: Build fails in Amplify**
- Check build logs in Amplify Console
- Verify `amplify.yml` syntax is correct
- Ensure `API_BASE_URL` environment variable is set

**Problem: CORS errors in browser**
- Update `CORS_ORIGINS` in Lambda environment variables
- Update API Gateway CORS settings
- Ensure CORS middleware in `main.py` includes your Amplify domain

### Backend Issues

**Problem: Lambda timeout errors**
- Increase Lambda timeout to 60 seconds
- Increase Lambda memory to 1024 MB
- Check CloudWatch logs for errors

**Problem: Bedrock access denied**
- Verify IAM role has Bedrock permissions
- Check the Bedrock policy is attached to Lambda execution role
- Verify Bedrock model ID is correct

**Problem: Knowledge Base not working**
- Verify `KNOWLEDGE_BASE_ID` is set correctly
- Check IAM role has `bedrock:Retrieve` permission
- Verify Knowledge Base exists in the same region

**Problem: SSE streaming not working**
- API Gateway has 30-second timeout limit
- Consider using WebSockets for long responses
- Or implement chunked responses with shorter timeouts

### Viewing Logs

**Lambda Logs:**
```bash
# Using AWS CLI
aws logs tail /aws/lambda/summoners-reunion-api --follow
```

**Amplify Build Logs:**
- Available in Amplify Console > App > Build history

**Frontend Errors:**
- Check browser console (F12)
- Check Network tab for failed requests

---

## Cost Considerations

### Estimated Monthly Costs (Low Traffic)

- **AWS Amplify Hosting**: $0.01 per GB served + $0.023 per build minute
- **AWS Lambda**: $0.20 per 1M requests + $0.0000166667 per GB-second
- **API Gateway**: $1.00 per million requests (first 300M)
- **AWS Bedrock**: Pay per token (varies by model)
  - Claude 3.5 Sonnet: ~$3 per 1M input tokens, ~$15 per 1M output tokens
- **S3 (Knowledge Base)**: $0.023 per GB/month

**Example**: 1,000 chat messages/month ≈ $2-5 (excluding Bedrock token costs)

### Cost Optimization

1. **Use Lambda reserved concurrency** for predictable traffic
2. **Enable API Gateway caching** to reduce Lambda invocations
3. **Set CloudWatch log retention** to 7 days (instead of indefinite)
4. **Use Bedrock with smaller models** for simpler queries
5. **Implement request throttling** to prevent abuse

---

## Security Best Practices

1. **Never commit credentials:**
   - Use IAM roles for Lambda
   - Never hardcode AWS keys

2. **Enable API Gateway authentication:**
   - Use IAM authorization
   - Or implement JWT/OAuth

3. **Implement rate limiting:**
   - Use API Gateway throttling
   - Or implement custom rate limiting in Lambda

4. **Monitor and alert:**
   - Set up CloudWatch alarms for errors
   - Monitor Lambda invocations
   - Track API Gateway 4xx/5xx errors

5. **Regular updates:**
   - Keep dependencies updated
   - Monitor for security vulnerabilities

---

## Continuous Deployment

### Automatic Deployments

Amplify automatically deploys when you push to your Git repository:

1. **Push code changes:**
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin master
   ```

2. **Amplify automatically:**
   - Detects the push
   - Runs the build
   - Deploys the updated frontend

### Lambda Updates

For Lambda updates:

1. **Update code locally**

2. **Create new deployment package:**
   ```bash
   cd backend
   pip install -r requirements.txt -t ./package
   cp -r agents config models main.py ./package/
   cd package && zip -r ../lambda-deployment.zip . && cd ..
   ```

3. **Upload to Lambda:**
   ```bash
   aws lambda update-function-code \
     --function-name summoners-reunion-api \
     --zip-file fileb://lambda-deployment.zip
   ```

Or use CI/CD tools like GitHub Actions for automated Lambda deployments.

---

## Next Steps

1. **Custom Domain:**
   - Add a custom domain in Amplify Console
   - Configure DNS settings

2. **Authentication:**
   - Implement user authentication
   - Use AWS Cognito or third-party providers

3. **Analytics:**
   - Enable Amplify Analytics
   - Track user interactions

4. **Monitoring:**
   - Set up CloudWatch dashboards
   - Configure alarms for errors

---

## Additional Resources

- [AWS Amplify Documentation](https://docs.aws.amazon.com/amplify/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Mangum Documentation](https://mangum.io/)

## Support

For issues or questions:
- Check AWS CloudWatch logs
- Review Amplify build logs
- Check browser console errors
- Consult AWS documentation

---

**Congratulations!** Your Summoners Reunion AI Chat is now deployed on AWS Amplify! 🎉
