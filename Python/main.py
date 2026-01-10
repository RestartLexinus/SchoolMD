import pygame
import sys
# Инициализация PyGame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLUE = (0, 120, 255)
GREEN = (0, 180, 0)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
PURPLE = (180, 0, 180)

# ========================================

# 1. СЛОВАРЬ ПРЕДМЕТОВ (что собирает игрок)
ITEM_COLORS = {
    "coin": YELLOW,
    "gem": PURPLE,
    "bonus": RED,
    "key": WHITE
}

# 2. СЛОВАРЬ УРОВНЕЙ (платформы и предметы)
LEVELS = {
    1: {
        "platforms": [
            (20, 355, 50, 20),
            (100, 300, 100, 20),
            (100, 500, 200, 20),
            (350, 400, 150, 20),
            (550, 300, 300, 20),
            (200, 200, 300, 20),
            (100, 75, 300, 20)
        ],
        "items": [
            {"type": "coin", "x": 150, "y": 235},
            {"type": "coin", "x": 400, "y": 300},
            {"type": "gem", "x": 600, "y": 250},
            {"type": "bonus", "x": 255, "y": 20}
        ],
        "start_pos": (100, 300)
    },
    2: {
        "platforms": [
            (0, 450, 150, 20),
            (250, 400, 150, 20),
            (450, 350, 150, 20),
            (300, 250, 200, 20),
            (100, 200, 150, 20),
            (500, 150, 150, 20)
        ],
        "items": [
            {"type": "coin", "x": 100, "y": 400},
            {"type": "gem", "x": 300, "y": 350},
            {"type": "coin", "x": 500, "y": 300},
            {"type": "key", "x": 350, "y": 200},
            {"type": "bonus", "x": 150, "y": 150}
        ],
        "start_pos": (50, 350)
    }
}


# 3. ФУНКЦИЯ ДЛЯ ОБРАБОТКИ ПРЕДМЕТОВ
def handle_item_collection(item_type, player):
    """Функция определяет, что происходит при сборе предмета"""
    score_values = {
        "coin": 10,
        "gem": 50,
        "bonus": 100,
        "key": 30
    }

    # Добавляем очки
    player.score += score_values.get(item_type, 0)

    # Специальные эффекты для некоторых предметов
    if item_type == "bonus":
        player.speed += 1  # Увеличиваем скорость
    elif item_type == "key":
        player.jump_power = -18  # Увеличиваем прыжок

    # Запоминаем собранный предмет
    player.collected_items.append(item_type)

    # Можно добавить звуковые эффекты (заглушка)
    print(f"Собран: {item_type}! Счет: {player.score}")


# ========================================

# Создание окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Dictionary Platformer")
clock = pygame.time.Clock()


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.vel_y = 0
        self.jump_power = -15
        self.speed = 5
        self.on_ground = False
        self.score = 0
        self.collected_items = []

    def draw(self):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))
        pygame.draw.circle(screen, WHITE, (self.x + 10, self.y + 15), 5)
        pygame.draw.circle(screen, WHITE, (self.x + 30, self.y + 15), 5)

    def update(self, platforms):
        # Гравитация
        self.vel_y += 0.8
        self.y += self.vel_y

        # Проверка платформ
        self.on_ground = False
        for platform in platforms:
            if (self.x + self.width > platform[0] and
                    self.x < platform[0] + platform[2] and
                    self.y + self.height > platform[1] and
                    self.y + self.height < platform[1] + 20):
                self.y = platform[1] - self.height
                self.vel_y = 0
                self.on_ground = True

        # Границы экрана
        if self.y > HEIGHT - self.height:
            self.y = HEIGHT - self.height
            self.vel_y = 0
            self.on_ground = True

        if self.x < 0:
            self.x = 0
        if self.x > WIDTH - self.width:
            self.x = WIDTH - self.width

    def jump(self):
        if self.on_ground:
            self.vel_y = self.jump_power

    def move(self, direction):
        self.x += direction * self.speed

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Item:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.type = item_type
        self.width = 30
        self.height = 30

    def draw(self):
        # Цвет предмета определяется в словаре ITEM_COLORS
        color = ITEM_COLORS.get(self.type, WHITE)
        pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height))

        # Специальные эффекты для разных типов
        if self.type == "bonus":
            pygame.draw.circle(screen, YELLOW, (self.x + 15, self.y + 15), 10)
        elif self.type == "key":
            pygame.draw.rect(screen, WHITE, (self.x + 10, self.y + 5, 10, 20))
            pygame.draw.circle(screen, WHITE, (self.x + 15, self.y + 10), 8)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)



def draw_text(text, size, color, x, y):
    font = pygame.font.SysFont(None, size)
    render = font.render(text, True, color)
    screen.blit(render, (x, y))


def main():
    current_level = 1
    level_data = LEVELS[current_level]

    player = Player(*level_data["start_pos"])

    # Создаем платформы
    platforms = level_data["platforms"]

    # Создаем предметы из словаря уровня
    items = []
    for item_data in level_data["items"]:
        items.append(Item(item_data["x"], item_data["y"], item_data["type"]))

    running = True

    while running:
        screen.fill((30, 30, 50))  # Темно-синий фон

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                if event.key == pygame.K_r:
                    # Рестарт уровня
                    player = Player(*level_data["start_pos"])
                    items = []
                    for item_data in level_data["items"]:
                        items.append(Item(item_data["x"], item_data["y"], item_data["type"]))
                if event.key == pygame.K_n:
                    # Следующий уровень
                    current_level = current_level + 1 if current_level + 1 in LEVELS else 1
                    level_data = LEVELS[current_level]
                    platforms = level_data["platforms"]
                    player = Player(*level_data["start_pos"])
                    items = []
                    for item_data in level_data["items"]:
                        items.append(Item(item_data["x"], item_data["y"], item_data["type"]))

        # Движение игрока
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.move(-1)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.move(1)

        # Обновление игрока
        player.update(platforms)

        # Проверка сбора предметов
        for item in items[:]:
            if player.get_rect().colliderect(item.get_rect()):
                handle_item_collection(item.type, player)
                items.remove(item)

        # Проверка завершения уровня
        if len(items) == 0:
            draw_text("Уровень пройден! Нажми N для следующего", 40, GREEN, 100, HEIGHT // 2)

        # Отрисовка платформ
        for platform in platforms:
            pygame.draw.rect(screen, GREEN, platform)

        # Отрисовка предметов
        for item in items:
            item.draw()

        # Отрисовка игрока
        player.draw()

        # Отрисовка информации
        draw_text(f"Уровень: {current_level}", 36, WHITE, 20, 20)
        draw_text(f"Счет: {player.score}", 36, WHITE, 20, 60)
        draw_text(f"Собрано предметов: {len(player.collected_items)}", 36, WHITE, 20, 100)

        # Подсказки
        draw_text("Управление: стрелки/A-D, Пробел - прыжок", 24, WHITE, 20, HEIGHT - 80)
        draw_text("R - рестарт уровня, N - следующий уровень", 24, WHITE, 20, HEIGHT - 50)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()