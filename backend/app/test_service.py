from services import add_xp, get_title_for_level

class User:
    def __init__(self, level=1, xp=0):
        self.level = level
        self.xp = xp

user = User(level=1, xp=0)

# XP ganho por dia aumentado para forçar evolução de título
dias = [120, 150, 200, 250, 300, 400, 500, 600]

for i, xp_ganho in enumerate(dias, start=1):
    resultado = add_xp(user, xp_ganho, tarefas_completas=True)
    titulo = get_title_for_level(user.level)
    print(f"----- DIA {i} -----")
    print(resultado)
    print(f"Nível atual: {user.level} | XP: {user.xp} | Título: {titulo}")
    print()
