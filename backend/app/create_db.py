from models import User, Task
from database import engine, Base

print("🧙 Criando tabelas no banco de dados...")
Base.metadata.create_all(bind=engine)
print("✅ Banco de dados criado com sucesso!")