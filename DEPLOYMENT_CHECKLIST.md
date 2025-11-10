# AWS Amplify Deployment Checklist

Use this checklist to ensure you've completed all necessary steps for deployment.

## Pre-Deployment

- [ ] AWS Account created and configured
- [ ] AWS CLI installed and configured
- [ ] AWS Bedrock access enabled in your region
- [ ] AWS Bedrock Knowledge Base created (see `KNOWLEDGE_BASE_GUIDE.md`)
- [ ] Git repository pushed to GitHub/GitLab/Bitbucket
- [ ] All code changes committed and pushed

## Backend Deployment (Lambda + API Gateway)

### Lambda Function Setup
- [ ] Created Lambda deployment package (backend/lambda-deployment.zip)
- [ ] Created Lambda function: `summoners-reunion-api`
- [ ] Runtime set to Python 3.9+
- [ ] Handler set to `main.handler`
- [ ] Timeout set to 30-60 seconds
- [ ] Memory set to 512 MB or higher
- [ ] Uploaded deployment package

### Environment Variables
- [ ] `BEDROCK_MODEL_ID` set (e.g., anthropic.claude-3-5-sonnet-20241022-v2:0)
- [ ] `KNOWLEDGE_BASE_ID` set to your KB ID
- [ ] `KNOWLEDGE_BASE_ENABLED` set to `true`
- [ ] `AWS_REGION` set (e.g., us-east-1)
- [ ] `CORS_ORIGINS` set (update after frontend deployment)
- [ ] `MAX_TOKENS` set (e.g., 4096)
- [ ] `TEMPERATURE` set (e.g., 0.7)
- [ ] `STREAMING_ENABLED` set to `true`
- [ ] `DEBUG` set to `false`
- [ ] `APP_NAME` set
- [ ] Other optional variables configured

### IAM Permissions
- [ ] Lambda execution role created
- [ ] Bedrock policy created with permissions:
  - `bedrock:InvokeModel`
  - `bedrock:InvokeModelWithResponseStream`
  - `bedrock:Retrieve`
- [ ] Bedrock policy attached to Lambda execution role
- [ ] CloudWatch Logs permissions verified

### API Gateway
- [ ] HTTP API created
- [ ] Lambda integration configured
- [ ] Route configured: `ANY /{proxy+}`
- [ ] CORS configured:
  - Access-Control-Allow-Origin: `*` (or specific domain)
  - Access-Control-Allow-Methods: `GET, POST, OPTIONS`
  - Access-Control-Allow-Headers: `Content-Type, Authorization`
- [ ] API deployed to stage
- [ ] API Gateway URL saved (needed for frontend)

### Backend Testing
- [ ] Health check tested: `GET /api/health`
- [ ] Chat endpoint tested: `POST /api/chat`
- [ ] Streaming endpoint tested: `POST /api/chat/stream`
- [ ] Knowledge base retrieval tested (if enabled)
- [ ] CloudWatch logs reviewed for errors

## Frontend Deployment (Amplify)

### Repository Setup
- [ ] All changes committed to Git
- [ ] Code pushed to remote repository
- [ ] `amplify.yml` exists in project root
- [ ] `frontend/config.js` exists (will be overwritten during build)

### Amplify App Creation
- [ ] Amplify app created in AWS Console
- [ ] Git repository connected
- [ ] Branch selected (master/main)
- [ ] Build settings configured (amplify.yml auto-detected)
- [ ] Environment variable `API_BASE_URL` set to API Gateway URL
- [ ] Build started

### Deployment Verification
- [ ] Build completed successfully
- [ ] Amplify URL noted (e.g., https://main.xxxxxx.amplifyapp.com)
- [ ] Site accessible in browser
- [ ] No console errors in browser

### CORS Update
- [ ] Lambda `CORS_ORIGINS` updated with Amplify URL
- [ ] API Gateway CORS updated (optional)
- [ ] Lambda function redeployed (if environment variables changed)

### Frontend Testing
- [ ] Status indicator shows "Online" (green dot)
- [ ] Test message sent successfully
- [ ] AI response received and displays correctly
- [ ] Streaming works (text appears progressively)
- [ ] Clear chat button works
- [ ] Suggestions panel works
- [ ] No CORS errors in browser console
- [ ] No JavaScript errors in browser console

## Post-Deployment

### Monitoring Setup
- [ ] CloudWatch logs enabled for Lambda
- [ ] CloudWatch alarms configured for errors
- [ ] Amplify build notifications configured
- [ ] Cost alerts configured in AWS Billing

### Documentation
- [ ] API Gateway URL documented
- [ ] Amplify URL documented
- [ ] Environment variables documented
- [ ] Deployment process documented for team

### Security
- [ ] No AWS credentials in code
- [ ] IAM roles used instead of hardcoded keys
- [ ] API Gateway throttling configured (optional)
- [ ] Request validation enabled (optional)
- [ ] Rate limiting implemented (optional)

### Optional Enhancements
- [ ] Custom domain configured in Amplify
- [ ] SSL certificate configured
- [ ] Authentication implemented (Cognito/OAuth)
- [ ] Analytics enabled
- [ ] Performance monitoring enabled
- [ ] Backup strategy implemented

## Continuous Deployment

### Automatic Deployments
- [ ] Amplify auto-deploy configured for Git pushes
- [ ] Branch deploy strategy configured
- [ ] Build notifications configured
- [ ] Rollback procedure documented

### Lambda Updates
- [ ] CI/CD pipeline configured for Lambda (optional)
- [ ] Deployment script created
- [ ] Version control strategy documented

## Troubleshooting

If issues occur, check:

- [ ] CloudWatch Logs for Lambda errors
- [ ] Amplify build logs for frontend issues
- [ ] Browser console for JavaScript errors
- [ ] Network tab for failed API requests
- [ ] CORS configuration in both Lambda and API Gateway
- [ ] Environment variables are set correctly
- [ ] API Gateway URL is correct in Amplify
- [ ] IAM permissions are correct

## Success Criteria

Your deployment is successful when:

- ✅ Frontend loads without errors
- ✅ Status shows "Online"
- ✅ Messages can be sent and received
- ✅ AI responses stream correctly
- ✅ Knowledge Base integration works (if enabled)
- ✅ No errors in CloudWatch Logs
- ✅ No errors in browser console
- ✅ Response time is acceptable (< 5s for first token)

---

**Deployment Date:** _________________

**Deployed By:** _________________

**API Gateway URL:** _________________

**Amplify URL:** _________________

**Notes:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
