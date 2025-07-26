from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from .config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG,
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Test database configuration
if settings.TEST_DATABASE_URL:
    test_engine = create_engine(
        settings.TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False} if "sqlite" in settings.TEST_DATABASE_URL else {},
    )
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    def get_test_db():
        """Dependency to get test database session"""
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()
else:
    test_engine = None
    TestSessionLocal = None
    get_test_db = None