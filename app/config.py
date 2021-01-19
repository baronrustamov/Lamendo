DATABASE = 'db/sqlite_img_board_db.db'
SCHEMA = 'db/init_schema.sql'
INIT_DATA = 'db/init_data.sql'
IMG_PATH = './static/img_uploads/'
LOG_PATH = './logs/app.log'

ALLOWED_FILETYPES = {'png', 'jpg', 'jpeg', 'gif'}
MAX_MB = 3
MAX_FILE_SIZE = MAX_MB * 1024 * 1024
MIN_POST_LENGTH = 4
MAX_POST_LENGTH = 1_000
EVENT_COOLDOWN = 10
