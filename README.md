# 📰 News Aggregation System with DeepSeek AI

An intelligent, automated news aggregation and monitoring system powered by LangChain, DeepSeek API, and Python. Search the web for news, get AI-powered analysis, and receive beautifully formatted email reports on demand or on a schedule.

!["image"](image.png)

## ✨ Features

- **🚀 Instant Reports**: Get immediate news reports on any topic
- **⏰ Scheduled Monitoring**: Continuous monitoring with reports every N hours
- **📊 Aggregate Reports**: Compile comprehensive summaries from monitoring history
- **🤖 AI-Powered Analysis**: DeepSeek AI analyzes and summarizes findings
- **📧 Email Delivery**: Professional HTML email reports
- **🔍 Web Search**: Integrated DuckDuckGo search (extensible to other providers)
- **💾 Persistent Storage**: SQLite database for monitoring history
- **🎯 CLI Interface**: Easy-to-use command-line tool
- **🔧 Flexible Configuration**: Environment variables or YAML config

## 📋 Requirements

- Python 3.8+
- DeepSeek API key
- Email account for sending reports (Gmail, Outlook, or custom SMTP)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd /home/user/Documents/Proyecto

# The bash script will auto-create the venv and install dependencies
./news-cli --help
```

### 2. Configure

Create a `.env` file with your credentials:

```bash
cp .env.example .env
nano .env
```

Required configuration:

```env
DEEPSEEK_API_KEY=your_deepseek_api_key_here
EMAIL_FROM_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password_here
```

> [!IMPORTANT]
> **Gmail Users**: Use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.
> 1. Enable 2-Factor Authentication on your Google account
> 2. Go to Security → App Passwords
> 3. Generate a new app password for "Mail"

### 3. Run Your First Report

```bash
./news-cli instant --prompt "latest AI technology news" --email your@email.com
```

## 📖 Usage

### Instant Report

Generate and send an immediate news report:

```bash
./news-cli instant --prompt "cryptocurrency market trends" --email you@example.com
```

### Scheduled Monitoring

Start continuous monitoring with reports every N hours:

```bash
# Monitor every 6 hours
./news-cli schedule --prompt "climate change developments" --interval 6 --email you@example.com

# Monitor every 2 hours
./news-cli schedule --prompt "tech industry news" --interval 2 --email you@example.com
```

Press `Ctrl+C` to stop monitoring.

### Aggregate Report

Generate a comprehensive summary from monitoring history:

```bash
# Aggregate specific session
./news-cli aggregate --session-id 1 --email you@example.com

# Aggregate all sessions
./news-cli aggregate --all --email you@example.com
```

### Check Status

View active monitoring sessions:

```bash
./news-cli status
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file (copy from `.env.example`):

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `DEEPSEEK_API_KEY` | Your DeepSeek API key | ✅ Yes | `sk-123...` |
| `EMAIL_FROM_ADDRESS` | Sender email address (must match SMTP auth) | ✅ Yes | `you@gmail.com` |
| `EMAIL_PASSWORD` | Email password/app password | ✅ Yes | `abcd efgh ijkl mnop` |
| `EMAIL_SMTP_SERVER` | SMTP server address | No | `smtp.gmail.com` |
| `EMAIL_SMTP_PORT` | SMTP port number | No | `587` |
| `DEEPSEEK_MODEL` | Model name to use | No | `deepseek-chat` |
| `LOG_LEVEL` | Logging verbosity | No | `INFO` |

### YAML Configuration

Alternatively, create `config.yaml` (copy from `config.yaml.example`):

```yaml
deepseek:
  api_key: your_key_here
  model: deepseek-chat
  temperature: 0.7

email:
  smtp_server: smtp.gmail.com
  smtp_port: 587
  from_address: your_email@gmail.com
  password: your_password_here

search:
  default_tool: duckduckgo
  max_results: 10

scheduler:
  default_interval_hours: 6
  timezone: America/New_York
```

> [!NOTE]
> Environment variables take precedence over YAML configuration.

## 🏗️ Architecture

```
news-aggregator/
├── src/
│   ├── api/              # DeepSeek API client
│   ├── agents/           # LangChain news agent
│   ├── reporters/        # Email and report generation
│   ├── scheduler/        # APScheduler and data management
│   └── config/           # Configuration management
├── data/                 # SQLite database
├── logs/                 # Application logs
├── main.py               # CLI application
├── news-cli              # Bash launcher
└── requirements.txt      # Dependencies
```

## 🔧 Advanced Usage

### Custom SMTP Server

For Outlook/Office365:

```env
EMAIL_SMTP_SERVER=smtp.office365.com
EMAIL_SMTP_PORT=587
EMAIL_FROM=your_email@outlook.com
EMAIL_PASSWORD=your_password
```

### Configure Timezone

Set your preferred timezone in `config.yaml`:

```yaml
scheduler:
  timezone: Europe/London  # or America/Los_Angeles, Asia/Tokyo, etc.
```

### Database Location

Change database path in `config.yaml`:

```yaml
app:
  database_path: ./data/news.db
```

## 📊 Report Examples

### Instant Report Email

- **Executive Summary**: AI-generated overview
- **Key Developments**: Highlighted important points
- **Detailed Analysis**: Comprehensive insights
- **Source Articles**: Links to all found articles

### Aggregate Report Email

- **Period Overview**: Time range covered
- **Major Trends**: Patterns across multiple reports
- **Key Insights**: Synthesized findings
- **All Articles**: Deduplicated article list

## 🔍 Troubleshooting

### Email Not Sending

1. **Gmail**: Ensure you're using an App Password, not your regular password
2. **2FA Required**: Gmail requires 2-Factor Authentication to create App Passwords
3. **Less Secure Apps**: Don't enable this - use App Passwords instead
4. **Check SMTP settings**: Verify server and port are correct

### DeepSeek API Errors

1. **Invalid API Key**: Check `DEEPSEEK_API_KEY` in `.env`
2. **Rate Limiting**: DeepSeek may have rate limits - add delays between requests
3. **Model Access**: Ensure you have access to the specified model

### No Articles Found

1. **Search Query**: Try more specific or broader search terms
2. **Network Issues**: Check internet connection
3. **Search Tool**: DuckDuckGo sometimes has rate limits - retry after a delay

### Database Locked

If monitoring runs while accessing the database:
```bash
# Stop all monitoring sessions first
./news-cli status
# Then manually stop via Ctrl+C in the monitoring terminal
```

## 🛠️ Development

### Install Development Dependencies

```bash
source venv/bin/activate
pip install -r requirements.txt
pip install pytest black flake8
```

### Run Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
```

## 📝 System Requirements

- **Python**: 3.8 or higher
- **Memory**: 512MB minimum, 1GB recommended
- **Storage**: 100MB for application + database growth
- **Network**: Stable internet connection for API calls and web search

## 🔐 Security Notes

- Never commit `.env` or `config.yaml` with real credentials
- Use App Passwords instead of email account passwords
- Rotate API keys periodically
- Keep dependencies updated for security patches

## 📜 License

This project is provided as-is for personal and commercial use.

## 🤝 Support

For issues or questions:
1. Check this README
2. Review error logs in `logs/` directory
3. Verify configuration in `.env` file

## 🎯 Future Enhancement Ideas

- [ ] Support for Google Search API and Tavily
- [ ] Slack/Discord notifications
- [ ] Web dashboard for monitoring management
- [ ] Export reports as PDF
- [ ] Multi-language support
- [ ] Custom email templates
- [ ] Article sentiment analysis
- [ ] Trending topics detection

---

