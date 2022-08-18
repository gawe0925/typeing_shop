import os
from celery import Celery
from django.conf import settings

# 設定環境變數
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ty.settings')

# 範例化
celery_app = Celery('ty')

# namespace='CELERY'作用是允許你在Django組態檔中對Celery進行設定
# 但所有Celery設定項必須以CELERY開頭，防止衝突
celery_app.config_from_object('django.conf:settings', namespace='CELERY')

# 自動從Django的已註冊app中發現任務
celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# 一個測試任務
@celery_app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')