"""
File: gunicorn.conf.py

Mục đích:
Gunicorn configuration file cho production deployment

Lưu ý: File này được load bởi Gunicorn trước khi Flask app được khởi tạo,
nên cần cẩn thận khi import Config. Sử dụng fallback về os.getenv() nếu cần.
"""
import multiprocessing
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import Config, fallback to os.getenv if not available
try:
    from config import Config
    LOG_LEVEL = Config.LOG_LEVEL
except (ImportError, AttributeError):
    # Fallback nếu Config chưa được load hoặc không có LOG_LEVEL
    LOG_LEVEL = os.getenv("LOG_LEVEL", "info")

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = LOG_LEVEL
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "bookstore_backend"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Graceful timeout
graceful_timeout = 30

# Enable preload app for better performance
preload_app = True

