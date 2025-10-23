# ShAI (pronounced "Shae-I")

🎯 **Your AI-Powered Pickup Line Generator** - Turn any situation into smooth conversation starters!

ShAI is a modern web application that generates creative, witty, and charming pickup lines using the latest AI technology. Powered by Claude 3.5 Haiku for lightning-fast, creative responses, ShAI turns any situation into smooth conversation starters!

## ✨ Features

- **🤖 AI-Powered Generation**: Uses Claude 3.5 Haiku (latest model) or local Ollama models
- **🎤 Voice Input**: Speech-to-text support for hands-free operation
- **📱 Modern UI**: Responsive design that works on all devices
- **🌙 Dark Mode**: Automatic dark/light mode based on system preferences
- **📋 Easy Sharing**: Copy and share pickup lines instantly
- **⚡ Fast & Reliable**: Quick response times with fallback options
- **🔒 Privacy-First**: Your conversations stay private
- **🚀 Auto-Initialization**: Automatic setup for Namecheap shared hosting

## 🚀 Quick Start

Choose your preferred setup method:

### Option 1: Local Development (Recommended for Testing)
Perfect for trying out ShAI without any API keys!

```bash
# 1. Clone and setup
git clone <your-repo-url>
cd ShAI
python deploy.py --local

# 2. Start the app
python app.py

# 3. Visit http://localhost:5000
```

### Option 2: Production Deployment
For deploying to shared hosting like Namecheap:

```bash
# 1. Setup for production
python deploy.py --production

# 2. Get your Claude API key from https://console.anthropic.com/
# 3. Add it to your .env file
# 4. Upload to your hosting provider
```

## 💬 How It Works

1. **Input Your Situation**: Describe where you are or what you're interested in
2. **Choose Your Method**: Type directly or use voice input (click the microphone)
3. **Get AI-Generated Lines**: ShAI creates 3-5 personalized pickup lines
4. **Copy & Use**: Click any line to copy it to your clipboard
5. **Share the Fun**: Use the share button to spread the charm!

## 🛠️ Installation Methods

### 🏠 Local Development (Free & Offline)
Perfect for testing and development. Uses Ollama to run AI models locally.

