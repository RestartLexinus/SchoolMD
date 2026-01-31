import pygame
import sys
import random
import math

# Инициализация Pygame
pygame.init()

# Константы для настроек игры
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BACKGROUND_COLOR = (20, 25, 45)  # Темно-синий
PLAYER_COLOR = (0, 200, 255)     # Голубой
ENEMY_COLORS = [(255, 100, 100), (255, 150, 50), (255, 50, 150)]
SHAPE_TYPES = ['circle', 'square', 'triangle']
LASER_COLOR = (0, 255, 200)      # Цвет луча

# Класс луча (пули)
class Laser:
    def __init__(self, x, y, direction_x, direction_y):
        self.x = x
        self.y = y
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.speed = 10
        self.radius = 5
        self.color = LASER_COLOR
        self.active = True
        self.lifetime = 60  # Луч существует 60 кадров (1 секунда при FPS=60)
        
    def move(self):
        """Движение луча"""
        self.x += self.direction_x * self.speed
        self.y += self.direction_y * self.speed
        self.lifetime -= 1
        
        # Деактивируем луч, если он вышел за границы экрана или истекло время жизни
        if (self.x < 0 or self.x > SCREEN_WIDTH or 
            self.y < 0 or self.y > SCREEN_HEIGHT or
            self.lifetime <= 0):
            self.active = False
            
    def draw(self, screen):
        """Отрисовка луча"""
        if self.active:
            # Основной круг луча
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            
            # Эффект свечения луча (внутренний круг)
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius - 2)
            
            # Эффект хвоста луча
            tail_length = 15
            tail_points = []
            for i in range(5):
                tail_x = self.x - self.direction_x * i * 3
                tail_y = self.y - self.direction_y * i * 3
                tail_radius = self.radius * (1 - i/5)
                pygame.draw.circle(screen, self.color, (int(tail_x), int(tail_y)), int(tail_radius))
                
    def check_collision(self, shape):
        """Проверка столкновения луча с фигурой"""
        if not self.active:
            return False
            
        distance = math.sqrt((self.x - shape.x)**2 + (self.y - shape.y)**2)
        
        # Для квадратов и треугольников используем упрощенную проверку
        if shape.shape_type == 'circle':
            return distance < (self.radius + shape.size)
        else:
            # Для квадратов и треугольников используем проверку по bounding circle
            return distance < (self.radius + shape.size * 1.2)

# Класс игрока
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.speed = 5
        self.color = PLAYER_COLOR
        self.score = 0
        self.lives = 3
        self.laser_cooldown = 0  # Время перезарядки луча
        self.max_cooldown = 20   # Максимальное время перезарядки (кадры)
        
    def move(self, keys):
        """Движение игрока по нажатию клавиш"""
        if keys[pygame.K_LEFT] and self.x > self.radius:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.radius:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > self.radius:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - self.radius:
            self.y += self.speed
            
        # Обновление времени перезарядки
        if self.laser_cooldown > 0:
            self.laser_cooldown -= 1
            
    def shoot(self, lasers, mouse_pos):
        """Создание луча при нажатии на пробел или клике мыши"""
        if self.laser_cooldown <= 0:
            # Определяем направление выстрела (в сторону курсора мыши или вперед)
            if mouse_pos:
                # Стреляем в сторону курсора мыши
                direction_x = mouse_pos[0] - self.x
                direction_y = mouse_pos[1] - self.y
                length = math.sqrt(direction_x**2 + direction_y**2)
                if length > 0:
                    direction_x /= length
                    direction_y /= length
                else:
                    direction_x, direction_y = 0, -1  # Стреляем вверх, если курсор на игроке
            else:
                # Стреляем вперед (вверх) по умолчанию
                direction_x, direction_y = 0, -1
                
            # Создаем луч, начиная от края игрока
            start_x = self.x + direction_x * (self.radius + 5)
            start_y = self.y + direction_y * (self.radius + 5)
            
            lasers.append(Laser(start_x, start_y, direction_x, direction_y))
            self.laser_cooldown = self.max_cooldown
            return True
        return False
            
    def draw(self, screen):
        """Отрисовка игрока"""
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        # Добавляем небольшой внутренний круг для визуального эффекта
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), self.radius - 8, 2)
        
        # Отображение индикатора перезарядки
        if self.laser_cooldown > 0:
            cooldown_percent = self.laser_cooldown / self.max_cooldown
            angle = 360 * cooldown_percent
            pygame.draw.arc(screen, (255, 50, 50), 
                           (self.x - 25, self.y - 25, 50, 50),
                           math.radians(0), math.radians(angle), 3)
        
    def check_collision(self, enemy):
        """Проверка столкновения с врагом"""
        distance = math.sqrt((self.x - enemy.x)**2 + (self.y - enemy.y)**2)
        return distance < (self.radius + enemy.size)

