import pygame
import random
import math
import sys

# ===================================================
# ОБЛАСТЬ ДЛЯ РЕДАКТИРОВАНИЯ (НАЧАЛО)

# Настройки окна
WIDTH, HEIGHT = 1000, 700
FPS = 60

# Настройки игрока
PLAYER_SIZE = 60
PLAYER_COLOR = (70, 130, 255)  # Приятный синий
PLAYER_SPEED = 7

# Настройки квадратов (монет)
NUM_SQUARES = 15  # Количество квадратов
SQUARE_SIZE = 45  # Размер квадратов

# Список квадратов с их описаниями и типами
# Формат: (цвет, описание, очки, тип_анимации)
SQUARES_INFO = [
    ((255, 215, 0), "Золотая монета", 15, "pulse"),  # Золото
    ((192, 192, 192), "Серебряная монета", 8, "rotate"),  # Серебро
    ((205, 127, 50), "Бронзовая монета", 5, "float"),  # Бронза
    ((255, 50, 50), " Рубиновая монета", 25, "pulse"),  # Рубин
    ((50, 205, 50), "Изумрудная монета", 20, "rotate"),  # Изумруд
    ((255, 140, 0), "Тыквенная монета", 12, "float"),  # Оранжевый
    ((148, 0, 211), "Королевская монета", 30, "pulse"),  # Фиолетовый
    ((255, 105, 180), "Розовая монета", 10, "rotate"),  # Розовый
    ((64, 224, 208), " Бриллиант", 40, "pulse"),  # Бирюзовый
    ((255, 255, 240), "Звездная пыль", 18, "float"),  # Бежевый
]

# Цвета интерфейса
BG_COLOR = (20, 25, 45)  # Тёмно-синий с фиолетовым оттенком
GRID_COLOR = (40, 45, 70, 30)  # Полупрозрачная сетка
TEXT_COLOR = (240, 240, 255)  # Светлый почти белый
SCORE_COLOR = (100, 255, 100)  # Светло-зелёный
HIGHLIGHT_COLOR = (255, 255, 100)  # Жёлтый для выделений

# Эффекты частиц
PARTICLE_COUNT = 15  # Количество частиц при сборе
# ===================================================
# ОБЛАСТЬ ДЛЯ РЕДАКТИРОВАНИЯ (КОНЕЦ)
# ===================================================

# Инициализация PyGame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("✨ Космический Сборщик Сокровищ ✨")
clock = pygame.time.Clock()

# Шрифты
try:
    font_large = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 28)
    font_tiny = pygame.font.Font(None, 22)
except:
    font_large = pygame.font.Font(None, 48)
    font_medium = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)
    font_tiny = pygame.font.Font(None, 18)


# Класс для частиц
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 8)
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-3, 3)
        self.life = random.randint(20, 40)
        self.gravity = 0.1

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += self.gravity
        self.life -= 1
        self.size = max(0, self.size - 0.1)

    def draw(self, surface):
        if self.life > 0:
            alpha = min(255, self.life * 6)
            color_with_alpha = (*self.color, alpha)
            particle_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color_with_alpha, (self.size, self.size), self.size)
            surface.blit(particle_surf, (self.x - self.size, self.y - self.size))


