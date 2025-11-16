# Telegram Torrent Bot 🤖

A Python-based Telegram bot that integrates with qBittorrent to manage torrent downloads. Send magnet links or .torrent files and organize them into Movies or TV Shows folders automatically.

## Features ✨

- 📥 **Add torrents via magnet links** - Simply paste a magnet link
- 📄 **Upload .torrent files** - Send .torrent files directly to the bot
- 📁 **Smart categorization** - Choose between Movies or TV Shows folders
- 🔄 **qBittorrent integration** - Seamless API integration with qBittorrent
- 🔒 **Environment-based configuration** - Secure credential management
- 📊 **Status monitoring** - Check qBittorrent connection and active torrents

## Prerequisites 📋

- Python 3.8 or higher
- qBittorrent with Web UI enabled
- A Telegram Bot Token (from [@BotFather](https://t.me/botfather))

## Installation 🚀

1. **Clone or navigate to the project directory:**
   ```bash
   cd /home/denilv/projects/telegram-torrent-bot
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and fill in your credentials:
   ```env
   # Telegram Bot Configuration
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   
   # qBittorrent Configuration
   QBITTORRENT_URL=http://localhost:8080
   QBITTORRENT_USERNAME=admin
   QBITTORRENT_PASSWORD=adminpass
   
   # Storage Folders (paths in qBittorrent)
   MOVIES_FOLDER=/downloads/movies
   TV_SHOWS_FOLDER=/downloads/tv_shows
   ```

## qBittorrent Setup 🔧

1. **Enable Web UI in qBittorrent:**
   - Go to Tools → Options → Web UI
   - Check "Enable Web User Interface (Remote control)"
   - Set username and password
   - Note the port (default: 8080)

2. **Create download folders:**
   - Make sure the paths specified in `MOVIES_FOLDER` and `TV_SHOWS_FOLDER` exist
   - These paths should be accessible by qBittorrent

## Usage 🎯

### Option 1: Using Docker (Recommended)

1. **Build and start the bot:**
   ```bash
   docker-compose up -d
   ```

2. **View logs:**
   ```bash
   docker-compose logs -f
   ```

3. **Stop the bot:**
   ```bash
   docker-compose down
   ```

4. **Restart the bot:**
   ```bash
   docker-compose restart
   ```

The bot will automatically start on system boot with the `restart: unless-stopped` policy.

### Option 2: Running Directly with Python

1. **Start the bot:**
   ```bash
   python bot.py
   ```

### Interacting with the Bot

1. **On Telegram:**
   - Send `/start` to begin
   - Send `/help` for usage instructions
   - Send `/status` to check qBittorrent connection

2. **Add torrents:**
   - **Magnet link:** Simply paste the magnet link
   - **Torrent file:** Upload the .torrent file
   - Choose the category (Movies or TV Shows)
   - Done! The torrent will be added to qBittorrent

## Commands 📝

- `/start` - Start the bot and see welcome message
- `/help` - Display help information
- `/status` - Check qBittorrent connection status and active torrents

## Docker Deployment 🐳

The project includes Docker support for easy deployment:

**Files:**
- `Dockerfile` - Alpine-based Python image for minimal size
- `docker-compose.yml` - Service configuration with auto-restart
- `.dockerignore` - Excludes unnecessary files from build

**Auto-start on System Boot:**
The `docker-compose.yml` includes `restart: unless-stopped` policy, ensuring the bot automatically starts when your system boots.

**To enable Docker service on boot (if not already enabled):**
```bash
sudo systemctl enable docker
```

## Project Structure 📂

```
telegram-torrent-bot/
├── bot.py                  # Main bot application
├── qbittorrent_client.py   # qBittorrent API client wrapper
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker image definition
├── docker-compose.yml     # Docker Compose configuration
├── .dockerignore         # Docker build exclusions
├── .env.example          # Example environment configuration
├── .env                  # Your actual configuration (not in git)
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Security Notes 🔒

- Never commit your `.env` file to version control
- Keep your Telegram bot token secret
- Use strong passwords for qBittorrent Web UI
- Consider running qBittorrent Web UI on localhost only for security

## Troubleshooting 🔍

**Bot won't start:**
- Check that `TELEGRAM_BOT_TOKEN` is set correctly in `.env`
- Verify Python dependencies are installed (or Docker image built correctly)
- Check logs: `docker-compose logs -f` (if using Docker)

**Can't connect to qBittorrent:**
- Ensure qBittorrent is running with Web UI enabled
- Verify `QBITTORRENT_URL`, `QBITTORRENT_USERNAME`, and `QBITTORRENT_PASSWORD` are correct
- Check that the qBittorrent port is accessible
- If using Docker, qBittorrent should be accessible from the container (use host network or proper container networking)
- Try using `host.docker.internal` instead of `localhost` in Docker on Mac/Windows, or your host IP on Linux

**Torrents not saving to correct folder:**
- Verify folder paths in `.env` match your qBittorrent download locations
- Ensure qBittorrent has write permissions to those directories

**Docker-specific issues:**
- Container won't start: Check logs with `docker-compose logs`
- Rebuild image after code changes: `docker-compose up -d --build`
- Reset everything: `docker-compose down && docker-compose up -d --build`

## Dependencies 📦

- `python-telegram-bot` - Telegram Bot API wrapper
- `qbittorrent-api` - qBittorrent Web API client
- `python-dotenv` - Environment variable management
- `requests` - HTTP library

## License 📄

This project is open source and available for personal use.

## Contributing 🤝

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

---

**Enjoy automated torrent management!** 🎉
