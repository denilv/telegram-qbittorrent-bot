import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from dotenv import load_dotenv
from qbittorrent_client import QBittorrentClient
import tempfile

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize qBittorrent client
qb_client = QBittorrentClient(
    url=os.getenv('QBITTORRENT_URL'),
    username=os.getenv('QBITTORRENT_USERNAME'),
    password=os.getenv('QBITTORRENT_PASSWORD')
)

# Storage folders from environment
MOVIES_FOLDER = os.getenv('MOVIES_FOLDER')
TV_SHOWS_FOLDER = os.getenv('TV_SHOWS_FOLDER')

# User context for storing pending torrents
user_pending_torrents = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = (
        "🎬 Welcome to Torrent Bot!\n\n"
        "I can help you download torrents using qBittorrent.\n\n"
        "📝 What I can do:\n"
        "• Add magnet links\n"
        "• Add .torrent files\n"
        "• Organize downloads into Movies or TV Shows folders\n\n"
        "🚀 Just send me a magnet link or a .torrent file to get started!"
    )
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    help_text = (
        "ℹ️ How to use this bot:\n\n"
        "1️⃣ Send a magnet link or upload a .torrent file\n"
        "2️⃣ Choose whether it's a Movie or TV Show\n"
        "3️⃣ I'll add it to qBittorrent for you!\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/status - Check qBittorrent connection status"
    )
    await update.message.reply_text(help_text)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check qBittorrent connection status."""
    if qb_client.connect():
        torrents = qb_client.get_torrents_info()
        if not torrents:
            status_message = "✅ Connected to qBittorrent\n📊 No active torrents"
        else:
            torrent_count = len(torrents)
            
            # Sort by added_on date (most recent first) and get last 5
            sorted_torrents = sorted(torrents, key=lambda x: x.get('added_on', 0), reverse=True)
            last_five = sorted_torrents[:5]
            
            status_message = f"✅ Connected to qBittorrent\n📊 Total torrents: {torrent_count}\n\n"
            status_message += "📥 Last 5 Added Torrents:\n"
            status_message += "━━━━━━━━━━━━━━━━━━━━\n\n"
            
            for idx, torrent in enumerate(last_five, 1):
                name = torrent.name[:40] + "..." if len(torrent.name) > 40 else torrent.name
                progress = torrent.progress * 100
                dl_speed = torrent.dlspeed / 1024 / 1024  # Convert to MB/s
                up_speed = torrent.upspeed / 1024 / 1024  # Convert to MB/s
                uploaded = torrent.uploaded / 1024 / 1024 / 1024  # Convert to GB
                state = torrent.state
                
                # State emoji
                state_emoji = {
                    'downloading': '⬇️',
                    'uploading': '⬆️',
                    'stalledDL': '⏸️',
                    'stalledUP': '⏸️',
                    'pausedDL': '⏸️',
                    'pausedUP': '⏸️',
                    'queuedDL': '⏳',
                    'queuedUP': '⏳',
                    'checkingDL': '🔍',
                    'checkingUP': '🔍',
                    'error': '❌',
                    'missingFiles': '❌',
                    'allocating': '💾',
                }.get(state, '📦')
                
                status_message += f"{idx}. {state_emoji} {name}\n"
                status_message += f"   Progress: {progress:.1f}%\n"
                status_message += f"   ⬇️ {dl_speed:.2f} MB/s  ⬆️ {up_speed:.2f} MB/s\n"
                status_message += f"   📤 Uploaded: {uploaded:.2f} GB\n"
                status_message += f"   Category: {torrent.category or 'None'}\n\n"
    else:
        status_message = "❌ Failed to connect to qBittorrent. Please check your configuration."
    
    await update.message.reply_text(status_message)


async def handle_magnet_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle magnet links sent by users."""
    magnet_link = update.message.text
    
    # Validate magnet link
    if not magnet_link.startswith('magnet:?'):
        await update.message.reply_text("❌ Invalid magnet link. Please send a valid magnet link.")
        return
    
    # Store the magnet link for the user
    user_id = update.effective_user.id
    user_pending_torrents[user_id] = {
        'type': 'magnet',
        'content': magnet_link
    }
    
    # Ask user to choose folder
    keyboard = [
        [
            InlineKeyboardButton("🎬 Movies", callback_data='folder_movies'),
            InlineKeyboardButton("📺 TV Shows", callback_data='folder_tvshows')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📁 Where should I save this torrent?",
        reply_markup=reply_markup
    )


async def handle_torrent_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle .torrent files sent by users."""
    # Get the file
    file = await update.message.document.get_file()
    
    # Validate file extension
    if not update.message.document.file_name.endswith('.torrent'):
        await update.message.reply_text("❌ Please send a valid .torrent file.")
        return
    
    # Download file to temporary location
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, update.message.document.file_name)
    await file.download_to_drive(file_path)
    
    # Store the file path for the user
    user_id = update.effective_user.id
    user_pending_torrents[user_id] = {
        'type': 'file',
        'content': file_path
    }
    
    # Ask user to choose folder
    keyboard = [
        [
            InlineKeyboardButton("🎬 Movies", callback_data='folder_movies'),
            InlineKeyboardButton("📺 TV Shows", callback_data='folder_tvshows')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "📁 Where should I save this torrent?",
        reply_markup=reply_markup
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks for folder selection."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Check if user has a pending torrent
    if user_id not in user_pending_torrents:
        await query.edit_message_text("❌ No pending torrent found. Please send a new torrent.")
        return
    
    torrent_data = user_pending_torrents[user_id]
    
    # Determine save path based on selection
    if query.data == 'folder_movies':
        save_path = MOVIES_FOLDER
        category = "Movies"
        folder_name = "🎬 Movies"
    elif query.data == 'folder_tvshows':
        save_path = TV_SHOWS_FOLDER
        category = "TV Shows"
        folder_name = "📺 TV Shows"
    else:
        await query.edit_message_text("❌ Invalid selection.")
        return
    
    # Connect to qBittorrent
    if not qb_client.connect():
        await query.edit_message_text("❌ Failed to connect to qBittorrent. Please try again later.")
        return
    
    # Add torrent based on type
    success = False
    if torrent_data['type'] == 'magnet':
        success = qb_client.add_torrent_magnet(
            magnet_link=torrent_data['content'],
            save_path=save_path,
            category=category
        )
    elif torrent_data['type'] == 'file':
        success = qb_client.add_torrent_file(
            torrent_file_path=torrent_data['content'],
            save_path=save_path,
            category=category
        )
        # Clean up temporary file
        try:
            os.remove(torrent_data['content'])
        except:
            pass
    
    # Send result to user
    if success:
        await query.edit_message_text(
            f"✅ Torrent added successfully!\n"
            f"📁 Category: {folder_name}\n"
            f"💾 Save path: {save_path}"
        )
    else:
        await query.edit_message_text("❌ Failed to add torrent. Please check the logs.")
    
    # Clean up pending torrent
    del user_pending_torrents[user_id]


def main():
    """Start the bot."""
    # Get bot token from environment
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        return
    
    # Create the Application
    application = Application.builder().token(token).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    
    # Handle magnet links (text messages starting with "magnet:")
    application.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r'^magnet:\?'),
        handle_magnet_link
    ))
    
    # Handle .torrent files
    application.add_handler(MessageHandler(
        filters.Document.ALL,
        handle_torrent_file
    ))
    
    # Handle button callbacks
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Log startup
    logger.info("Starting Telegram Torrent Bot...")
    
    # Test qBittorrent connection
    if qb_client.connect():
        logger.info("Successfully connected to qBittorrent")
    else:
        logger.warning("Failed to connect to qBittorrent on startup")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
