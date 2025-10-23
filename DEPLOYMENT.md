# ShAI Deployment Guide

Complete deployment guide for ShAI (Shae-I) AI Pickup Line Generator across multiple hosting platforms.

## Table of Contents

- [Platform Overview](#platform-overview)
- [Namecheap Shared Hosting](#namecheap-shared-hosting)
- [Heroku](#heroku)
- [Railway](#railway)
- [Render](#render)
- [DigitalOcean App Platform](#digitalocean-app-platform)
- [PythonAnywhere](#pythonanywhere)
- [AWS EC2](#aws-ec2)
- [Google Cloud Platform](#google-cloud-platform)
- [Vercel (Serverless)](#vercel-serverless)
- [Docker Deployment](#docker-deployment)
- [Environment Variables Reference](#environment-variables-reference)
- [Troubleshooting](#troubleshooting)

## Platform Overview

| Platform | Difficulty | Cost | Best For |
|----------|------------|------|----------|
| Heroku | Easy | Free tier available | Quick deployment |
| Railway | Easy | $5/month | Modern deployment |
| Render | Easy | Free tier available | Simple hosting |
| Namecheap | Medium | $2-10/month | Shared hosting |
| DigitalOcean | Medium | $5-25/month | Scalable apps |
| PythonAnywhere | Easy | $5/month | Python-focused |
| AWS EC2 | Hard | Variable | Enterprise |
| GCP | Hard | Variable | Enterprise |
| Vercel | Medium | Free tier available | Serverless |

## Namecheap Shared Hosting

**Best for:** Budget-friendly hosting with cPanel access.

### Prerequisites
- Namecheap shared hosting account with Python support
- Claude API key from [Anthropic](https://console.anthropic.com/)
- FTP/SFTP access

### Deployment Steps

1. **Prepare Files**
   ```bash
   # Create deployment package
   mkdir shai-deploy
   cp -r ShAI/* shai-deploy/
   cd shai-deploy
   
   # Remove development files
   rm -rf __pycache__/ *.pyc venv/ .git/
   ```

2. **Configure Environment**
   ```bash
   # Create .env file
   cat > .env << EOF
   USE_LOCAL=false
   CLAUDE_API_KEY=your-claude-api-key-here
   SECRET_KEY=your-super-secret-production-key
   DEBUG=false
   FLASK_ENV=production
   EOF
   ```

3. **Upload Files**
   - Connect via FTP/SFTP
   - Navigate to `public_html/` or subdomain folder
   - Upload all files including `passenger_wsgi.py`

4. **Configure Python App**
   - Go to cPanel → Python Selector
   - Create new application:
     - Python Version: 3.8+
     - Application Root: `/public_html`
     - Application URL: Your domain
     - Startup File: `passenger_wsgi.py`

5. **Install Dependencies**
   ```bash
   # In cPanel terminal or SSH
   cd public_html
   python -m pip install --user -r requirements.txt
   ```

6. **Set Environment Variables**
   In Python app settings:
   ```
   CLAUDE_API_KEY=your-actual-api-key
   USE_LOCAL=false
   SECRET_KEY=production-secret-key
   ```

## Heroku

**Best for:** Quick deployment with minimal configuration.

### Prerequisites
- Heroku account
- Heroku CLI installed
- Claude API key

### Deployment Steps

1. **Prepare Project**
   ```bash
   cd ShAI
   
   # Create Procfile
   echo "web: gunicorn app:app" > Procfile
   
   # Create runtime.txt (optional)
   echo "python-3.11.0" > runtime.txt
   ```

2. **Initialize Git**
   ```bash
   git init
   git add .
   git commit -m "Initial ShAI deployment"
   ```

3. **Create Heroku App**
   ```bash
   heroku create your-shai-app-name
   ```

4. **Set Environment Variables**
   ```bash
   heroku config:set CLAUDE_API_KEY=your-api-key
   heroku config:set USE_LOCAL=false
   heroku config:set SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
   heroku config:set FLASK_ENV=production
   heroku config:set DEBUG=false
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

6. **Open App**
   ```bash
   heroku open
   ```

### Heroku Configuration Files

**Procfile:**
```
web: gunicorn app:app --timeout 120
```

**runtime.txt:**
```
python-3.11.0
```

## Railway

**Best for:** Modern deployment with excellent developer experience.

### Prerequisites
- Railway account
- GitHub repository
- Claude API key

### Deployment Steps

1. **Push to GitHub**
   ```bash
   cd ShAI
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/shai.git
   git push -u origin main
   ```

2. **Deploy on Railway**
   - Visit [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your ShAI repository
   - Railway auto-detects Python and Flask

3. **Set Environment Variables**
   In Railway dashboard:
   ```
   CLAUDE_API_KEY=your-api-key
   USE_LOCAL=false
   SECRET_KEY=your-production-secret
   FLASK_ENV=production
   PORT=8080
   ```

4. **Configure Start Command**
   ```bash
   # In Railway settings
   gunicorn app:app --bind 0.0.0.0:$PORT
   ```

5. **Access Your App**
   Railway provides a unique URL automatically.

## Render

**Best for:** Simple deployment with free tier.

### Prerequisites
- Render account
- GitHub repository
- Claude API key

### Deployment Steps

1. **Push to GitHub**
   ```bash
   cd ShAI
   git init
   git add .
   git commit -m "Deploy ShAI to Render"
   git push origin main
   ```

2. **Create Web Service**
   - Go to [render.com](https://render.com)
   - Click "New" → "Web Service"
   - Connect GitHub repository

3. **Configure Service**
   ```yaml
   # Build Command
   pip install -r requirements.txt
   
   # Start Command
   gunicorn app:app
   
   # Environment
   PYTHON_VERSION=3.11.0
   ```

4. **Set Environment Variables**
   ```
   CLAUDE_API_KEY=your-api-key
   USE_LOCAL=false
   SECRET_KEY=production-secret-key
   FLASK_ENV=production
   ```

5. **Deploy**
   Render automatically deploys on git push.

## DigitalOcean App Platform

**Best for:** Scalable applications with managed infrastructure.

### Prerequisites
- DigitalOcean account
- GitHub repository
- Claude API key

### Deployment Steps

1. **Create App**
   - Go to DigitalOcean Control Panel
   - Apps → Create App
   - Connect GitHub repository

2. **Configure App**
   ```yaml
   name: shai
   services:
   - name: web
     source_dir: /
     github:
       repo: yourusername/shai
       branch: main
     run_command: gunicorn app:app
     environment_slug: python
     instance_count: 1
     instance_size_slug: basic-xxs
     envs:
     - key: CLAUDE_API_KEY
       value: your-api-key
       type: SECRET
     - key: USE_LOCAL
       value: "false"
     - key: SECRET_KEY
       value: production-secret
       type: SECRET
   ```

3. **Deploy**
   DigitalOcean builds and deploys automatically.

## PythonAnywhere

**Best for:** Python-focused hosting with easy setup.

### Prerequisites
- PythonAnywhere account
- Claude API key

### Deployment Steps

1. **Upload Files**
   - Use Files tab in PythonAnywhere
   - Upload ShAI files to `/home/yourusername/`

2. **Install Dependencies**
   ```bash
   # In PythonAnywhere console
   cd /home/yourusername/ShAI
   pip3.10 install --user -r requirements.txt
   ```

3. **Create Web App**
   - Web tab → Add new web app
   - Python 3.10 → Flask
   - Source code: `/home/yourusername/ShAI`
   - WSGI file: `/home/yourusername/mysite/flask_app.py`

4. **Configure WSGI**
   Edit WSGI file:
   ```python
   import sys
   import os
   
   path = '/home/yourusername/ShAI'
   if path not in sys.path:
       sys.path.append(path)
   
   os.environ['CLAUDE_API_KEY'] = 'your-api-key'
   os.environ['USE_LOCAL'] = 'false'
   os.environ['SECRET_KEY'] = 'production-secret'
   
   from app import app as application
   ```

5. **Reload Web App**
   Click reload in Web tab.

## AWS EC2

**Best for:** Full control and enterprise deployments.

### Prerequisites
- AWS account
- EC2 instance (Ubuntu 20.04+)
- Domain name (optional)
- Claude API key

### Deployment Steps

1. **Launch EC2 Instance**
   ```bash
   # Instance type: t2.micro (free tier)
   # OS: Ubuntu 20.04 LTS
   # Security Group: Allow HTTP (80), HTTPS (443), SSH (22)
   ```

2. **Connect and Setup**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install Python and dependencies
   sudo apt install python3 python3-pip python3-venv nginx -y
   ```

3. **Deploy Application**
   ```bash
   # Clone or upload ShAI files
   cd /home/ubuntu
   git clone https://github.com/yourusername/shai.git
   cd shai
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install gunicorn
   ```

4. **Configure Environment**
   ```bash
   # Create .env file
   cat > .env << EOF
   CLAUDE_API_KEY=your-api-key
   USE_LOCAL=false
   SECRET_KEY=production-secret-key
   FLASK_ENV=production
   DEBUG=false
   EOF
   ```

5. **Setup Systemd Service**
   ```bash
   sudo nano /etc/systemd/system/shai.service
   ```
   
   ```ini
   [Unit]
   Description=ShAI Flask App
   After=network.target
   
   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/shai
   Environment=PATH=/home/ubuntu/shai/venv/bin
   EnvironmentFile=/home/ubuntu/shai/.env
   ExecStart=/home/ubuntu/shai/venv/bin/gunicorn --bind 0.0.0.0:8000 app:app
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

6. **Configure Nginx**
   ```bash
   sudo nano /etc/nginx/sites-available/shai
   ```
   
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
   
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

7. **Start Services**
   ```bash
   sudo systemctl enable shai
   sudo systemctl start shai
   sudo ln -s /etc/nginx/sites-available/shai /etc/nginx/sites-enabled
   sudo systemctl restart nginx
   ```

## Google Cloud Platform

**Best for:** Enterprise deployments with Google services.

### Prerequisites
- GCP account
- gcloud CLI installed
- Claude API key

### Deployment Steps

1. **Create Project**
   ```bash
   gcloud projects create your-shai-project
   gcloud config set project your-shai-project
   ```

2. **Enable APIs**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   ```

3. **Create app.yaml**
   ```yaml
   runtime: python311
   
   env_variables:
     CLAUDE_API_KEY: "your-api-key"
     USE_LOCAL: "false"
     SECRET_KEY: "production-secret"
     FLASK_ENV: "production"
   
   automatic_scaling:
     min_instances: 1
     max_instances: 10
   ```

4. **Deploy to App Engine**
   ```bash
   gcloud app deploy
   ```

5. **Access Application**
   ```bash
   gcloud app browse
   ```

## Vercel (Serverless)

**Best for:** Serverless deployment with edge functions.

### Prerequisites
- Vercel account
- GitHub repository
- Claude API key

### Deployment Steps

1. **Create vercel.json**
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "app.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "app.py"
       }
     ],
     "env": {
       "CLAUDE_API_KEY": "@claude_api_key",
       "USE_LOCAL": "false",
       "SECRET_KEY": "@secret_key"
     }
   }
   ```

2. **Deploy with Vercel CLI**
   ```bash
   npm i -g vercel
   vercel
   ```

3. **Set Environment Variables**
   ```bash
   vercel env add CLAUDE_API_KEY
   vercel env add SECRET_KEY
   vercel env add USE_LOCAL
   ```

## Docker Deployment

**Best for:** Containerized deployment across any platform.

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  shai:
    build: .
    ports:
      - "5000:5000"
    environment:
      - CLAUDE_API_KEY=your-api-key
      - USE_LOCAL=false
      - SECRET_KEY=production-secret
      - FLASK_ENV=production
    restart: unless-stopped
```

### Deployment Commands
```bash
# Build and run
docker build -t shai .
docker run -p 5000:5000 --env-file .env shai

# Or with docker-compose
docker-compose up -d
```

## Environment Variables Reference

### Required Variables
```env
CLAUDE_API_KEY=your-claude-api-key-here
USE_LOCAL=false
SECRET_KEY=your-production-secret-key
```

### Optional Variables
```env
DEBUG=false
FLASK_ENV=production
PORT=5000
OLLAMA_URL=http://localhost:11434
LOG_LEVEL=INFO
```

### Security Notes
- Never commit API keys to version control
- Use platform-specific secret management
- Generate strong secret keys
- Use environment variables, not hardcoded values

## Troubleshooting

### Common Issues

**Application Won't Start**
```bash
# Check logs
heroku logs --tail  # Heroku
railway logs        # Railway
docker logs shai    # Docker
```

**API Key Issues**
- Verify key is correctly set in environment
- Check API key validity at Anthropic console
- Ensure account has sufficient credits

**Dependency Errors**
```bash
# Update requirements.txt
pip freeze > requirements.txt

# Clear pip cache
pip cache purge
```

**Performance Issues**
- Increase timeout values for AI requests
- Use larger instance sizes
- Implement request caching
- Add error handling and retries

### Platform-Specific Debugging

**Heroku**
```bash
heroku logs --tail --app your-app-name
heroku run bash --app your-app-name
heroku config --app your-app-name
```

**Railway**
```bash
railway logs
railway shell
railway variables
```

**Docker**
```bash
docker logs shai
docker exec -it shai bash
docker inspect shai
```

### Health Check Endpoints

All deployments include health check endpoints:
- `GET /health` - Application health status
- `GET /` - Main application interface

Use these for monitoring and load balancer health checks.

---

## Quick Reference

| Need | Use This Platform |
|------|-------------------|
| Free hosting | Heroku, Render, Railway (free tiers) |
| Shared hosting | Namecheap, PythonAnywhere |
| Quick deployment | Heroku, Railway, Render |
| Full control | AWS EC2, DigitalOcean Droplet |
| Serverless | Vercel, AWS Lambda, GCP Cloud Run |
| Container deployment | Docker on any platform |

**Remember:** Always test your deployment with the `/health` endpoint and a few pickup line generations before going live!

Happy deploying! 🚀💕