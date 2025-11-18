# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importação ABSOLUTA em vez de relativa
from routes import router

app = FastAPI(title="To-Do RPG API")

# Permitir comunicação com o React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # depois dá pra restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Servidor do To-Do RPG ativo!"}