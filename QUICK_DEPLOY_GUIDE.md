# Quick Deploy Guide - After GitHub Connection

This guide covers the exact steps to follow AFTER you've pushed to GitHub and connected to AWS Amplify.

## 🎯 Overview

You'll deploy in this order:
1. **Backend First** (Lambda + API Gateway) - Get the API URL
2. **Frontend Second** (Amplify) - Use the API URL from step 1

---

## Part 1: Deploy Backend (Lambda + API Gateway)

### Step 1: Create Lambda Deployment Package

On your local machine:

```bash
# Navigate to project directory
cd /home/lavender_goombs/new-project/summoners-reunion

# Run the deployment script
./deploy-lambda.sh
```

This creates: `backend/lambda-deployment.zip` (about 20-50 MB)

---

### Step 2: Create Lambda Function in AWS

1. **Go to AWS Lambda Console:**
   - Open: https://console.aws.amazon.com/lambda
   - Click **"Create function"**

2. **Configure function:**
   - Choose: **"Author from scratch"**
   - Function name: `summoners-reunion-api`
   - Runtime: **Python 3.9**
   - Architecture: **x86_64**
   - Click **"Create function"**

3. **Upload your code:**
   - In the **Code** tab, click **"Upload from"** → **".zip file"**
   - Select `backend/lambda-deployment.zip` from your computer
   - Click **"Save"**
   - Wait for upload to complete

4. **Configure Runtime settings:**
   - Click **"Edit"** in Runtime settings
   - Handler: `main.handler`
   - Click **"Save"**

5. **Configure Timeout and Memory:**
   - Go to **Configuration** → **General configuration** → **Edit**
   - Timeout: `60 seconds`
   - Memory: `512 MB`
   - Click **"Save"**

---

### Step 3: Set Environment Variables

1. **Go to Configuration → Environment variables → Edit**

2. **Click "Add environment variable"** and add each of these:

```
BEDROCK_MODEL_ID = anthropic.claude-3-5-sonnet-20241022-v2:0
AWS_REGION = us-east-1
KNOWLEDGE_BASE_ID = YOUR_KB_ID_HERE
KNOWLEDGE_BASE_ENABLED = true
KB_MAX_RESULTS = 5
APP_NAME = Summoners Reunion AI
DEBUG = false
MAX_CONVERSATION_HISTORY = 10
CORS_ORIGINS = *
STREAMING_ENABLED = true
MAX_TOKENS = 4096
TEMPERATURE = 0.7
TOP_P = 0.9
```

