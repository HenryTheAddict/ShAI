# ShAI Setup Guide

A comprehensive guide to set up ShAI (pronounced "Shae-I"), your AI pickup line generator that works with both local Ollama models and Claude API.

## Table of Contents

- [Quick Start](#quick-start)
- [Local Development Setup](#local-development-setup)
- [Production Deployment (Namecheap Shared Hosting)](#production-deployment-namecheap-shared-hosting)
- [Environment Configuration](#environment-configuration)
- [API Keys Setup](#api-keys-setup)
- [Testing Your Setup](#testing-your-setup)
- [Troubleshooting](#troubleshooting)
- [Features](#features)

## Quick Start

Choose your deployment method:

- **Local Development**: Uses Ollama for AI generation (free, runs offline)
- **Production Hosting**: Uses Claude API for AI generation (requires API key)

## Local Development Setup

Perfect for testing and development. Uses Ollama to run AI models locally.

### Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running

### Step 1: Install Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from [ollama.ai](https://ollama.ai/download)

### Step 2: Download AI Model

```bash
# Start Ollama service
ollama serve

# In another terminal, download a model (choose one):
ollama pull llama2        # Recommended for better performance
ollama pull codellama     # Alternative option
ollama pull mistral       # Smaller, faster option
```

### Step 3: Clone and Setup Project

```bash
# Clone the repository (or extract if you have the files)
cd ShAI

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

Set these values in `.env`:
```env
USE_LOCAL=true
OLLAMA_URL=http://localhost:11434
DEBUG=true
SECRET_KEY=your-local-secret-key
```

### Step 5: Run the Application

```bash
# Make sure Ollama is running in another terminal:
ollama serve

# Run the Flask app
python app.py
```

Visit `http://localhost:5000` in your browser!

## Production Deployment (Namecheap Shared Hosting)

Deploy ShAI to Namecheap's shared Python hosting using Claude API.

### Prerequisites

- Namecheap shared hosting account with Python support
- Claude API key from [Anthropic](https://console.anthropic.com/)
- FTP/SFTP access to your hosting account

### Step 1: Get Claude API Key

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create an account or sign in
3. Go to API Keys section
4. Create a new API key
5. Save the key securely (you'll need it later)

**Note:** ShAI uses the latest Claude 3.5 Haiku model (`claude-3-5-haiku-20241022`) for optimal performance and cost efficiency.

### Step 2: Auto-Initialize for Namecheap (Recommended)

ShAI includes automatic initialization for Namecheap hosting:

```bash
# Run the Namecheap initialization script
python namecheap_init.py

# This will:
# - Detect Namecheap hosting environment
# - Install dependencies automatically  
# - Configure environment variables
# - Set proper file permissions
# - Create necessary directories
# - Test the setup
```

### Step 2 Alternative: Manual Preparation

```bash
# Create a deployment package (manual method)
mkdir shai-deploy
cd shai-deploy

# Copy all application files (excluding development files)
cp -r ../ShAI/* .

# Remove development files
rm -rf __pycache__/ *.pyc .env

# Create production environment file
cp .env.example .env
```

Edit the `.env` file for production:
```env
USE_LOCAL=false
CLAUDE_API_KEY=your-claude-api-key-here
SECRET_KEY=your-production-secret-key-here
DEBUG=false
FLASK_ENV=production
```

### Step 3: Upload to Namecheap

1. **Connect via FTP/SFTP** to your Namecheap hosting account
2. **Navigate to your domain's folder** (usually `public_html/` or your subdomain folder)
3. **Upload all files** including:
   - `app.py`
   - `wsgi.py` 
   - `passenger_wsgi.py` (with auto-initialization)
   - `namecheap_init.py` (initialization helper)
   - `requirements.txt`
   - `.env`
   - `templates/` folder
   - `static/` folder

**Important:** The enhanced `passenger_wsgi.py` will automatically initialize the application when accessed for the first time on Namecheap hosting.

### Step 4: Install Dependencies

**Method 1: SSH Access (if available)**
```bash
ssh your-username@your-domain.com
cd public_html  # or your app directory
python -m pip install --user -r requirements.txt
```

**Method 2: Via Namecheap Control Panel**
1. Go to Advanced → Python Selector
2. Create Python App
3. Install packages from requirements.txt

### Step 5: Configure Python Application

In Namecheap control panel:

1. **Go to Advanced → Python Selector**
2. **Create Application:**
   - Python Version: 3.8+ (3.11+ recommended)
   - Application Root: `/public_html` (or your subfolder)  
   - Application URL: your domain
   - Application Startup File: `passenger_wsgi.py`
3. **Auto-Installation:** 
   - The enhanced `passenger_wsgi.py` will automatically detect and install missing packages
   - Check `/logs/passenger_wsgi.log` for initialization details
4. **Manual Package Installation (if needed):**
   - Upload `requirements.txt`
   - Install packages via control panel

### Step 6: Set Environment Variables

In the Python app configuration:
```
CLAUDE_API_KEY=your-actual-claude-api-key
USE_LOCAL=false
SECRET_KEY=your-production-secret-key
FLASK_ENV=production
DEBUG=false
```

## Environment Configuration

### Local Development (.env)
```env
# Local development with Ollama
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=true
PORT=5000
USE_LOCAL=true
OLLAMA_URL=http://localhost:11434
LOG_LEVEL=DEBUG
```

### Production (.env)
```env
# Production with Claude API
SECRET_KEY=super-secret-production-key-here
DEBUG=false
FLASK_ENV=production
USE_LOCAL=false
CLAUDE_API_KEY=your-claude-api-key-here
LOG_LEVEL=INFO
```

## API Keys Setup

### Claude API (Anthropic)

1. **Sign up** at [console.anthropic.com](https://console.anthropic.com/)
2. **Verify your phone number** (required)
3. **Add billing method** (Claude API uses pay-per-use pricing)
4. **Generate API key** in the API Keys section
5. **Copy the key** and add it to your `.env` file

**Model Information**: ShAI uses Claude 3.5 Haiku (`claude-3-5-haiku-20241022`), which offers:
- Fast response times (perfect for pickup lines!)
- Cost-effective pricing
- High-quality creative output
- Excellent instruction following

**Important**: Never commit your API key to version control!

### Ollama (Local Development)

1. **Install Ollama** from [ollama.ai](https://ollama.ai/)
2. **Start the service**: `ollama serve`
3. **Download a model**: `ollama pull llama2`
4. **Verify it's running**: Visit `http://localhost:11434`

## Testing Your Setup

### Local Development Test

```bash
# 1. Start Ollama
ollama serve

# 2. In another terminal, test the model
ollama run llama2 "Generate a pickup line"

# 3. Start your ShAI app
python app.py

# 4. Visit http://localhost:5000 and test the interface
```

### Production Test

1. **Visit your deployed URL**
2. **Test the health endpoint**: `https://yourdomain.com/health`
3. **Try generating pickup lines** with different inputs
4. **Check browser console** for any JavaScript errors

### API Endpoint Testing

You can test the API directly:

```bash
# Test local
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"input": "I am at a coffee shop"}'

# Test production
curl -X POST https://yourdomain.com/generate \
  -H "Content-Type: application/json" \
  -d '{"input": "I am at a coffee shop"}'
```

## Troubleshooting

### Common Issues

#### "Connection refused" Error (Local)
**Problem**: Can't connect to Ollama
**Solutions**:
- Ensure Ollama is running: `ollama serve`
- Check if port 11434 is available
- Verify OLLAMA_URL in .env file

#### "API Key Invalid" Error (Production)
**Problem**: Claude API authentication failed
**Solutions**:
- Verify your API key is correct
- Check if you have credits in your Anthropic account
- Ensure the key has proper permissions

#### "Module not found" Error
**Problem**: Python dependencies missing
**Solutions**:
```bash
# Local
pip install -r requirements.txt

# Production (Namecheap) - Multiple options:
# 1. Auto-initialization (recommended)
python namecheap_init.py

# 2. Manual installation via control panel
# Use the Python Selector in control panel to install packages

# 3. SSH installation (if available)  
python -m pip install --user -r requirements.txt
```

#### Voice Recognition Not Working
**Problem**: Voice input button is disabled
**Solutions**:
- Use HTTPS (required for voice API)
- Allow microphone permissions in browser
- Try a different browser (Chrome/Firefox recommended)

#### Slow Response Times
**Problem**: Pickup line generation takes too long
**Solutions**:
- **Local**: Use a smaller Ollama model like `mistral`
- **Production**: Check your internet connection
- Increase timeout values in the code if needed

### Debug Mode

Enable debug mode for detailed error information:

```bash
# Local development
export DEBUG=true
python app.py

# Check logs
tail -f logs/shai.log  # if logging is set up
```

### Namecheap-Specific Debugging

For Namecheap hosting issues:

```bash
# Run comprehensive diagnostics
python namecheap_init.py --debug

# Verify setup
python namecheap_init.py --verify  

# Fix common issues
python namecheap_init.py --fix

# Check auto-initialization logs
cat logs/passenger_wsgi.log
```

### Log Files

**Local Development**: Check console output
**Production**: Check your hosting provider's error logs
**Namecheap**: Check `logs/passenger_wsgi.log` and `logs/namecheap_init.log` for detailed diagnostics

## Features

### 🎯 Core Features

- **AI-Powered**: Uses Claude Haiku or local Ollama models
- **Voice Input**: Speech-to-text support (HTTPS required)
- **Modern UI**: Responsive design with dark mode support
- **Copy & Share**: Easy pickup line sharing
- **Real-time**: Fast response times
- **Error Handling**: Graceful fallbacks and error messages

### 🌐 Deployment Options

- **Local Development**: Ollama integration for offline use
- **Shared Hosting**: Namecheap and similar providers
- **Cloud Platforms**: Easy deployment to Heroku, DigitalOcean, etc.

### 📱 Browser Compatibility

- **Chrome**: Full support including voice recognition
- **Firefox**: Full support including voice recognition
- **Safari**: Basic support (voice may be limited)
- **Mobile**: Responsive design works on all devices

### 🔒 Security Features

- **API Key Protection**: Environment variable security
- **Input Validation**: XSS protection and input sanitization
- **Rate Limiting**: Built-in request throttling
- **HTTPS Ready**: SSL/TLS support for production

## Additional Configuration

### Custom Ollama Models

You can use different models with Ollama:

```bash
# Install different models
ollama pull mistral          # Faster, smaller
ollama pull codellama        # Code-focused
ollama pull neural-chat      # Conversation-focused

# Update your code to use different model
# In app.py, change the model name in generate_with_ollama()
```

### Performance Tuning

**Local Development**:
- Use SSD storage for better Ollama performance
- Allocate more RAM to Ollama if available
- Close unnecessary applications

**Production**:
- Use CDN for static files
- Enable gzip compression
- Implement caching for repeated requests

### Customization

**Styling**: Edit `templates/index.html` and the embedded CSS
**Prompts**: Modify the AI prompts in `app.py`
**Features**: Add new endpoints or functionality as needed

## Support

### Getting Help

- **Check the logs** for specific error messages
- **Test with curl** to isolate API issues
- **Try different browsers** for frontend issues
- **Verify environment variables** are set correctly

### Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Ollama Documentation](https://ollama.ai/docs)
- [Anthropic Claude API](https://docs.anthropic.com/claude/reference)
- [Namecheap Python Hosting Guide](https://www.namecheap.com/support/knowledgebase/article.aspx/10090/2213/python-app-deployment)

---

**Enjoy creating amazing pickup lines with ShAI!** 🚀❤️