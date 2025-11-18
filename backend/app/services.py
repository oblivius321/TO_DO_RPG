LEVELS = [
    {"min": 1,   "max": 15,  "xp": 100, "title": "Novato"},
    {"min": 16,  "max": 20,  "xp": 150, "title": "Aprendiz"},
    {"min": 21,  "max": 30,  "xp": 200, "title": "Guerreiro"},
    {"min": 31,  "max": 50,  "xp": 250, "title": "Mestre"},
    {"min": 51,  "max": 70,  "xp": 300, "title": "Grão Mestre"},
    {"min": 71,  "max": 100, "xp": 500, "title": "Deus"},
]

MAX_LEVEL = 100

def get_xp_for_level(level):
    for lvl in LEVELS:
        if lvl["min"] <= level <= lvl["max"]:
            return lvl["xp"]
    return 500  

def get_title_for_level(level):
    for lvl in LEVELS:
        if lvl["min"] <= level <= lvl["max"]:
            return lvl["title"]
    return "Deus"

def add_xp(user, xp_amount, tarefas_completas):
    """
    Adiciona XP ao usuário se ele completou todas as tarefas do dia.
    Retorna mensagem sobre progresso ou nível máximo.
    """
    if not tarefas_completas:
        return "Você não completou todas as tarefas de hoje."

    user.xp += xp_amount

    while user.level < MAX_LEVEL and user.xp >= get_xp_for_level(user.level):
        xp_para_subir = get_xp_for_level(user.level)
        user.xp -= xp_para_subir
        user.level += 1

    if user.level >= MAX_LEVEL:
        user.level = MAX_LEVEL
        user.xp = 0
        return "Você alcançou o nível máximo! deus!"

    return f"XP atual: {user.xp} | Nível: {user.level}"
