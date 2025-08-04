# Deployment Guide for HackRX API on Render - Gemini Version

This guide provides step-by-step instructions for deploying the HackRX API with Google Gemini integration on Render.com with memory optimizations.

## Prerequisites

1. **GitHub Repository**: Your code should be in a GitHub repository
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **Google Gemini API Key**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Step-by-Step Deployment

### 1. Prepare Your Repository

Ensure your repository contains these files:
```
hackrx-api/
├── src/
│   ├── main.py
│   ├── routes/
│   │   └── hackrx.py
│   └── utils/
│       └── memory_manager.py
├── requirements.txt
├── render.yaml
├── Procfile
├── runtime.txt
└── README.md
```

### 2. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: HackRX API"
git branch -M main
git remote add origin https://github.com/yourusername/hackrx-api.git
git push -u origin main
```

### 3. Deploy on Render

#### Option A: Using Render Dashboard

1. **Login to Render**
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Sign in with your GitHub account

2. **Create New Web Service**
   - Click "New +" button
   - Select "Web Service"
   - Choose "Build and deploy from a Git repository"

3. **Connect Repository**
   - Select your GitHub account
   - Choose the repository containing your HackRX API
   - Click "Connect"

4. **Configure Service**
   - **Name**: `hackrx-api` (or your preferred name)
   - **Environment**: `Python 3`
   - **Region**: Choose closest to your users
   - **Branch**: `main`
   - **Root Directory**: Leave empty (or specify if code is in subdirectory)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python src/main.py`

5. **Set Environment Variables**
   Click "Advanced" and add:
   - **Key**: `GOOGLE_API_KEY`, **Value**: Your Google Gemini API key

6. **Choose Plan**
   - **Free Tier**: 512MB RAM, 0.1 CPU (sufficient for testing)
   - **Starter**: $7/month, 512MB RAM, 0.5 CPU (recommended for production)

7. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (usually 2-5 minutes)

#### Option B: Using render.yaml (Infrastructure as Code)

1. **Ensure render.yaml exists** in your repository root
2. **Push to GitHub** (render.yaml will be auto-detected)
3. **Import from Dashboard**
   - Go to Render Dashboard
   - Click "New +" → "Blueprint"
   - Connect your repository
   - Render will read the render.yaml configuration

### 4. Configure Environment Variables

After deployment, set these environment variables in the Render dashboard:

1. **Go to your service** in the Render dashboard
2. **Click "Environment"** tab
3. **Add variables**:
   ```
   GOOGLE_API_KEY=your-actual-gemini-api-key-here
   ```

### 5. Verify Deployment

1. **Check Service Status**
   - Your service should show "Live" status
   - Note the service URL (e.g., `https://hackrx-api.onrender.com`)

2. **Test Health Endpoint**
   ```bash
   curl https://your-service-url.onrender.com/api/health
   ```

3. **Test Main Endpoint**
   ```bash
   curl -X POST https://your-service-url.onrender.com/api/v1/hackrx/run \
     -H "Content-Type: application/json" \
     -d '{
       "documents": "https://example.com/sample.pdf",
       "questions": ["What is this document about?"]
     }'
   ```

## Memory Optimization for Render

### Free Tier Limitations (512MB RAM)

The API is specifically optimized for Render's free tier:

1. **Memory Monitoring**: Built-in memory usage tracking
2. **Automatic Cleanup**: Garbage collection between operations
3. **Size Limits**: 
   - PDF files: 50MB maximum
   - Questions: 20 maximum per request
   - Text processing: 200KB chunks

### Memory Configuration

The application includes several memory optimizations:

```python
# Memory limits in the code
MAX_PDF_SIZE = 50 * 1024 * 1024  # 50MB
MAX_MEMORY_MB = 400  # Leave 100MB buffer for Render
MAX_QUESTIONS = 20
MAX_TEXT_LENGTH = 200000
```

### Monitoring Memory Usage

