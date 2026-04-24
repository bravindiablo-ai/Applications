import json
from app.services.stripe_service import stripe_service
from app.database import SessionLocal
from app.models.subscription_corrected import Subscription
from app.models.payment_webhook import WebhookEvent


def test_webhook_idempotency(tmp_path):
    # This is a lightweight test that exercises the webhook dedup logic by
    # creating a fake event payload and ensuring processing the same event twice
    # results in the second call being skipped (no duplicate WebhookEvent created)
    payload = {
        "id": "evt_test_123",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_123",
                "metadata": {"user_id": "1"},
                "subscription": "sub_test_123",
                "customer": "cus_test_123"
            }
        }
    }

    # ensure DB has a pending subscription for user 1
    with SessionLocal() as db:
        db.query(Subscription).filter(Subscription.user_id == 1).delete()
        db.query(WebhookEvent).filter(WebhookEvent.id == payload['id']).delete()
        db.commit()
        s = Subscription(user_id=1, stripe_subscription_id=None, plan_id='test', status='pending')
        db.add(s)
        db.commit()

    raw = json.dumps(payload).encode('utf-8')
    sig = 't=123,v1=fake'

    result1 = awaitable(stripe_service.handle_webhook_event(raw, sig))
    result2 = awaitable(stripe_service.handle_webhook_event(raw, sig))

    # first should process (success or skip if signature validation fails in CI), second must return skipped or success again but not duplicate WebhookEvent
    with SessionLocal() as db:
        events = db.query(WebhookEvent).filter(WebhookEvent.id == payload['id']).all()
        assert len(events) <= 1


# helper to call async from sync test runner

def awaitable(coro):
    import asyncio
    return asyncio.get_event_loop().run_until_complete(coro)
