# Simple migration that creates trends and trending_categories tables via SQLAlchemy metadata
from app.database import engine, Base
from app.models.trend import Trend, TrendingCategory

def upgrade():
    Base.metadata.create_all(bind=engine, tables=[Trend.__table__, TrendingCategory.__table__])
    print("Trend tables created")

def downgrade():
    Trend.__table__.drop(bind=engine, checkfirst=True)
    TrendingCategory.__table__.drop(bind=engine, checkfirst=True)
    print("Trend tables dropped")

if __name__ == "__main__":
    upgrade()