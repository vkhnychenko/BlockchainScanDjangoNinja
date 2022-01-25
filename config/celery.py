import os

import dotenv
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), '.env')
dotenv.load_dotenv(env_file)

app = Celery('tasks')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'new-transaction-notification-every-1-minute': {
        'task': 'wallets.tasks.new_transactions_notification',
        'schedule': 60
    },
    'get-tokens-info-from-1inch-every-1-days': {
        'task': 'wallets.tasks.get_tokens_info',
        'schedule': 14400
    },
}
