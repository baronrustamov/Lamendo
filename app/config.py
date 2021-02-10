DATABASE = 'db/lamendo.db'
SCHEMA = 'db/schema.sql'
INIT_DATA = 'db/data.sql'
IMG_PATH = './static/img_uploads/'
LOG_PATH = './logs/app.log'

ALLOWED_FILETYPES = {'png', 'jpg', 'jpeg', 'gif'}
MAX_MB = 3
MAX_FILE_SIZE = MAX_MB * 1024 * 1024
MIN_POST_LENGTH = 4
MAX_POST_LENGTH = 1_500
MAX_POST_ROWS = 25
EVENT_COOLDOWN = 10


RULES = (
    'You will not upload, post, discuss, request, or link any content that violates your local, or Canadian, law.',
    'You will immediately stop using this site if you are under the age of 18.',
    'You will not post or request personal information about yourself or other users (ie. no \"doxxing\").',
    'High quality content is encouraged, distasteful content may be removed, and may result in a ban.',
    'No spamming, or intentionally evading spam or content submission filters.',
    'Any form of business advertising is not welcome.',
    'The use of scrapers, bots, or other automated posting or downloading scripts is prohibited.',
    'No posting content using proxies or Tor.',
    'No uploading images containing additional data including: embedded sounds, documents, archives, etc.',
    'Exceptions to these rules may be granted for testing purposes.',
)


REPORTS = [
    'Very low quality or distasteful content.',
    'Violation of law.',
    'Personal information is being doxxed.',
    'Business advertising.',
    'Spam.',
    'Something is broken.',
    'Other.',
]


FEEDBACK_MSG = 'Thank you for your feedback!'
POST_MSG = 'Post submitted!'
REPLY_MSG = 'Reply submitted!'
REPORT_MSG = 'Report submitted.'
BANNED_MSG = 'Cannot post. Your IP address has been banned.'
COOLDOWN_MSG = 'Wait at least 15 seconds before posting again.'
