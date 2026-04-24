# Development helper: import models then create all tables
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.db.base import Base
from app.database import engine
# import models to ensure they're registered with Base
import app.models.analytics_event
import app.models.trend
import app.models.trends
import app.models.subscription_corrected
import app.models.reward
import app.models.moderation
import app.models.payment_webhook

print('Creating DB tables from models...')
Base.metadata.create_all(bind=engine)
print('Done')
