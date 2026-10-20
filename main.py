import pygame
import random

pygame.init()
WIDTH, HEIGHT = (750, 700)
FPS = 40
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
player_imgs = [pygame.image.load('sprites/player1.png').convert_alpha(), pygame.image.load('sprites/player2.png').convert_alpha()]
enemy_imgs = [pygame.image.load('sprites/enemy1.png').convert_alpha(), pygame.image.load('sprites/enemy2.png').convert_alpha()]

map_list = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
            [0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 0],
            [0, 0, 0, 1, 0, 0, 1, 2, 1, 0, 0, 1, 0, 0, 0],]

game_over = False
game_won = False

bullets = []
class Bullet:
    def __init__(self, pos, degree, bulletfrom, speed=5):
        self.bulletfrom = bulletfrom
        self.degree = degree
        self.img = pygame.transform.scale(pygame.image.load('sprites/bullet.png').convert_alpha(), (12, 16))
        self.img = pygame.transform.rotate(self.img, self.degree)
        self.rect = self.img.get_rect()
        self.rect.center = pos
        self.speed = speed

    def update(self, world_map_instance):
        global game_over, game_won
        
        # Видаляємо кулю, якщо вона вийшла за межі екрану
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT or self.rect.right >= WIDTH or self.rect.left <= 0:
            if self in bullets:
                bullets.remove(self)
                if self.bulletfrom == 'player':
                    player.can_shoot = True
                elif self.bulletfrom == 'enemy':
                    for enemy in enemies:
                        if not enemy.can_shoot:
                            enemy.can_shoot = True
                            break
            return

        # Перевіряємо зіткнення зі стінами
        wall_hit = False
        for tile_index, (wall_img, wall_rect) in enumerate(list(world_map_instance.pos_list)): 
            if self.rect.colliderect(wall_rect):
                if self in bullets:
                    bullets.remove(self)
                if self.bulletfrom == 'player':
                    player.can_shoot = True
                elif self.bulletfrom == 'enemy':
                     for enemy in enemies:
                        if not enemy.can_shoot:
                            enemy.can_shoot = True
                            break
                
                if wall_img == world_map_instance.wall_img:
                    world_map_instance.pos_list.pop(tile_index)
                elif wall_img == world_map_instance.base_img:
                    game_over = True # Гра закінчується при попаданні в базу
                
                wall_hit = True
                break

        if wall_hit:
            return

        # Перевіряємо зіткнення з гравцем (якщо куля від ворога)
        if self.bulletfrom == 'enemy' and self.rect.colliderect(player.rect):
            player.lifes -= 1
            if self in bullets:
                bullets.remove(self)
            for enemy in enemies:
                if not enemy.can_shoot:
                    enemy.can_shoot = True
                    break
            if player.lifes <= 0:
                game_over = True
            return

        # Перевіряємо зіткнення з ворогами (якщо куля від гравця)
        if self.bulletfrom == 'player':
            for enemy_tank in list(enemies):
                if self.rect.colliderect(enemy_tank.rect):
                    enemy_tank.lifes = 1
                    enemies.remove(enemy_tank)
                    
                    if self in bullets:
                        bullets.remove(self)
                    player.can_shoot = True
                    return

        # Рухаємо кулю
        if self.degree == 0:
            self.rect.y -= self.speed
        elif self.degree == 180:
            self.rect.y += self.speed
        elif self.degree == 90:
            self.rect.x -= self.speed
        elif self.degree == -90:
            self.rect.x += self.speed

    def draw(self):
        screen.blit(self.img, self.rect)

