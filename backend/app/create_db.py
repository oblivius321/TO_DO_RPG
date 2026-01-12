from database import Base, engine
import models  # noqa: F401 garante que os modelos sejam registrados

print("🧙 Criando tabelas no banco de dados...")
Base.metadata.create_all(bind=engine)
print("✅ Banco de dados criado com sucesso!")