# Базовый класс для геометрических фигур
class GeometricShape:
    def __init__(self):
        self.size = random.randint(15, 40)
        self.x = random.randint(self.size, SCREEN_WIDTH - self.size)
        self.y = random.randint(self.size, SCREEN_HEIGHT - self.size)
        self.color = random.choice(ENEMY_COLORS)
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-2, 2)
        self.shape_type = random.choice(SHAPE_TYPES)
        self.rotation = 0
        self.rotation_speed = random.uniform(-3, 3)
        self.health = 1  # Здоровье фигуры (по умолчанию 1)
        
    def move(self):
        """Движение фигуры с отскоками от границ экрана"""
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Отскок от границ экрана
        if self.x < self.size or self.x > SCREEN_WIDTH - self.size:
            self.speed_x *= -1
        if self.y < self.size or self.y > SCREEN_HEIGHT - self.size:
            self.speed_y *= -1
            
        # Вращение фигуры
        self.rotation += self.rotation_speed
        
    def draw(self, screen):
        """Отрисовка фигуры в зависимости от её типа"""
        if self.shape_type == 'circle':
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
            # Декоративный внутренний круг
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.size - 5, 2)
            
        elif self.shape_type == 'square':
            # Создаем повернутый квадрат
            points = []
            for i in range(4):
                angle = self.rotation + i * 90
                rad_angle = math.radians(angle)
                px = self.x + self.size * math.cos(rad_angle)
                py = self.y + self.size * math.sin(rad_angle)
                points.append((px, py))
            pygame.draw.polygon(screen, self.color, points)
            
        elif self.shape_type == 'triangle':
            # Создаем повернутый треугольник
            points = []
            for i in range(3):
                angle = self.rotation + i * 120
                rad_angle = math.radians(angle)
                px = self.x + self.size * math.cos(rad_angle)
                py = self.y + self.size * math.sin(rad_angle)
                points.append((px, py))
            pygame.draw.polygon(screen, self.color, points)

