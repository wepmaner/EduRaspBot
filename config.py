import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Токен Telegram бота
token_1 = os.getenv('BOT_TOKEN')

# Настройки базы данных MySQL
host = os.getenv('DB_HOST')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')
db_port = int(os.getenv('DB_PORT'))

# Настройки логирования
log_level = os.getenv('LOG_LEVEL', 'INFO')

# Интервал обновления кеша в секундах
cache_update_interval = int(os.getenv('CACHE_UPDATE_INTERVAL', '3600'))
