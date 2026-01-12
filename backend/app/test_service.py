from services import apply_xp, get_title_for_level


class DummyUser:
    def __init__(self, level: int = 1, current_xp: int = 0, total_xp: int = 0):
        self.level = level
        self.current_xp = current_xp
        self.total_xp = total_xp
        self.title = get_title_for_level(level)


user = DummyUser()

xp_entries = [120, 150, 200, 250, 300, 400, 500, 600]

for day_index, xp_gain in enumerate(xp_entries, start=1):
    result = apply_xp(user, xp_gain)
    user.title = result["title"]
    print(f"----- DIA {day_index} -----")
    print(
        f"XP ganho: {result['xp_awarded']} | XP atual: {result['current_xp']} | "
        f"Nível: {result['level']} | Level ups: {result['level_ups']}"
    )
    print(f"Título: {user.title} | XP total acumulado: {user.total_xp}")
    print()