# Класс игры
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Геометрическое приключение с лазером!")
        self.clock = pygame.time.Clock()
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.shapes = []
        self.lasers = []  # Список активных лучей
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.game_over = False
        self.level = 1
        self.shape_count = 5
        self.spawn_timer = 0
        self.spawn_delay = 60  # кадры между спавном новых фигур
        self.mouse_pos = None  # Позиция курсора мыши
        
        # Создаем начальные фигуры
        for _ in range(self.shape_count):
            self.shapes.append(GeometricShape())
            
    def handle_events(self):
        """Обработка событий игры"""
        self.mouse_pos = None  # Сбрасываем позицию мыши
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.restart_game()
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE and not self.game_over:
                    # Выстрел при нажатии пробела (стреляет вперед)
                    self.player.shoot(self.lasers, None)
            if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                if event.button == 1:  # Левая кнопка мыши
                    # Выстрел при клике мыши (стреляет в сторону курсора)
                    self.mouse_pos = pygame.mouse.get_pos()
                    self.player.shoot(self.lasers, self.mouse_pos)
                    
    def update(self):
        """Обновление состояния игры"""
        if not self.game_over:
            # Движение игрока
            keys = pygame.key.get_pressed()
            self.player.move(keys)
            
            # Обновление фигур
            for shape in self.shapes:
                shape.move()
                
                # Проверка столкновений игрока с фигурой
                if self.player.check_collision(shape):
                    self.player.lives -= 1
                    self.shapes.remove(shape)
                    # Добавляем новую фигуру взамен удаленной
                    self.shapes.append(GeometricShape())
                    
                    # Проверяем, остались ли жизни у игрока
                    if self.player.lives <= 0:
                        self.game_over = True
                        
            # Обновление лучей
            for laser in self.lasers[:]:  # Используем копию списка для безопасного удаления
                laser.move()
                
                # Проверка столкновений лучей с фигурами
                for shape in self.shapes[:]:
                    if laser.check_collision(shape):
                        # Уничтожаем фигуру
                        self.shapes.remove(shape)
                        # Добавляем очки за уничтожение
                        self.player.score += 100
                        # Помечаем луч как неактивный
                        laser.active = False
                        # Добавляем новую фигуру
                        self.shapes.append(GeometricShape())
                        break
                
                # Удаляем неактивные лучи
                if not laser.active:
                    self.lasers.remove(laser)
            
            # Увеличение счета со временем
            self.player.score += 0.1
            
            # Уровень сложности увеличивается со временем
            if self.player.score > self.level * 500:
                self.level += 1
                self.shape_count += 2
                # Добавляем новые фигуры при повышении уровня
                for _ in range(2):
                    self.shapes.append(GeometricShape())
                    
            # Периодическое добавление новых фигур
            self.spawn_timer += 1
            if self.spawn_timer >= self.spawn_delay:
                self.spawn_timer = 0
                if len(self.shapes) < 15:  # Максимальное количество фигур
                    self.shapes.append(GeometricShape())
                    
    def draw(self):
        """Отрисовка всех элементов игры"""
        # Заливка фона
        self.screen.fill(BACKGROUND_COLOR)
        
        # Отрисовка сетки на фоне для декоративного эффекта
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(self.screen, (30, 35, 60), (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 50):
            pygame.draw.line(self.screen, (30, 35, 60), (0, y), (SCREEN_WIDTH, y), 1)
        
        # Отрисовка фигур
        for shape in self.shapes:
            shape.draw(self.screen)
            
        # Отрисовка лучей
        for laser in self.lasers:
            laser.draw(self.screen)
            
        # Отрисовка игрока
        self.player.draw(self.screen)
        
        # Отрисовка информации (счет, жизни, уровень)
        score_text = self.font.render(f"Счет: {int(self.player.score)}", True, (255, 255, 255))
        lives_text = self.font.render(f"Жизни: {self.player.lives}", True, (255, 255, 255))
        level_text = self.font.render(f"Уровень: {self.level}", True, (255, 255, 255))
        shapes_text = self.small_font.render(f"Фигур: {len(self.shapes)}", True, (200, 200, 200))
        lasers_text = self.small_font.render(f"Лучей: {len(self.lasers)}", True, (200, 200, 200))
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))
        self.screen.blit(level_text, (10, 90))
        self.screen.blit(shapes_text, (10, 130))
        self.screen.blit(lasers_text, (10, 160))
        
        # Инструкции по управлению
        controls_text = [
            "Управление: стрелки для движения",
            "Пробел или ЛКМ - выстрел лазером",
            "Цель: избегайте фигур и стреляйте по ним",
            "R - перезапуск игры, ESC - выход"
        ]
        
        for i, text in enumerate(controls_text):
            control_text = self.small_font.render(text, True, (180, 180, 220))
            self.screen.blit(control_text, (SCREEN_WIDTH - 350, 10 + i * 25))
        
        # Если игра окончена, показываем сообщение
        if self.game_over:
            self.draw_game_over()
            
        # Обновление экрана
        pygame.display.flip()
        
    def draw_game_over(self):
        """Отрисовка экрана окончания игры"""
        # Полупрозрачное наложение
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Текст "Игра окончена"
        game_over_font = pygame.font.SysFont(None, 72)
        game_over_text = game_over_font.render("ИГРА ОКОНЧЕНА", True, (255, 50, 50))
        self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 100))
        
        # Финальный счет
        score_text = self.font.render(f"Финальный счет: {int(self.player.score)}", True, (255, 255, 255))
        self.screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 - 20))
        
        # Уровень
        level_text = self.font.render(f"Достигнутый уровень: {self.level}", True, (255, 255, 255))
        self.screen.blit(level_text, (SCREEN_WIDTH//2 - level_text.get_width()//2, SCREEN_HEIGHT//2 + 20))
        
        # Статистика по выстрелам
        lasers_fired = int(self.player.score / 100)  # Примерное количество выстрелов
        lasers_text = self.font.render(f"Уничтожено фигур: {lasers_fired}", True, (255, 255, 255))
        self.screen.blit(lasers_text, (SCREEN_WIDTH//2 - lasers_text.get_width()//2, SCREEN_HEIGHT//2 + 60))
        
        # Инструкция по перезапуску
        restart_text = self.font.render("Нажмите R для перезапуска игры", True, (100, 255, 100))
        self.screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 120))
        
    def restart_game(self):
        """Перезапуск игры"""
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.shapes = []
        self.lasers = []
        self.game_over = False
        self.level = 1
        self.shape_count = 5
        self.spawn_timer = 0
        
        # Создаем начальные фигуры
        for _ in range(self.shape_count):
            self.shapes.append(GeometricShape())
            
    def run(self):
        """Основной игровой цикл"""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

# Запуск игры
if __name__ == "__main__":
    game = Game()
    game.run()