counter = 0
ismoving = False
class Player():
    def __init__(self, width, height, speed, lifes=1, rotate=0):
        self.width = width
        self.height = height
        self.rotate = rotate
        self.img = pygame.transform.scale(player_imgs[0], (self.width, self.height))
        self.rect = self.img.get_rect()
        self.rect.topleft = ((WIDTH//2 - 150), HEIGHT - self.height) 
        self.current_img = player_imgs[0]
        self.speed = speed
        self.lifes = lifes
        self.bullet_direction = (32, 0)
        self.can_shoot = True

    def update(self):
        self.img = pygame.transform.scale(self.current_img, (self.width, self.height))
        self.img = pygame.transform.rotate(self.img, self.rotate)
        screen.blit( self.img, self.rect)

    def move(self, keys, walls):
        global ismoving
        ismoving = False

        original_x, original_y = self.rect.x, self.rect.y
        if keys[pygame.K_w]:
            ismoving = True
            self.rotate = 0
            self.rect.y -= self.speed
            self.bullet_direction = (0, -32)
        if keys[pygame.K_s]:
            self.rotate = 180
            ismoving = True
            self.rect.y += self.speed
            self.bullet_direction = (0, 32)
        if keys[pygame.K_a]:
            ismoving = True
            self.rotate = 90
            self.rect.x -= self.speed
            self.bullet_direction = (-32, 0)
        if keys[pygame.K_d]:
            ismoving = True
            self.rotate = -90
            self.rect.x += self.speed
            self.bullet_direction = (32, 0)

        if keys[pygame.K_SPACE] and self.can_shoot:
            bullet_pos = (self.rect.centerx + self.bullet_direction[0], self.rect.centery + self.bullet_direction[1])
            bullet = Bullet(bullet_pos, self.rotate, 'player')
            bullets.append(bullet)
            self.can_shoot = False

        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

        for wall_tile, wall_rect in walls:
            if self.rect.colliderect(wall_rect):
                self.rect.x = original_x
                self.rect.y = original_y
                break
        
        for enemy_tank in enemies:
            if self.rect.colliderect(enemy_tank.rect):
                self.rect.x = original_x
                self.rect.y = original_y
                break

    def anim(self):
        global counter, ismoving
        if ismoving:
            if counter >= 4:
                counter = 0
            if counter < 2:
                self.current_img = player_imgs[0]
            else: 
                self.current_img = player_imgs[1]
            counter += 2
        else:
            self.current_img = player_imgs[0]

class Enemy:
    def __init__(self, x, y, width, height, speed, lifes=1, rotate=0):
        self.width = width
        self.height = height
        self.rotate = rotate
        self.img = pygame.transform.scale(enemy_imgs[0], (self.width, self.height))
        self.rect = self.img.get_rect()
        self.rect.topleft = (x, y) 
        self.current_img = enemy_imgs[0]
        self.speed = speed
        self.lifes = float(lifes)
        self.bullet_direction = (32, 0)
        self.can_shoot = True
        self.move_timer = 0
        self.shoot_timer = 0
        self.direction = random.choice(['up', 'down', 'left', 'right']) # Початковий випадковий напрямок
        self.anim_counter = 0
        self.ismoving = False
        
        # Координати бази гравця (приблизно)
        self.target_x = WIDTH // 2 - 25
        self.target_y = HEIGHT - 50

    def update(self):
        self.img = pygame.transform.scale(self.current_img, (self.width, self.height))
        self.img = pygame.transform.rotate(self.img, self.rotate)
        screen.blit(self.img, self.rect)
        self.anim()

    def move(self, walls, player_rect, enemies_list):
        original_x, original_y = self.rect.x, self.rect.y
        self.ismoving = True

        self.move_timer += 1
        # Змінюємо напрямок руху кожні 30-80 кадрів, щоб танк міг адаптуватися до шляху до бази
        if self.move_timer > random.randint(30, 80):
            # Визначаємо, в якому напрямку рухатися, щоб наблизитися до бази
            dx = self.target_x - self.rect.centerx
            dy = self.target_y - self.rect.centery

            possible_directions = []
            if dy > 0: # База нижче
                possible_directions.append('down')
            elif dy < 0: # База вище
                possible_directions.append('up')
            
            if dx > 0: # База правіше
                possible_directions.append('right')
            elif dx < 0: # База лівіше
                possible_directions.append('left')
            
            # Якщо є кілька варіантів, вибираємо один випадково, щоб уникнути застрягання
            if possible_directions:
                self.direction = random.choice(possible_directions)
            else: # Якщо ворог вже на одній лінії з базою, просто рухаємося до неї
                self.direction = random.choice(['up', 'down', 'left', 'right']) # Запасний варіант
            
            self.move_timer = 0

        # Рух відповідно до обраного напрямку
        if self.direction == 'up':
            self.rotate = 0
            self.rect.y -= self.speed
            self.bullet_direction = (0, -32)
        elif self.direction == 'down':
            self.rotate = 180
            self.rect.y += self.speed
            self.bullet_direction = (0, 32)
        elif self.direction == 'left':
            self.rotate = 90
            self.rect.x -= self.speed
            self.bullet_direction = (-32, 0)
        elif self.direction == 'right':
            self.rotate = -90
            self.rect.x += self.speed
            self.bullet_direction = (32, 0)

        # Обмеження руху в межах екрану
        if self.rect.top < 0:
            self.rect.top = 0
            self.direction = random.choice(['down', 'left', 'right']) # Змінюємо напрямок при ударі об край
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            self.direction = random.choice(['up', 'left', 'right'])
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            self.direction = random.choice(['up', 'down', 'left'])
        if self.rect.left < 0:
            self.rect.left = 0
            self.direction = random.choice(['up', 'down', 'right'])

        # Обробка зіткнень зі стінами
        for wall_tile, wall_rect in walls:
            if self.rect.colliderect(wall_rect):
                self.rect.x = original_x
                self.rect.y = original_y
                self.direction = random.choice(['up', 'down', 'left', 'right']) # Змінюємо напрямок при ударі об стіну
                break
        
        # Обробка зіткнень з гравцем
        if self.rect.colliderect(player_rect):
            self.rect.x = original_x
            self.rect.y = original_y
            self.direction = random.choice(['up', 'down', 'left', 'right'])
        
        # Обробка зіткнень з іншими ворогами
        for other_enemy in enemies_list:
            if other_enemy != self and self.rect.colliderect(other_enemy.rect):
                self.rect.x = original_x
                self.rect.y = original_y
                self.direction = random.choice(['up', 'down', 'left', 'right'])
                break

        # Логіка пострілів
        self.shoot_timer += 1
        if self.can_shoot and self.shoot_timer > random.randint(80, 200):
            bullet_pos = (self.rect.centerx + self.bullet_direction[0], self.rect.centery + self.bullet_direction[1])
            bullet = Bullet(bullet_pos, self.rotate, 'enemy')
            bullets.append(bullet)
            self.can_shoot = False
            self.shoot_timer = 0
            
    def anim(self):
        if self.ismoving:
            self.anim_counter += 1
            if self.anim_counter >= 4:
                self.anim_counter = 0
            if self.anim_counter < 2:
                self.current_img = enemy_imgs[0]
            else: 
                self.current_img = enemy_imgs[1]
        else:
            self.current_img = enemy_imgs[0]

class Map:
    def __init__(self, data):
        self.pos_list = []
        self.wall_img = pygame.transform.scale(pygame.image.load('sprites/block.png').convert_alpha(), (50, 50))
        self.base_img = pygame.transform.scale(pygame.image.load('sprites/base.png').convert_alpha(), (50, 50))
        self.broken_base_img = pygame.transform.scale(pygame.image.load('sprites/broken_base.png').convert_alpha(), (50, 50))

        row_count = 0
        for row_index, row in enumerate(data):
            col_count = 0
            for col_index, tile_type in enumerate(row):
                if tile_type == 1:
                    image = self.wall_img
                    image_rect = image.get_rect()
                    image_rect.x = image.get_width() * col_count
                    image_rect.y = image.get_height() * row_count
                    self.pos_list.append((image, image_rect))
                elif tile_type == 2:
                    image = self.base_img
                    image_rect = image.get_rect()
                    image_rect.x = image.get_width() * col_count
                    image_rect.y = image.get_height() * row_count
                    self.pos_list.append((image, image_rect))
                col_count += 1
            row_count += 1
        
    def draw(self):
        for tile in self.pos_list:
            screen.blit(tile[0], tile[1])

world = Map(map_list)
player = Player(45, 45, 3) 

enemies = []

enemies.append(Enemy(50, 0, 45, 45, 2, 2)) # x, y, width, height, speed, lifes
enemies.append(Enemy(WIDTH - 50, 50, 45, 45, 2, 2))
enemies.append(Enemy(50, HEIGHT // 2 - 25, 45, 45, 2, 2))
enemies.append(Enemy(WIDTH - 50, HEIGHT // 2, 45, 45, 2, 2))

game = True
while game:
    screen.fill((10, 10, 10))

    if not game_over and not game_won:
        world.draw()

        keys = pygame.key.get_pressed()
        player.move(keys, world.pos_list)
        player.anim()
        player.update()
        
        for enemy_tank in list(enemies):
            enemy_tank.move(world.pos_list, player.rect, enemies)
            enemy_tank.update()

        for bullet in list(bullets):
            bullet.update(world)
            bullet.draw()
            
        # Перевірка умови перемоги
        if not enemies and not game_over:
            game_won = True

    elif game_over:
        font = pygame.font.Font(None, 74)
        text = font.render("GAME OVER", True, (255, 0, 0))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)
    elif game_won:
        font = pygame.font.Font(None, 74)
        text = font.render("YOU WIN!", True, (0, 255, 0))
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(text, text_rect)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game = False
    
    clock.tick(FPS)
    pygame.display.flip()