Check memory usage via the health endpoint:
```bash
curl https://your-service-url.onrender.com/api/health
```

Response includes memory statistics:
```json
{
  "status": "healthy",
  "memory_usage_mb": 45.2,
  "memory_percent": 8.8
}
```

## Troubleshooting Deployment

### Common Issues

1. **Build Failures**
   ```
   Error: Could not find a version that satisfies the requirement...
   ```
   **Solution**: Check `requirements.txt` for correct package versions

2. **Memory Errors**
   ```
   Error: Memory limit exceeded
   ```
   **Solution**: 
   - Reduce PDF size
   - Decrease number of questions
   - Upgrade to Starter plan

3. **API Key Errors**
   ```
   Error: OpenAI API error: Incorrect API key
   ```
   **Solution**: Verify `OPENAI_API_KEY` environment variable

4. **Timeout Errors**
   ```
   Error: Request timeout
   ```
   **Solution**: 
   - Check PDF URL accessibility
   - Reduce document size
   - Increase timeout in code if needed

### Debugging Steps

1. **Check Logs**
   - Go to Render Dashboard → Your Service → Logs
   - Look for error messages and stack traces

2. **Test Locally First**
   ```bash
   python test_api.py
   ```

3. **Verify Environment Variables**
   - Check that all required variables are set
   - Ensure no typos in variable names

4. **Monitor Resource Usage**
   - Watch memory usage in logs
   - Check if hitting memory limits

## Performance Optimization

### For Production Use

1. **Upgrade Plan**
   - Starter plan: $7/month, better performance
   - Professional plan: $25/month, auto-scaling

2. **Optimize Requests**
   - Batch multiple questions in single request
   - Use smaller PDF files when possible
   - Cache frequently accessed documents

3. **Monitor Performance**
   - Use Render's built-in metrics
   - Monitor response times
   - Track memory usage patterns

### Scaling Considerations

1. **Horizontal Scaling**
   - Render auto-scales on higher plans
   - Consider load balancing for high traffic

2. **Database Optimization**
   - Current implementation is stateless
   - Consider caching for frequently accessed PDFs

3. **CDN Integration**
   - Use CDN for static assets
   - Cache API responses where appropriate

## Security Best Practices

1. **Environment Variables**
   - Never commit API keys to repository
   - Use Render's environment variable management

2. **HTTPS**
   - Render provides HTTPS by default
   - All API communication is encrypted

3. **Input Validation**
   - API includes comprehensive input validation
   - Rate limiting can be added if needed

## Maintenance

### Regular Tasks

1. **Monitor Logs**
   - Check for errors and performance issues
   - Monitor memory usage trends

2. **Update Dependencies**
   - Regularly update `requirements.txt`
   - Test updates in development first

3. **Backup Configuration**
   - Keep render.yaml in version control
   - Document environment variables

### Updating the Application

1. **Push Changes**
   ```bash
   git add .
   git commit -m "Update: description of changes"
   git push origin main
   ```

2. **Automatic Deployment**
   - Render automatically deploys on git push
   - Monitor deployment in dashboard

3. **Rollback if Needed**
   - Use Render's rollback feature
   - Or revert git commit and push

## Cost Optimization

### Free Tier Usage

- **Spin Down**: Free services sleep after 15 minutes of inactivity
- **Cold Starts**: First request after sleep takes longer
- **Monthly Limits**: 750 hours per month (sufficient for most use cases)

### Upgrading Plans

- **Starter ($7/month)**: No sleep, faster performance
- **Professional ($25/month)**: Auto-scaling, better resources

## Support and Resources

- **Render Documentation**: [render.com/docs](https://render.com/docs)
- **Render Community**: [community.render.com](https://community.render.com)
- **API Issues**: Check repository issues or create new ones

## Conclusion

This deployment guide provides everything needed to successfully deploy the HackRX API on Render with optimal memory usage and performance. The API is specifically designed to work within Render's constraints while providing reliable PDF processing and query answering capabilities.

