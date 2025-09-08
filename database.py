from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

SQLALCHEMY_DATABASE_URL = "postgresql://ksmcnns:Ks.31213000@localhost:5433/shartflixdb"  # Kendi bilgilerini gir!
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Blacklist tablosu (token iptali için)
class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(500), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Bağımlılık enjeksiyonu için DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()