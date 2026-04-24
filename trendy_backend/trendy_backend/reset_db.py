from app.db.base import Base
from app.db.session import engine
from sqlalchemy import inspect

inspector = inspect(engine)
if inspector.has_table('users'):
    print('Tables exist, skipping creation')
else:
    Base.metadata.create_all(bind=engine)
    print('Tables created successfully')