**Important Notes:**
- Replace `YOUR_KB_ID_HERE` with your actual Bedrock Knowledge Base ID
- Set `CORS_ORIGINS = *` for now (we'll update it later with your Amplify URL)
- Click **"Save"** when done

---

### Step 4: Configure IAM Permissions for Bedrock

1. **Go to Configuration → Permissions**

2. **Click on the Role name** (opens IAM console in new tab)

3. **Add Bedrock permissions:**
   - Click **"Add permissions"** → **"Create inline policy"**
   - Click **JSON** tab
   - Paste this policy:

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

4. **Click "Review policy"**
   - Name: `BedrockAccessPolicy`
   - Click **"Create policy"**

---

### Step 5: Create API Gateway

1. **Go to API Gateway Console:**
   - Open: https://console.aws.amazon.com/apigateway
   - Click **"Create API"**

2. **Choose HTTP API:**
   - Find **"HTTP API"** (not REST API)
   - Click **"Build"**

3. **Add integration:**
   - Click **"Add integration"**
   - Select **"Lambda"**
   - Choose your region (e.g., us-east-1)
   - Lambda function: Select `summoners-reunion-api`
   - API name: `summoners-reunion-api`
   - Click **"Next"**

4. **Configure routes:**
   - Keep the default: `ANY /{proxy+}`
   - Click **"Next"**

5. **Configure stages:**
   - Stage name: `$default` (auto-filled)
   - Auto-deploy: **Enabled**
   - Click **"Next"**

6. **Review and create:**
   - Review settings
   - Click **"Create"**

7. **🎯 SAVE YOUR API URL:**
   - After creation, you'll see **"Invoke URL"**
   - Example: `https://abc123xyz.execute-api.us-east-1.amazonaws.com`
   - **COPY THIS URL** - you need it for the next part!

---

### Step 6: Test Your Backend

Open terminal and test:

```bash
# Replace with YOUR API URL
export API_URL="https://YOUR-API-URL-HERE.execute-api.us-east-1.amazonaws.com"

# Test health endpoint
curl $API_URL/api/health

# Expected response:
# {"status":"healthy","app_name":"Summoners Reunion AI","timestamp":"...","bedrock_configured":true}
```

If you see `"status":"healthy"` and `"bedrock_configured":true`, you're good! ✅

If you see errors, check CloudWatch Logs:
- Lambda Console → Monitor → View logs in CloudWatch

---

## Part 2: Deploy Frontend (AWS Amplify)

### Step 7: Push Code to GitHub

If you haven't already:

```bash
# Check git status
git status

# Add all changes
git add .

# Commit
git commit -m "Configure for AWS Amplify deployment"

# Push to GitHub
git push origin master
```

---

### Step 8: Create Amplify App

1. **Go to AWS Amplify Console:**
   - Open: https://console.aws.amazon.com/amplify
   - Click **"New app"** → **"Host web app"**

2. **Connect repository:**
   - Choose **"GitHub"** (or your Git provider)
   - Click **"Connect branch"**
   - Authorize AWS Amplify (if first time)
   - Select repository: **summoners-reunion**
   - Select branch: **master** (or **main**)
   - Click **"Next"**

3. **Configure build settings:**
   - App name: `summoners-reunion`
   - Build and test settings should show your `amplify.yml`
   - If not, it will be auto-detected
   - Click **"Advanced settings"** to expand

4. **🎯 ADD ENVIRONMENT VARIABLE:**
   - Click **"Add environment variable"**
   - Key: `API_BASE_URL`
   - Value: `https://YOUR-API-URL.execute-api.us-east-1.amazonaws.com`
   - (Use the API URL from Step 5!)
   - Click **"Next"**

5. **Review:**
   - Review all settings
   - Click **"Save and deploy"**

---

### Step 9: Wait for Build

The build process takes 2-5 minutes:

1. **Provision** - Downloads your code from GitHub
2. **Build** - Runs commands from amplify.yml
3. **Deploy** - Uploads to Amplify hosting
4. **Verify** - Final checks

Watch the progress in the Amplify Console.

---

### Step 10: Get Your Amplify URL

After deployment completes:

1. **You'll see your app URL:**
   - Example: `https://master.d1a2b3c4d5e6.amplifyapp.com`
   - Click it to open your app!

2. **🎯 COPY THIS URL** - you need it for the next step

---

### Step 11: Update CORS Settings

Now that you have your Amplify URL, update Lambda CORS:

1. **Go back to Lambda Console**
   - Open your `summoners-reunion-api` function

2. **Go to Configuration → Environment variables → Edit**

3. **Find `CORS_ORIGINS`:**
   - Change from: `*`
   - To: `https://master.d1a2b3c4d5e6.amplifyapp.com` (your Amplify URL)
   - Click **"Save"**

This ensures only your frontend can call your API.

---

## Part 3: Test Your Deployed Application

### Step 12: Test the Live App

1. **Open your Amplify URL** in a browser

2. **Check the status indicator:**
   - Top right should show **"Online"** with a green dot
   - If it shows "Offline", see troubleshooting below

3. **Send a test message:**
   - Type: "Hello, how are you?"
   - Click Send
   - You should see:
     - Your message appears
     - Typing indicator shows
     - AI response streams in character by character

4. **Test suggestions:**
   - Click the lightbulb icon (bottom right)
   - Click a suggestion
   - Verify it sends successfully

5. **Check browser console:**
   - Press F12 → Console tab
   - Should see no errors
   - If you see CORS errors, double-check Step 11

---

## 🎉 You're Done!

If all tests pass, your application is fully deployed and working!

**Your URLs:**
- Frontend: `https://master.xxxxx.amplifyapp.com`
- Backend API: `https://xxxxx.execute-api.region.amazonaws.com`

---

## 🔧 Troubleshooting

### Problem: Status shows "Offline"

**Check 1: API URL is correct**
```bash
# In Amplify Console → App settings → Environment variables
# Verify API_BASE_URL is set correctly
```

**Check 2: Lambda is working**
```bash
# Test Lambda directly
curl https://YOUR-API-URL/api/health
```

**Check 3: CORS is configured**
```bash
# In Lambda → Environment variables
# Verify CORS_ORIGINS includes your Amplify URL
```

**Check 4: Browser console**
- Open F12 → Console
- Look for errors
- Common: CORS errors or 403 Forbidden

---

### Problem: "Error streaming response"

**Check 1: Lambda timeout**
- Lambda → Configuration → General configuration
- Timeout should be 60 seconds

**Check 2: Bedrock permissions**
- Lambda → Configuration → Permissions → Role
- Verify BedrockAccessPolicy is attached

**Check 3: CloudWatch Logs**
```bash
# In Lambda Console → Monitor → View logs in CloudWatch
# Look for error messages
```

---

### Problem: Build fails in Amplify

**Check 1: Environment variable**
- Amplify → App settings → Environment variables
- Verify API_BASE_URL is set

**Check 2: Build logs**
- Amplify → Build history → Latest build
- Click on failed phase
- Read error message

**Common fix:**
- Redeploy: Amplify → Redeploy this version

---

### Problem: CORS errors in browser

```
Access to fetch at '...' from origin '...' has been blocked by CORS policy
```

**Fix:**
1. Go to Lambda → Environment variables
2. Update `CORS_ORIGINS` to your exact Amplify URL
3. Include the full URL: `https://master.d123.amplifyapp.com` (no trailing slash)
4. Save and wait 30 seconds for Lambda to update

---

## 🔄 Making Changes After Deployment

### Update Frontend:
```bash
# Make changes to frontend files
git add .
git commit -m "Update frontend"
git push origin master

# Amplify automatically rebuilds and deploys!
```

### Update Backend:
```bash
# Make changes to backend files
./deploy-lambda.sh

# Then in AWS Console:
# Lambda → Upload from → .zip file → Select lambda-deployment.zip
```

---

## 📊 Monitoring

### View Logs:
- **Frontend errors:** Browser console (F12)
- **Backend errors:** Lambda → Monitor → View logs in CloudWatch
- **Build logs:** Amplify → Build history

### Check Costs:
- AWS Console → Billing Dashboard
- Set up billing alerts in Billing → Budgets

---

## 🆘 Need Help?

1. **Check CloudWatch Logs** for Lambda errors
2. **Check Amplify Build Logs** for frontend errors
3. **Check Browser Console** for JavaScript errors
4. Review **AWS_AMPLIFY_DEPLOYMENT.md** for detailed info

---

## ✅ Success Checklist

- [ ] Lambda function deployed and returns healthy status
- [ ] API Gateway created and URL saved
- [ ] Amplify app deployed successfully
- [ ] Frontend shows "Online" status
- [ ] Can send messages and receive AI responses
- [ ] Streaming works (text appears progressively)
- [ ] No errors in browser console
- [ ] No errors in CloudWatch logs

**All checked?** Congratulations! 🎉 Your app is live!
