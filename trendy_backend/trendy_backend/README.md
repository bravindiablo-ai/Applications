# Trendy Backend - Complete Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Redis 6.0+
- Node.js 16+ (for frontend)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/bravindiablo-ai/FINAL.git
cd FINAL/trendy_backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
python scripts/seed_simple.py
```

6. **Run the server**
```bash
uvicorn app.main:app --reload
```

Server will be available at: `http://localhost:8000`

## 📊 Database Management

### Complete Database Reset

When you need to completely reset the database schema and start fresh:

#### Option 1: Using PostgreSQL CLI
```sql
-- Connect to your PostgreSQL database
psql -U postgres -d trendy_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```

#### Option 2: Using Python (Recommended)
```bash
# Reset and reinitialize the database with SQLAlchemy
python -c "from app.database import Base, engine; Base.metadata.drop_all(engine); Base.metadata.create_all(engine)"
```

#### Option 3: Using provided scripts
```bash
# Complete clean start
python scripts/seed_fixed.py

# This script will:
# 1. Drop all existing tables
# 2. Create fresh schema
# 3. Initialize with test data
```

### Database Operations

```bash
# Create database tables only
python scripts/seed_simple.py

# Seed with complete test data
python scripts/seed_complete.py

# Reset database and reload data
python scripts/seed_fixed.py
```

### Migration Management

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/trendy_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Firebase
FIREBASE_CREDENTIALS_JSON='{...escaped json...}'

# API Keys
TMDB_API_KEY=your_tmdb_api_key
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Other
DEBUG=False
SECRET_KEY=your-secret-key
```

### Firebase Setup

1. Download your Firebase service account key from Firebase Console
2. Convert the JSON to a single-line format with escaped newlines
3. Set `FIREBASE_CREDENTIALS_JSON` in your `.env` file

## 🏃 Running the Application

### Development Mode
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

### Docker
```bash
# Build the image
docker build -t trendy-backend .

# Run the container
docker run -p 8000:8000 --env-file .env trendy-backend
```

### With Docker Compose
```bash
docker-compose up -d
```

## 📚 Documentation

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Database Schema
- ER Diagram: docs/database_schema.png
- Migration Guide: docs/migration_guide.md

## 🛠️ Troubleshooting

### Common Issues

1. **Port already in use:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

2. **Database connection issues:**
```bash
# Check database connection
python -c "from app.database import engine; engine.connect()"
```

3. **Import errors:**
```bash
# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Debug Mode
```bash
# Enable debug mode
export DEBUG=true
python -m uvicorn app.main:app --reload
```

## 📞 Support

For support and questions:
- GitHub Issues: [Create an issue](https://github.com/bravindiablo-ai/FINAL/issues)
- Discord: [Join our Discord](https://discord.gg/your-server)
- Email: support@trendyapp.com

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
