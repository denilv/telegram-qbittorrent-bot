import qbittorrentapi
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class QBittorrentClient:
    """Client for interacting with qBittorrent API"""
    
    def __init__(self, url: str, username: str, password: str):
        """
        Initialize qBittorrent client
        
        Args:
            url: qBittorrent Web UI URL (e.g., 'http://localhost:8080')
            username: qBittorrent Web UI username
            password: qBittorrent Web UI password
        """
        self.url = url
        self.username = username
        self.password = password
        self.client: Optional[qbittorrentapi.Client] = None
        
    def connect(self) -> bool:
        """
        Connect to qBittorrent
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.client = qbittorrentapi.Client(
                host=self.url,
                username=self.username,
                password=self.password
            )
            # Test connection
            self.client.auth_log_in()
            logger.info(f"Successfully connected to qBittorrent: {self.client.app.version}")
            return True
        except qbittorrentapi.LoginFailed as e:
            logger.error(f"Failed to login to qBittorrent: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to qBittorrent: {e}")
            return False
    
    def add_torrent_magnet(self, magnet_link: str, save_path: str, category: str = "") -> bool:
        """
        Add a torrent via magnet link
        
        Args:
            magnet_link: Magnet link to add
            save_path: Path where to save the torrent
            category: Category for the torrent
            
        Returns:
            True if torrent added successfully, False otherwise
        """
        if not self.client:
            logger.error("Client not connected")
            return False
            
        try:
            self.client.torrents_add(
                urls=magnet_link,
                save_path=save_path,
                category=category
            )
            logger.info(f"Successfully added magnet link to {save_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to add magnet link: {e}")
            return False
    
    def add_torrent_file(self, torrent_file_path: str, save_path: str, category: str = "") -> bool:
        """
        Add a torrent via .torrent file
        
        Args:
            torrent_file_path: Path to .torrent file
            save_path: Path where to save the torrent
            category: Category for the torrent
            
        Returns:
            True if torrent added successfully, False otherwise
        """
        if not self.client:
            logger.error("Client not connected")
            return False
            
        try:
            with open(torrent_file_path, 'rb') as torrent_file:
                self.client.torrents_add(
                    torrent_files=torrent_file,
                    save_path=save_path,
                    category=category
                )
            logger.info(f"Successfully added torrent file to {save_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to add torrent file: {e}")
            return False
    
    def get_torrents_info(self):
        """Get information about all torrents"""
        if not self.client:
            logger.error("Client not connected")
            return None
            
        try:
            return self.client.torrents_info()
        except Exception as e:
            logger.error(f"Failed to get torrents info: {e}")
            return None
