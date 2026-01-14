import os
import sys
import random

# Список стартовых артефактов
START_ARTIFACTS = [
    "🗡 Меч ночи и пламени",
    "🪓 Боевой Топор Грома",
    "🏹 Львиный большой лук",
    "🔪 Клык ищейки",
    "🔮 Адский посох прелата"
]
# Список артефактов босса
BOSS_ARTIFACTS = [
    "🛡 Комплект Малении",
    "💍 Талисман овцебыка",
    "🩸 Реки крови",
    "⚔️ Редувия",
    "🌑 Комета Азура",
    "🔨 Золотая алебарда",
    "👑 Знак Радагона",
    "🪦 Пепел Войны"
]
ARTIFACT_POOL_FILE = "artifact_pool.txt"  # Файл с набором артефактов
USER_FILE = "players.txt"  # Файл с игроками
RESULT_FILE = "game_log.txt"  # Файл с логом игр


class ArtifactPool:
    """Класс для управления набором артефактов."""

    def __init__(self, filename: str):
        """
        Создает экземпляр набора артефактов.

        filename (str): Имя файла с артефактами.
        """
        self.filename = filename
        if not os.path.exists(self.filename):  # Если файл не существует, сгенерировать новый набор
            self.regenerate()
        self.artifacts = self.load()

    def load(self) -> list[str]:
        """Загружает артефакты из файла."""
        if not os.path.exists(self.filename):
            self.regenerate()
        with open(self.filename, 'r', encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    def save(self) -> None:
        """Сохраняет текущий набор артефактов в файл."""
        with open(self.filename, 'w', encoding="utf-8") as f:
            for artifact in self.artifacts:
                f.write(artifact + '\n')

    def put_back(self, artifact: str) -> None:
        """Возвращает артефакт обратно в набор, если его нет."""
        if artifact and artifact not in self.artifacts:
            self.artifacts.append(artifact)
            self.save()

    def remove(self, artifact: str) -> None:
        """Удаляет артефакт из набора."""
        if artifact in self.artifacts:
            self.artifacts.remove(artifact)
            self.save()

    def get_random(self) -> str | None:
        """Берёт случайный артефакт из набора."""
        if not self.artifacts:
            return None
        artifact = random.choice(self.artifacts)
        self.remove(artifact)
        return artifact

    def add(self, artifact: str) -> None:
        """Добавляет новый артефакт в набор, если его нет."""
        if artifact and artifact not in self.artifacts:
            self.artifacts.append(artifact)
            self.save()

    def regenerate(self) -> None:
        """Восстанавливает набор артефактов до изначального состояния."""
        self.artifacts = START_ARTIFACTS + BOSS_ARTIFACTS
        self.save()

class Player:
    """Класс для игрока."""

    def __init__(self, login: str, password: str):
        """Создать игрока с логином, паролем, артефактами и историей посещений."""
        self.login = login
        self.password = password
        self.artifacts: list[str] = []
        self.visited: set[str] = set()
        self.collect_history: list[str] = []
        self.load()

    @staticmethod
    def authenticate() -> "Player":
        """Аутентификация игрока. При отсутствии аккаунта создаёт новый."""
        login = input("Введите логин: ").strip()
        password = input("Введите пароль: ").strip()
        if os.path.exists(USER_FILE):
            with open(USER_FILE, "r", encoding="utf-8") as uf:
                for line in uf:
                    ln, pw, artlist = (line.strip().split("|") + [""])[:3]
                    if ln == login and pw == password:
                        print("Вход выполнен.")
                        player = Player(login, password)
                        player.artifacts = artlist.split(";") if artlist else []
                        return player
        print("Создан новый аккаунт.")
        return Player(login, password)


    def save(self) -> None:
        """Сохраняет состояние игрока в файл."""
        lines = []
        updated = False
        if os.path.exists(USER_FILE):
            with open(USER_FILE, "r", encoding="utf-8") as uf:
                for line in uf:
                    ln, pw, *rest = line.strip().split("|")
                    if ln == self.login:
                        new_line = f"{self.login}|{self.password}|{';'.join(self.artifacts)}\n"
                        lines.append(new_line)
                        updated = True
                    else:
                        lines.append(line)
        if not updated:
            lines.append(f"{self.login}|{self.password}|{';'.join(self.artifacts)}\n")
        with open(USER_FILE, "w", encoding="utf-8") as uf:
            uf.writelines(lines)
        print("💾 Прогресс сохранён.")

    def load(self) -> None:
        """Загружает прогресс игрока из файла."""
        if not os.path.exists(USER_FILE):
            return
        with open(USER_FILE, "r", encoding="utf-8") as uf:
            for line in uf:
                ln, pw, *rest = line.strip().split("|")
                if ln == self.login and pw == self.password:
                    self.artifacts = (rest[0].split(";") if rest and rest[0] else [])
                    return

    def lose_all_artifacts(self, pool: ArtifactPool) -> None:
        """Игрок теряет все артефакты, возвращая их в набор."""
        for art in self.artifacts:
            pool.put_back(art)
        self.artifacts = []

    def add_artifact(self, artifact: str) -> None:
        """Добавляет артефакт игроку."""
        if artifact and artifact not in self.artifacts:
            self.artifacts.append(artifact)

    def remove_artifact(self, artifact: str) -> None:
        """Удаляет артефакт у игрока."""
        if artifact in self.artifacts:
            self.artifacts.remove(artifact)

    def has_all(self, pool: ArtifactPool) -> bool:
        """Проверяет, собрал ли игрок все артефакты."""
        return sorted(self.artifacts) == sorted(START_ARTIFACTS + BOSS_ARTIFACTS)

    def __repr__(self) -> str:
        return f"Игрок {self.login}: {self.artifacts}"

class Game:
    """Класс для управления основной логикой игры."""

    def __init__(self):
        """Создаёт экземпляр игры."""
        self.player: Player | None = None
        self.pool: ArtifactPool = ArtifactPool(ARTIFACT_POOL_FILE)
        self.BOSS_ARTIFACTS: list[str] = list(BOSS_ARTIFACTS)
        self.moves: list[str] = []

    def run(self) -> None:
        """Основной цикл запуска и завершения игры."""
        self.player = Player.authenticate()
        if not self.player.artifacts:
            got = self.pool.get_random()
            if got:
                print(f"👤 Вы у места благодати и находите: {got}")
                self.player.add_artifact(got)
        self.moves = []
        while True:
            if self.player.has_all(self.pool):
                print("🔥 Все артефакты у игрока! Генерирую новые...")
                self.pool.regenerate()
                self.player.artifacts = []
                print("Копилка обновлена. Продолжаем...")
            self.game_loop()
            save_ans = input("💾 Сохранить прогресс? (да/нет): ").strip().lower()
            if save_ans == "да":
                self.player.save()
                print("🔥 Спасибо за игру!")
                break
            else:
                self.player.lose_all_artifacts(self.pool)
                print("⚰️ Прогресс не сохранён. Артефакты отправлены в копилку. До свидания!")
                break

    def log(self, message: str) -> None:
        """Записывает ход игры."""
        self.moves.append(message)

    def save_game_log(self, result: str) -> None:
        """
        Сохраняет лог игры вместе с результатом.

        result (str): строка с текстом результата (победа/проигрыш)
        """
        with open(RESULT_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n--- Новая игра ({self.player.login}) ---\n")
            for move in self.moves:
                f.write(move + "\n")
            f.write("Результат: " + result + "\n")


    def game_loop(self) -> None:
        """Один игровой проход - цикл принятия решений."""
        self.player.visited = set()
        self.player.collect_history = []
        print("💍 ТЫ В МЕЖДУЗЕМЬЕ 💍")
        self.log("Начало игры.")
        print("🔥 Вы находитесь в Месте Благодати\n",
            'На севере Замок Грозовой Завесы, на юге Медвежий Лес ')
        d = input("Введите 'север' или 'юг': ").strip().lower()
        self.log(f"Выбор направления: {d}")

        if d == "север":
            self.castle_with_boss()
            return
        if d == "юг":
            self.scene_forest()
            return

        print("🆘 Неверный выбор, игра заканчивается.")
        self.log("Ошибка выбора направления.")
        self.save_game_log("Проигрыш: неверный выбор.")

    def castle_with_boss(self) -> None:
        """Сцена - поход к замку и выбор: войти к боссу или нет."""
        self.player.visited.add("Поход к замку.")
        print("Вы подошли к замку. Перед вами большие ворота. За ними босс.")
        ch = input("Войти в ворота? (да/нет): ").strip().lower()
        self.log(f"Вход к боссу: {ch}")
        if ch == "да":
            self.battle_with_boss()
            return
        if ch == "нет":
            if self.player.artifacts:
                self.pool.put_back(self.player.artifacts[-1])
            msg = "🛏 Вы отказались от битвы с боссом. Отдыхайте!"
            self.log(msg)
            self.save_game_log(msg)
            print(msg)
            return

        print("🆘 Неверный выбор. Игра завершена.")
        self.save_game_log("Проигрыш: неверный выбор.")

    def scene_forest(self) -> None:
        """Сцена - Медвежий Лес. Игрок решает, подходить к волку или идти мимо."""
        self.player.visited.add("Медвежий лес")
        print("🏞 В Медвежьем лесу вы видите волка на двух ногах, в плаще и с мечом.")
        ch = input("Подойти или пройти мимо? (подойти/мимо): ").strip().lower()
        self.log(f"Встреча с волком: {ch}")
        if ch == "подойти":
            self.scene_wolf()
            return
        if ch == "мимо":
            if self.player.artifacts:
                self.pool.put_back(self.player.artifacts[-1])
            msg = "👍 Ничего не произошло, вы вернулись к началу."
            self.log(msg)
            self.save_game_log(msg)
            print(msg)
            return

        print("🆘 Неверный выбор. Игра завершена.")
        self.save_game_log("Проигрыш: неверный выбор.")

    def scene_wolf(self) -> None:
        """Сцена - встреча с волком, принять загадку или отказаться."""
        self.player.visited.add("Встреча с волком")
        print("🐺 Волк оказался дружелюбным и предложил вам решить загадку.")
        ch = input("Вы принимаете решение (согласиться/отказаться): ").strip().lower()
        self.log(f"Выбор у эльфов: {ch}")
        if ch == "согласиться":
            self.riddle_of_the_wolf()
            return
        if ch == "отказаться":
            msg = "Волк кивнул головой и исчез. Интересно, что будет если согласиться? "
            if self.player.artifacts:
                self.pool.put_back(self.player.artifacts[-1])
            self.log(msg)
            self.save_game_log(msg)
            print(msg)
            return
        print("🆘 Неверный выбор. Игра завершена.")
        self.save_game_log("Проигрыш: неверный выбор.")


    def riddle_of_the_wolf(self) -> None:
        """Сцена - решение загадки от волка (угадывание числа)."""
        self.player.visited.add("Загадка от волка")
        print("Загадка: Какой балл надо поставить за эту работу?")
        code = "100"
        success = False
        for tries in range(5, 0, -1):
            user_code = input(f"Подумайте лучше, у вас {tries} попыток: ")
            self.log(f"Ответ: {user_code}")
            if user_code == code:
                print("🥳🥳🥳Поздравляю, вы ответили верно. Только не забудьте поставить сам балл.")
                success = True
                break
            else:
                print("Неверно...")
        if not success:
            if self.player.artifacts:
                self.pool.put_back(self.player.artifacts[-1])
            msg = "💀 За неверные ответы вам отрубили голову, в следующий раз надо думать лучше."
            self.log(msg)
            self.save_game_log(msg)
            print(msg)
            return
        self.gift()

    def battle_with_boss(self) -> None:
        """Сцена - битва с боссом, имитация игры на выбор."""
        self.player.visited.add("Битва с боссом")
        print("🧌 Вы вошли и перед вами босс Маргит, Ужасное Знамение\n",
            "🧌 Битва с Маргитом: победите - получите артефакт, проиграете - он заберёт ваш.")
        choices = ["сила", "ловкость", "магия"]
        user = input("Выберите (сила/ловкость/магия): ").strip().lower()
        if user not in choices:
            print("Неверный выбор. Игра завершена.")
            self.save_game_log("Проигрыш: неверный выбор.")
            return
        self.log(f"Игрок: {user}")
        boss = random.choice(choices)
        print(f"Маргит выбрал: {boss}")
        self.log(f"Маргит: {boss}")
        win = ((user == "сила" and boss == "ловкость") or
                (user == "ловкость" and boss == "магия") or
                (user == "магия" and boss == "сила"))
        if user == boss:
            print("Ничья. Попробуйте снова.")
            self.battle_with_boss()
            return
        if win:
            print("🔥 Вы победили Маргота!")
            self.log("🔥 Победа над Мароготом.")
            self.gift()
            msg = "Игра завершена (победа над Марготом)."
            self.save_game_log(msg)
            print(msg)
            return
        else:
            print("💀 Вы умерли! Маргот забрал ваш артефакт.")
            if self.player.artifacts:
                lost = self.player.artifacts[-1]
                self.player.remove_artifact(lost)
                self.pool.put_back(lost)
                self.log(f"Артефакт {lost} перемещён обратно в копилку.")
            msg = "Игра завершена: проигрыш Марготу."
            self.save_game_log(msg)
            print(msg)
            return

    def gift(self) -> None:
        """Выдаёт игроку артефакт за победу (или загадку/сцену)."""
        available = [a for a in self.pool.artifacts if a not in self.player.artifacts]
        if not available:
            print("Пока что в копилке нет новых артефактов.")
            return
        print("Выберите артефакт:")
        for i, item in enumerate(available, 1):
            print(f"{i}. {item}")
        try:
            ch = int(input("Введите номер выбранного артефакта: "))
            if 1 <= ch <= len(available):
                prize = available[ch - 1]
                self.player.add_artifact(prize)
                # удаляем выданный артефакт из пула
                self.pool.remove(prize)
                print(f"😎 Вы получили артефакт: {prize}! Ты крут")
                self.log(f"Выбран артефакт: {prize}")
            else:
                print("Некорректный выбор. Артефакт не выдан.")
        except Exception:
            print("Некорректный ввод. Артефакт не выдан.")


if __name__ == '__main__':
    g = Game()
    g.run()