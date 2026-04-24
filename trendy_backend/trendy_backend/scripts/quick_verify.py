# Quick verification script: import core modules and call health_check
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import main
from app.db.base import Base
from app.database import engine

print('Imported app.main, Base, engine')
# Verify metadata has tables
tables = Base.metadata.tables.keys()
print('Registered tables count:', len(tables))
# Call health_check
import asyncio
result = asyncio.run(main.health_check())
print('health_check result:', result)
