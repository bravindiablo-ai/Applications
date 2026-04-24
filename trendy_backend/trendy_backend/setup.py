from setuptools import setup, find_packages

setup(
    name="trendy-backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy",
        "alembic",
        "pydantic",
        "pydantic-settings",
        "python-jose[cryptography]",
        "bcrypt",
        "cryptography",
        "fastapi",
        "uvicorn",
        "python-dotenv",
        "python-multipart",
        "redis",
        "aioredis",
        "openai",
        "sqlalchemy-utils",
        "pytest",
        "pytest-asyncio",
    ],
)