from app.services.user_engagement_service import UserEngagementService
from app.services.analytics_event_service import AnalyticsEventService
from app.services.trending_service import TrendingService
from app.services.analytics_engine import AnalyticsEngine
from app.database import get_db


def main():
    print('Testing analytics services...')

    try:
        db = next(get_db())

        # Test UserEngagementService
        engagement_service = UserEngagementService(db)
        print('\u2713 UserEngagementService initialized')

        # Test AnalyticsEventService
        event_service = AnalyticsEventService(db)
        print('\u2713 AnalyticsEventService initialized')

        # Test TrendingService
        trending_service = TrendingService(db)
        print('\u2713 TrendingService initialized')

        # Test AnalyticsEngine
        analytics_engine = AnalyticsEngine(db)
        print('\u2713 AnalyticsEngine initialized')

        print('All analytics services initialized successfully!')

    except Exception as e:
        print(f'Error initializing services: {e}')
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