**Requirements:**
- Python 3.8+
- [Ollama](https://ollama.ai/) installed

**Steps:**
```bash
# 1. Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh  # macOS/Linux
# or download from ollama.ai for Windows

# 2. Download AI model
ollama serve
ollama pull llama2

# 3. Setup ShAI
python deploy.py --local
python app.py

# 4. Open http://localhost:5000
```

**Production Deployment (Namecheap Shared Hosting)**
Deploy to the web using Claude 3.5 Haiku API with automatic initialization.

**Requirements:**
- Namecheap shared hosting account
- Claude API key from [Anthropic](https://console.anthropic.com/)

**Steps:**
```bash
# 1. Auto-setup for Namecheap (recommended)
python namecheap_init.py

# 2. Or manual setup
python deploy.py --production

# 3. Get Claude API key and add to .env file
CLAUDE_API_KEY=your-api-key-here

# 4. Upload files via FTP/SFTP to your hosting account
# 5. The enhanced passenger_wsgi.py will auto-initialize everything!
```

**Auto-Initialization Features:**
- Automatically detects Namecheap hosting environment
- Installs missing dependencies
- Sets proper file permissions
- Creates necessary directories
- Provides detailed error diagnostics

## 🎯 Usage Examples

**Coffee Shop Scenario:**
> Input: "I'm at a coffee shop and there's someone reading a book"
> 
> ShAI generates: "Are you a book? Because I can't put you down, and I'd love to know your story."

**General Conversation:**
> Input: "I want something funny and lighthearted"
>
> ShAI generates: "Are you Wi-Fi? Because I'm really feeling a connection."

**Voice Input:**
> Just click the microphone and say: "I'm at the gym and need something fitness-related"

## 📁 Project Structure

```
ShAI/
├── app.py                 # Main Flask application
├── wsgi.py               # WSGI configuration
├── passenger_wsgi.py     # Namecheap hosting configuration
├── deploy.py             # Automated deployment script
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── templates/           # HTML templates
│   ├── index.html       # Main application interface
│   ├── 404.html         # Error page
│   └── 500.html         # Server error page
├── static/              # Static assets
│   ├── css/             # Stylesheets (embedded in HTML)
│   └── js/              # JavaScript files
│       └── app.js       # Main application logic
└── SETUP.md             # Detailed setup instructions
```

## 🔧 Configuration

### Environment Variables

**Local Development (.env):**
```env
USE_LOCAL=true
OLLAMA_URL=http://localhost:11434
DEBUG=true
SECRET_KEY=your-local-secret
```

**Production (.env):**
```env
USE_LOCAL=false
CLAUDE_API_KEY=your-claude-api-key
DEBUG=false
SECRET_KEY=your-production-secret
```

### Customization

- **Styling**: Edit the CSS in `templates/index.html`
- **AI Prompts**: Modify prompts in `app.py`
- **Models**: Change Ollama models in the configuration
- **Features**: Add new endpoints or functionality as needed

## 🚀 API Endpoints

- `GET /` - Main application interface
- `POST /generate` - Generate pickup lines API
- `GET /health` - Health check endpoint
- `GET /404` - Custom 404 page
- `GET /500` - Custom error page

**API Example:**
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"input": "I am at a coffee shop"}'
```

## 🛡️ Security & Privacy

- **API Key Protection**: Environment variables keep keys secure
- **Input Validation**: XSS protection and sanitization
- **No Data Storage**: Conversations aren't saved or logged
- **HTTPS Ready**: SSL/TLS support for production deployments

## 🎨 Browser Support

- **Chrome**: Full support (including voice recognition)
- **Firefox**: Full support (including voice recognition)  
- **Safari**: Basic support (limited voice features)
- **Mobile**: Responsive design works on all devices
- **Dark Mode**: Automatic based on system preferences

## 🔍 Troubleshooting

**Common Issues:**

- **"Connection refused"**: Make sure Ollama is running (`ollama serve`)
- **"API Key Invalid"**: Check your Claude API key and account credits
- **Voice not working**: Use HTTPS and allow microphone permissions
- **Slow responses**: Try a smaller Ollama model like `mistral`

**Shared Hosting Issues:**
- **Unicode/Encoding Errors**: The enhanced `passenger_wsgi.py` now uses ASCII-only logging to prevent encoding issues
- **Missing Dependencies**: Run `python install_deps.py` to automatically install Flask, requests, etc.
- **Import Errors**: Use `python namecheap_init.py --fix` to resolve common hosting issues
- **Permission Errors**: The auto-initialization sets proper file permissions automatically

**Getting Help:**
- Check the detailed [SETUP.md](SETUP.md) guide
- Verify your `.env` configuration
- Test with `python deploy.py --check`
- Check browser console for JavaScript errors

## 📖 Documentation

- **[SETUP.md](SETUP.md)** - Comprehensive setup guide
- **[Flask Documentation](https://flask.palletsprojects.com/)** - Web framework docs
- **[Ollama Documentation](https://ollama.ai/docs)** - Local AI model docs  
- **[Claude API](https://docs.anthropic.com/claude/reference)** - Cloud AI docs

## 🤝 Contributing

ShAI started as a fun project and we welcome improvements! Whether it's:

- 🐛 Bug fixes
- ✨ New features
- 📚 Documentation improvements
- 🎨 UI/UX enhancements
- 🧪 Tests and quality improvements

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

## 🎉 Credits

- **AI Models**: Claude 3.5 Haiku (Anthropic) and Ollama community models
- **Framework**: Flask (Python web framework)
- **Inspiration**: Born from a joke in science class, evolved into something actually useful!

---

**Ready to create some smooth conversation starters?** 🚀❤️

**Quick Start Options:**
- Local: `python deploy.py --local` 
- Namecheap: `python namecheap_init.py` (auto-setup!)
- Other hosting: `python deploy.py --production`

*Remember: Great pickup lines are just conversation starters - your personality does the rest!* 😉