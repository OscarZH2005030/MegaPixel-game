import pygame
import random
import sys
import math

# 初始化 Pygame
pygame.init()
pygame.mixer.init()

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 32
FPS = 60

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# 创建游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("MegaPixel - 版权所有 © 2025 赵瀚")
clock = pygame.time.Clock()

# 创建字体
title_font = pygame.font.SysFont(None, 48)
ui_font = pygame.font.SysFont(None, 28)
small_font = pygame.font.SysFont(None, 20)

# 玩家类
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE * 2), pygame.SRCALPHA)
        # 身体 - 蓝色
        pygame.draw.rect(self.image, BLUE, (0, TILE_SIZE//2, TILE_SIZE, TILE_SIZE))
        # 头部 - 肤色
        pygame.draw.rect(self.image, (255, 220, 177), (TILE_SIZE//4, 0, TILE_SIZE//2, TILE_SIZE//2))
        # 眼睛 - 黑色
        pygame.draw.rect(self.image, BLACK, (TILE_SIZE//3, TILE_SIZE//6, 3, 3))
        pygame.draw.rect(self.image, BLACK, (2*TILE_SIZE//3, TILE_SIZE//6, 3, 3))
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.health = 100
        self.coins = 0
        self.direction = 1
        self.jumping = False
        self.jump_velocity = 0
        self.gravity = 0.5
        self.invincible = 0
        self.on_ground = False
        
    def update(self, platforms, enemies, coins, megapixels):
        if self.invincible > 0:
            self.invincible -= 1
            
        old_x = self.rect.x
        old_y = self.rect.y
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.direction = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            self.direction = 1
            
        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground and not self.jumping:
            self.jumping = True
            self.jump_velocity = -12
            self.on_ground = False
            
        if self.jumping:
            self.rect.y += self.jump_velocity
            self.jump_velocity += self.gravity
            
            self.on_ground = False
            for platform in platforms:
                if (self.rect.bottom >= platform.rect.top and 
                    self.rect.top < platform.rect.top and
                    self.rect.right > platform.rect.left and 
                    self.rect.left < platform.rect.right and
                    self.jump_velocity > 0):
                    self.rect.bottom = platform.rect.top
                    self.jumping = False
                    self.jump_velocity = 0
                    self.on_ground = True
                    break
            
            if self.rect.bottom >= SCREEN_HEIGHT - 40 and self.jump_velocity > 0:
                self.rect.bottom = SCREEN_HEIGHT - 40
                self.jumping = False
                self.jump_velocity = 0
                self.on_ground = True
        else:
            self.on_ground = False
            for platform in platforms:
                if (self.rect.bottom == platform.rect.top and 
                    self.rect.right > platform.rect.left and 
                    self.rect.left < platform.rect.right):
                    self.on_ground = True
                    break
                    
            if not self.on_ground:
                self.rect.y += 5
        
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            if not self.jumping:
                self.health -= 5
            
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if old_x + self.rect.width <= platform.rect.left and self.rect.right >= platform.rect.left:
                    self.rect.right = platform.rect.left
                elif old_x >= platform.rect.right and self.rect.left <= platform.rect.right:
                    self.rect.left = platform.rect.right
                    
        if self.invincible <= 0:
            for enemy in enemies:
                if self.rect.colliderect(enemy.rect):
                    if old_y + self.rect.height <= enemy.rect.top and self.rect.bottom >= enemy.rect.top:
                        enemy.kill()
                        self.rect.bottom = enemy.rect.top
                        self.jumping = False
                        self.jump_velocity = 0
                        self.coins += 5
                    else:
                        self.health -= 10
                        self.invincible = 30
                        if self.rect.x < enemy.rect.x:
                            self.rect.x -= 30
                        else:
                            self.rect.x += 30
                        
        for coin in coins:
            if self.rect.colliderect(coin.rect):
                coin.kill()
                self.coins += 1
                
        for megapixel in megapixels:
            if self.rect.colliderect(megapixel.rect):
                megapixel.kill()
                self.coins += 10
                self.health = min(100, self.health + 30)
                
        if self.health <= 0:
            self.health = 0

    def draw_health_bar(self, surface):
        bar_width = 100
        bar_height = 10
        fill_width = int((self.health / 100) * bar_width)
        
        pygame.draw.rect(surface, RED, (self.rect.x, self.rect.y - 15, bar_width, bar_height))
        pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 15, fill_width, bar_height))
        pygame.draw.rect(surface, WHITE, (self.rect.x, self.rect.y - 15, bar_width, bar_height), 1)

# 平台类
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        for i in range(0, width, 4):
            for j in range(0, height, 4):
                color_variation = random.randint(-10, 10)
                color = (
                    max(0, min(255, BROWN[0] + color_variation)),
                    max(0, min(255, BROWN[1] + color_variation)),
                    max(0, min(255, BROWN[2] + color_variation))
                )
                pygame.draw.rect(self.image, color, (i, j, 3, 3))
                
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# 敌人类
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(self.image, RED, (0, 0, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(self.image, WHITE, (TILE_SIZE//4, TILE_SIZE//4, 4, 4))
        pygame.draw.rect(self.image, WHITE, (3*TILE_SIZE//4, TILE_SIZE//4, 4, 4))
        pygame.draw.rect(self.image, BLACK, (TILE_SIZE//4, 3*TILE_SIZE//4, TILE_SIZE//2, 3))
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = random.randint(1, 3)
        self.direction = 1
        
    def update(self, platforms):
        self.rect.x += self.speed * self.direction
        
        on_platform = False
        for platform in platforms:
            if (self.rect.bottom == platform.rect.top and 
                self.rect.right > platform.rect.left and 
                self.rect.left < platform.rect.right):
                on_platform = True
                if (self.direction > 0 and self.rect.right >= platform.rect.right) or \
                   (self.direction < 0 and self.rect.left <= platform.rect.left):
                    self.direction *= -1
                break
                
        if not on_platform:
            self.direction *= -1
            
        if self.rect.left < 0:
            self.direction = 1
        if self.rect.right > SCREEN_WIDTH:
            self.direction = -1

# 金币类
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE//2, TILE_SIZE//2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (TILE_SIZE//4, TILE_SIZE//4), TILE_SIZE//4)
        pygame.draw.circle(self.image, (255, 200, 0), (TILE_SIZE//4, TILE_SIZE//4), TILE_SIZE//6)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.float_offset = random.random() * 2 * math.pi

    def update(self):
        self.rect.y += math.sin(pygame.time.get_ticks() / 200 + self.float_offset) * 0.5

# MegaPixel 特殊物品类
class MegaPixel(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(self.image, PURPLE, (0, 0, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(self.image, (200, 0, 200), (4, 4, TILE_SIZE-8, TILE_SIZE-8))
        pygame.draw.rect(self.image, (255, 100, 255), (8, 8, TILE_SIZE-16, TILE_SIZE-16))
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.float_offset = random.random() * 2 * math.pi

    def update(self):
        self.rect.y += math.sin(pygame.time.get_ticks() / 200 + self.float_offset) * 0.7
        
        glow_size = abs(math.sin(pygame.time.get_ticks() / 300)) * 5
        glow_surface = pygame.Surface((TILE_SIZE + int(glow_size)*2, TILE_SIZE + int(glow_size)*2), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, (255, 100, 255, 100), 
                        (0, 0, TILE_SIZE + int(glow_size)*2, TILE_SIZE + int(glow_size)*2))
        self.image = glow_surface
        pygame.draw.rect(self.image, PURPLE, (glow_size, glow_size, TILE_SIZE, TILE_SIZE))
        pygame.draw.rect(self.image, (200, 0, 200), (glow_size+4, glow_size+4, TILE_SIZE-8, TILE_SIZE-8))
        pygame.draw.rect(self.image, (255, 100, 255), (glow_size+8, glow_size+8, TILE_SIZE-16, TILE_SIZE-16))

# 创建游戏精灵组
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
coins = pygame.sprite.Group()
megapixels = pygame.sprite.Group()

# 创建玩家
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
all_sprites.add(player)

# 创建平台
platform_positions = [
    (0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40),
    (100, 500, 200, 20),
    (400, 400, 150, 20),
    (200, 300, 100, 20),
    (500, 250, 200, 20),
    (100, 200, 150, 20),
    (600, 150, 100, 20),
]

for pos in platform_positions:
    platform = Platform(*pos)
    platforms.add(platform)
    all_sprites.add(platform)

# 创建敌人
for i in range(5):
    enemy = Enemy(random.randint(50, SCREEN_WIDTH-50), 
                  random.choice([450, 350, 250, 150]))
    enemies.add(enemy)
    all_sprites.add(enemy)

# 创建金币
for i in range(10):
    coin = Coin(random.randint(50, SCREEN_WIDTH-50), 
                random.randint(50, SCREEN_HEIGHT-100))
    coins.add(coin)
    all_sprites.add(coin)

# 创建MegaPixel特殊物品
for i in range(3):
    megapixel = MegaPixel(random.randint(50, SCREEN_WIDTH-50), 
                          random.randint(50, SCREEN_HEIGHT-150))
    megapixels.add(megapixel)
    all_sprites.add(megapixel)

# 游戏状态
game_over = False
game_won = False

# 游戏主循环
running = True
while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_r and game_over:
                game_over = False
                game_won = False
                player.health = 100
                player.coins = 0
                player.rect.x = SCREEN_WIDTH // 2
                player.rect.y = SCREEN_HEIGHT // 2
                player.jumping = False
                player.jump_velocity = 0
                player.invincible = 0
                
                for enemy in enemies:
                    enemy.kill()
                for coin in coins:
                    coin.kill()
                for megapixel in megapixels:
                    megapixel.kill()
                    
                for i in range(5):
                    enemy = Enemy(random.randint(50, SCREEN_WIDTH-50), 
                                  random.choice([450, 350, 250, 150]))
                    enemies.add(enemy)
                    all_sprites.add(enemy)
                    
                for i in range(10):
                    coin = Coin(random.randint(50, SCREEN_WIDTH-50), 
                                random.randint(50, SCREEN_HEIGHT-100))
                    coins.add(coin)
                    all_sprites.add(coin)
                    
                for i in range(3):
                    megapixel = MegaPixel(random.randint(50, SCREEN_WIDTH-50), 
                                          random.randint(50, SCREEN_HEIGHT-150))
                    megapixels.add(megapixel)
                    all_sprites.add(megapixel)
    
    if not game_over:
        player.update(platforms, enemies, coins, megapixels)
        enemies.update(platforms)
        coins.update()
        megapixels.update()
        
        if player.health <= 0:
            game_over = True
            game_won = False
        if player.coins >= 30:
            game_over = True
            game_won = True
    
    screen.fill((135, 206, 235))
    
    for i in range(0, SCREEN_WIDTH, 100):
        for j in range(0, 100, 20):
            pygame.draw.rect(screen, WHITE, (i + j, 50 + j//5, 80, 20))
    
    all_sprites.draw(screen)
    
    player.draw_health_bar(screen)
    
    health_text = ui_font.render(f"生命值: {player.health}", True, WHITE)
    coins_text = ui_font.render(f"金币: {player.coins}/30", True, WHITE)
    screen.blit(health_text, (10, 10))
    screen.blit(coins_text, (10, 50))
    
    copyright_text = small_font.render("MegaPixel - 版权所有 © 2023 赵瀚", True, WHITE)
    screen.blit(copyright_text, (SCREEN_WIDTH - copyright_text.get_width() - 10, 10))
    
    controls_text = small_font.render("方向键/WASD移动, 空格/上箭头/W跳跃, R重新开始, ESC退出", True, WHITE)
    screen.blit(controls_text, (SCREEN_WIDTH//2 - controls_text.get_width()//2, SCREEN_HEIGHT - 40))
    
    if len(megapixels) > 0:
        mega_text = ui_font.render("收集紫色MegaPixel获得额外奖励!", True, PURPLE)
        screen.blit(mega_text, (SCREEN_WIDTH//2 - mega_text.get_width()//2, 80))
    
    if game_over:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        if not game_won:
            game_over_text = title_font.render("游戏结束!", True, RED)
            restart_text = ui_font.render("按R重新开始", True, WHITE)
        else:
            game_over_text = title_font.render("恭喜获胜!", True, GREEN)
            restart_text = ui_font.render("你收集了所有MegaPixel! 按R重新开始", True, WHITE)
            
        screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 10))
    
    pygame.display.flip()

pygame.quit()
sys.exit()