# Класс для игрока
class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, PLAYER_SIZE, PLAYER_SIZE)
        self.color = PLAYER_COLOR
        self.speed = PLAYER_SPEED
        self.angle = 0
        self.trail = []
        self.trail_length = 10

    def move(self, keys):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed

        # Добавляем позицию в след
        self.trail.append((self.rect.centerx, self.rect.centery))
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)

        # Плавное движение с ограничениями
        new_x = max(0, min(WIDTH - PLAYER_SIZE, self.rect.x + dx))
        new_y = max(0, min(HEIGHT - PLAYER_SIZE, self.rect.y + dy))
        self.rect.x = new_x
        self.rect.y = new_y

        # Вращение игрока
        self.angle = (self.angle + 1) % 360

    def draw(self, surface):
        # Рисуем след
        for i, pos in enumerate(self.trail):
            alpha = int(50 * (i / len(self.trail)))
            size = int(PLAYER_SIZE * (i / len(self.trail)))
            trail_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            color = (*self.color, alpha)
            pygame.draw.circle(trail_surf, color, (size, size), size)
            surface.blit(trail_surf, (pos[0] - size, pos[1] - size))

        # Рисуем игрока с градиентом
        player_surf = pygame.Surface((PLAYER_SIZE * 2, PLAYER_SIZE * 2), pygame.SRCALPHA)

        # Внешний круг
        pygame.draw.circle(player_surf, self.color, (PLAYER_SIZE, PLAYER_SIZE), PLAYER_SIZE)

        # Внутренний круг (более светлый)
        inner_color = tuple(min(255, c + 40) for c in self.color)
        pygame.draw.circle(player_surf, inner_color, (PLAYER_SIZE, PLAYER_SIZE), PLAYER_SIZE - 8)

        # Глаза
        eye_offset = PLAYER_SIZE // 3
        pygame.draw.circle(player_surf, (255, 255, 255),
                           (PLAYER_SIZE - eye_offset, PLAYER_SIZE - eye_offset // 2), 8)
        pygame.draw.circle(player_surf, (255, 255, 255),
                           (PLAYER_SIZE + eye_offset, PLAYER_SIZE - eye_offset // 2), 8)
        pygame.draw.circle(player_surf, (30, 30, 60),
                           (PLAYER_SIZE - eye_offset, PLAYER_SIZE - eye_offset // 2), 4)
        pygame.draw.circle(player_surf, (30, 30, 60),
                           (PLAYER_SIZE + eye_offset, PLAYER_SIZE - eye_offset // 2), 4)

        # Поворачиваем игрока
        rotated = pygame.transform.rotate(player_surf, self.angle)
        surface.blit(rotated, (self.rect.x - PLAYER_SIZE // 2, self.rect.y - PLAYER_SIZE // 2))


# Класс для квадратов (сокровищ)
class Treasure:
    def __init__(self, x, y, treasure_type):
        self.rect = pygame.Rect(x, y, SQUARE_SIZE, SQUARE_SIZE)
        self.color, self.description, self.points, self.animation_type = treasure_type
        self.collected = False
        self.animation_progress = 0
        self.float_offset = random.uniform(0, 2 * math.pi)
        self.particle_timer = 0

    def update(self):
        if not self.collected:
            self.animation_progress += 0.05
            self.particle_timer += 1

            # Создаем редкие частицы вокруг сокровища
            if self.particle_timer > 30:
                self.particle_timer = 0

    def draw(self, surface):
        if not self.collected:
            # Эффекты анимации
            if self.animation_type == "pulse":
                size_mod = math.sin(self.animation_progress * 2) * 5
                draw_rect = self.rect.inflate(size_mod, size_mod)
            elif self.animation_type == "float":
                float_y = math.sin(self.animation_progress + self.float_offset) * 10
                draw_rect = self.rect.move(0, float_y)
            else:  # rotate
                draw_rect = self.rect

            # Рисуем сокровище с эффектами
            treasure_surf = pygame.Surface((SQUARE_SIZE * 2, SQUARE_SIZE * 2), pygame.SRCALPHA)

            # Внешний блеск
            if self.animation_type == "pulse":
                glow_size = int(abs(math.sin(self.animation_progress)) * 15)
                glow_color = tuple(min(255, c + 100) for c in self.color)
                pygame.draw.circle(treasure_surf, (*glow_color, 100),
                                   (SQUARE_SIZE, SQUARE_SIZE), SQUARE_SIZE + glow_size)

            # Основная форма (ромб для драгоценностей)
            if self.points >= 25:  # Дорогие сокровища - ромбы
                points = [
                    (SQUARE_SIZE, SQUARE_SIZE - SQUARE_SIZE // 1.5),
                    (SQUARE_SIZE + SQUARE_SIZE // 1.5, SQUARE_SIZE),
                    (SQUARE_SIZE, SQUARE_SIZE + SQUARE_SIZE // 1.5),
                    (SQUARE_SIZE - SQUARE_SIZE // 1.5, SQUARE_SIZE)
                ]
                pygame.draw.polygon(treasure_surf, self.color, points)
            else:  # Обычные монеты - круги
                pygame.draw.circle(treasure_surf, self.color, (SQUARE_SIZE, SQUARE_SIZE), SQUARE_SIZE)

                # Внутренний круг
                inner_color = tuple(min(255, c + 50) for c in self.color)
                pygame.draw.circle(treasure_surf, inner_color,
                                   (SQUARE_SIZE, SQUARE_SIZE), SQUARE_SIZE - 10)

            # Блестящие блики
            highlight_size = SQUARE_SIZE // 3
            highlight_pos = (SQUARE_SIZE - highlight_size, SQUARE_SIZE - highlight_size)
            pygame.draw.circle(treasure_surf, (255, 255, 255, 150),
                               highlight_pos, highlight_size)

            # Вращение для некоторых типов
            if self.animation_type == "rotate":
                angle = self.animation_progress * 30
                rotated = pygame.transform.rotate(treasure_surf, angle)
                surface.blit(rotated, (draw_rect.x - SQUARE_SIZE, draw_rect.y - SQUARE_SIZE))
            else:
                surface.blit(treasure_surf, (draw_rect.x - SQUARE_SIZE // 2, draw_rect.y - SQUARE_SIZE // 2))


# Создание объектов игры
player = Player()
treasures = []
particles = []

# Создаём сокровища в случайных местах
for _ in range(NUM_SQUARES):
    x = random.randint(SQUARE_SIZE, WIDTH - SQUARE_SIZE)
    y = random.randint(SQUARE_SIZE, HEIGHT - SQUARE_SIZE)
    treasure_type = random.choice(SQUARES_INFO)
    treasures.append(Treasure(x, y, treasure_type))

# Переменные игры
score = 0
collected_count = 0
current_message = ""
message_timer = 0
combo = 0
combo_timer = 0
game_time = 0


# Функция для создания фоновых звёзд
def create_stars(count):
    stars = []
    for _ in range(count):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.uniform(0.5, 2)
        brightness = random.randint(150, 255)
        twinkle_speed = random.uniform(0.01, 0.05)
        stars.append([x, y, size, brightness, twinkle_speed, 0])
    return stars


# Создаём звёздное небо
stars = create_stars(200)

# Главный игровой цикл
running = True
while running:
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:  # Перезапуск игры
                player = Player()
                treasures = []
                particles = []
                for _ in range(NUM_SQUARES):
                    x = random.randint(SQUARE_SIZE, WIDTH - SQUARE_SIZE)
                    y = random.randint(SQUARE_SIZE, HEIGHT - SQUARE_SIZE)
                    treasure_type = random.choice(SQUARES_INFO)
                    treasures.append(Treasure(x, y, treasure_type))
                score = 0
                collected_count = 0
                current_message = "✨ Игра перезапущена! ✨"
                message_timer = 60
                combo = 0
                combo_timer = 0
                game_time = 0
            if event.key == pygame.K_ESCAPE:  # Выход по ESC
                running = False

    # Обновление времени
    game_time += 1
    if combo_timer > 0:
        combo_timer -= 1
    else:
        combo = 0

    # Движение игрока
    keys = pygame.key.get_pressed()
    player.move(keys)

    # Обновление сокровищ
    for treasure in treasures:
        treasure.update()

        # Проверка столкновения с игроком
        if not treasure.collected and player.rect.colliderect(treasure.rect):
            treasure.collected = True
            score += treasure.points
            collected_count += 1

            # Комбо-система
            combo += 1
            combo_timer = 60  # Комбо сбрасывается через 60 кадров
            combo_bonus = max(0, (combo - 1) * 2)
            score += combo_bonus

            # Создаём частицы
            for _ in range(PARTICLE_COUNT):
                particles.append(Particle(
                    treasure.rect.centerx,
                    treasure.rect.centery,
                    treasure.color
                ))

            current_message = f"{treasure.description} +{treasure.points}"
            if combo_bonus > 0:
                current_message += f" (Комбо x{combo} +{combo_bonus}!)"
            message_timer = 90

    # Обновление частиц
    for particle in particles[:]:
        particle.update()
        if particle.life <= 0:
            particles.remove(particle)

    # Обновление звёзд (мерцание)
    for star in stars:
        star[5] += star[4]
        star[3] = 150 + int(math.sin(star[5]) * 50)

    # Обновление таймера сообщения
    if message_timer > 0:
        message_timer -= 1
    else:
        current_message = ""

    # Проверка завершения игры
    if collected_count >= NUM_SQUARES:
        time_bonus = max(0, 3000 - game_time) // 10
        score += time_bonus
        current_message = f"🎉 Победа! Все сокровища собраны! 🎉"
        message_timer = 180

    # =============== ОТРИСОВКА ===============
    # Фон с градиентом
    for y in range(HEIGHT):
        # Плавный переход от тёмно-синего к фиолетовому
        r = int(20 + (y / HEIGHT) * 10)
        g = int(25 + (y / HEIGHT) * 5)
        b = int(45 + (y / HEIGHT) * 20)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    # Звёзды
    for x, y, size, brightness, _, _ in stars:
        pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), size)

    # Туманность (размытые цветные пятна)
    if game_time % 600 < 300:  # Меняем каждые 5 секунд
        for i in range(3):
            x = WIDTH // 4 * i + (game_time % 100) * 0.5
            y = HEIGHT // 3 + math.sin(game_time * 0.01 + i) * 100
            radius = 100 + math.sin(game_time * 0.02 + i) * 50
            color = (50 + i * 30, 30, 80 + i * 20, 30)
            fog_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(fog_surf, color, (radius, radius), radius)
            screen.blit(fog_surf, (x - radius, y - radius))

    # Частицы
    for particle in particles:
        particle.draw(screen)

    # Сокровища
    for treasure in treasures:
        treasure.draw(screen)

    # Игрок
    player.draw(screen)

    # =============== ИНТЕРФЕЙС ===============
    # Панель статистики с закруглёнными углами
    panel_rect = pygame.Rect(20, 20, 300, 160)
    panel_surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel_surf, (30, 35, 60, 200), panel_surf.get_rect(), border_radius=15)
    pygame.draw.rect(panel_surf, (100, 110, 170, 100), panel_surf.get_rect(), width=2, border_radius=15)
    screen.blit(panel_surf, panel_rect)

    # Очки
    score_text = font_medium.render(f"💰 {score}", True, SCORE_COLOR)
    screen.blit(score_text, (40, 40))

    # Собрано сокровищ
    collected_text = font_small.render(f"Собрано: {collected_count}/{NUM_SQUARES}", True, TEXT_COLOR)
    screen.blit(collected_text, (40, 85))

    # Комбо
    if combo > 1:
        combo_color = (255, 255, 100) if combo_timer > 30 else (255, 200, 100)
        combo_text = font_small.render(f"Комбо: x{combo}", True, combo_color)
        screen.blit(combo_text, (40, 120))

    # Время игры
    minutes = game_time // 3600
    seconds = (game_time // 60) % 60
    time_text = font_tiny.render(f"Время: {minutes:02d}:{seconds:02d}", True, (200, 200, 220))
    screen.blit(time_text, (40, 155))

    # Отображение текущего сообщения
    if current_message:
        message_alpha = min(255, message_timer * 4)
        message_surface = font_small.render(current_message, True, HIGHLIGHT_COLOR)
        message_rect = message_surface.get_rect(center=(WIDTH // 2, 50))

        # Фон сообщения
        bg_rect = message_rect.inflate(40, 20)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(bg_surf, (0, 0, 0, message_alpha // 2), bg_surf.get_rect(), border_radius=10)
        pygame.draw.rect(bg_surf, (255, 255, 100, message_alpha // 3), bg_surf.get_rect(), width=2, border_radius=10)
        screen.blit(bg_surf, bg_rect)
        screen.blit(message_surface, message_rect)

    # Панель управления
    controls = [
        "Управление: WASD или Стрелки",
        "Перезапуск: R",
        "Выход: ESC",
        "Цель: Собрать все сокровища!"
    ]

    control_panel = pygame.Rect(WIDTH - 320, 20, 300, 120)
    control_surf = pygame.Surface((control_panel.width, control_panel.height), pygame.SRCALPHA)
    pygame.draw.rect(control_surf, (30, 35, 60, 200), control_surf.get_rect(), border_radius=15)
    screen.blit(control_surf, control_panel)

    for i, text in enumerate(controls):
        instr_surface = font_tiny.render(text, True, (200, 200, 220))
        screen.blit(instr_surface, (WIDTH - 300, 40 + i * 25))

    # Прогресс-бар
    if NUM_SQUARES > 0:
        progress = collected_count / NUM_SQUARES
        bar_width = 400
        bar_rect = pygame.Rect(WIDTH // 2 - bar_width // 2, HEIGHT - 40, bar_width, 20)

        # Фон прогресс-бара
        pygame.draw.rect(screen, (50, 55, 80), bar_rect, border_radius=10)

        # Заполненная часть
        fill_width = max(10, int(bar_width * progress))
        fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_width, bar_rect.height)

        # Градиент для прогресс-бара
        for i in range(fill_width):
            color_ratio = i / bar_width
            r = int(50 + color_ratio * 200)
            g = int(150 + color_ratio * 100)
            b = int(255)
            pygame.draw.line(screen, (r, g, b),
                             (bar_rect.x + i, bar_rect.y),
                             (bar_rect.x + i, bar_rect.y + bar_rect.height))

        pygame.draw.rect(screen, (200, 220, 255), bar_rect, width=2, border_radius=10)

        # Текст прогресса
        progress_text = font_tiny.render(f"{collected_count}/{NUM_SQUARES}", True, TEXT_COLOR)
        screen.blit(progress_text, (bar_rect.centerx - 20, bar_rect.y - 25))

    # Декоративные элементы
    if game_time % 120 < 60:  # Мерцающий заголовок
        title_color = (255, 255, 200) if game_time % 60 < 30 else (200, 230, 255)
        title = font_large.render("СОКРОВИЩА", True, title_color)
        title_shadow = font_large.render("СОКРОВИЩА", True, (0, 0, 0, 100))
        screen.blit(title_shadow, (WIDTH // 2 - title.get_width() // 2 + 3, 103))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

    # Обновление экрана
    pygame.display.flip()
    clock.tick(FPS)

# Завершение игры
pygame.quit()
sys.exit()