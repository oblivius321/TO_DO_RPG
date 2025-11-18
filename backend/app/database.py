from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base

# Caminho pro arquivo do banco
DATABASE_URL = "sqlite:///./todo_rpg.db"

# Cria a engine (responsável pela conexão)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Gerencia sessões (pra consultas e alterações)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para nossos modelos
Base = declarative_base()
