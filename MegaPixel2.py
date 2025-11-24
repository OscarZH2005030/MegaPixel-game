import pygame
import random
import math
import sys
import os

# 初始化 Pygame
pygame.init()
pygame.mixer.init()

# 游戏常量
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
TILE_SIZE = 48
FPS = 60

# 颜色定义
BACKGROUND = (25, 25, 50)
UI_BACKGROUND = (40, 40, 80, 200)
UI_BOTTOM_BACKGROUND = (30, 30, 60, 220)
PLAYER_BLUE = (65, 105, 225)
PLAYER_ACCENT = (100, 149, 237)
ENEMY_RED = (220, 20, 60)
ENEMY_ACCENT = (255, 99, 71)
COIN_YELLOW = (255, 215, 0)
COIN_GLOW = (255, 255, 100)
MEGAPIXEL_PURPLE = (138, 43, 226)
MEGAPIXEL_GLOW = (186, 85, 211)
PLATFORM_COLOR = (101, 67, 33)
PLATFORM_HIGHLIGHT = (139, 115, 85)
TEXT_COLOR = (240, 240, 255)
UI_ACCENT = (70, 130, 180)
BUTTON_COLOR = (80, 80, 120)
BUTTON_HOVER = (100, 100, 150)
VICTORY_GOLD = (255, 215, 0)
DEFEAT_RED = (200, 0, 0)

# 创建游戏窗口
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("MegaPixel v2.0 - 版权所有 © 2025 赵瀚")
clock = pygame.time.Clock()

# 创建字体
try:
    title_font = pygame.font.Font(None, 64)
    large_font = pygame.font.Font(None, 48)
    medium_font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    tiny_font = pygame.font.Font(None, 18)
except:
    title_font = pygame.font.SysFont("arial", 64, bold=True)
    large_font = pygame.font.SysFont("arial", 48)
    medium_font = pygame.font.SysFont("arial", 36)
    small_font = pygame.font.SysFont("arial", 24)
    tiny_font = pygame.font.SysFont("arial", 18)

# 音效系统
class SoundSystem:
    def __init__(self):
        self.sounds = {}
        self.music_playing = False
        self.load_sounds()
        
    def load_sounds(self):
        # 尝试创建简单的音效
        try:
            # 跳跃音效
            self.sounds['jump'] = self.create_beep_sound(523, 100)
            # 收集金币音效
            self.sounds['coin'] = self.create_beep_sound(659, 150)
            # 收集MegaPixel音效
            self.sounds['megapixel'] = self.create_beep_sound(784, 200)
            # 击败敌人音效
            self.sounds['enemy'] = self.create_beep_sound(392, 100)
            # 受伤音效
            self.sounds['hurt'] = self.create_beep_sound(220, 200)
            # 胜利音效
            self.sounds['victory'] = self.create_victory_sound()
            # 失败音效
            self.sounds['defeat'] = self.create_defeat_sound()
            
            # 设置音量
            for sound in self.sounds.values():
                sound.set_volume(0.5)
                
        except Exception as e:
            print(f"音效创建失败: {e}")
            # 创建空的音效作为备用
            for key in ['jump', 'coin', 'megapixel', 'enemy', 'hurt', 'victory', 'defeat']:
                self.sounds[key] = pygame.mixer.Sound(bytes(0))
    
    def create_beep_sound(self, frequency, duration):
        # 创建一个简单的正弦波音效
        sample_rate = 44100
        n_samples = int(round(duration * 0.001 * sample_rate))
        buf = bytearray()
        
        for i in range(n_samples):
            # 简单的正弦波
            sample = int(127 * math.sin(2 * math.pi * frequency * i / sample_rate) + 128)
            buf.append(sample)
            buf.append(sample)  # 立体声
        
        return pygame.mixer.Sound(bytes(buf))
    
    def create_victory_sound(self):
        # 胜利音效 - 上升的音阶
        sample_rate = 44100
        buf = bytearray()
        
        # 创建上升的音阶
        for freq in [523, 659, 784, 1047]:  # C5, E5, G5, C6
            n_samples = int(round(100 * 0.001 * sample_rate))
            for i in range(n_samples):
                sample = int(127 * math.sin(2 * math.pi * freq * i / sample_rate) + 128)
                buf.append(sample)
                buf.append(sample)
        
        return pygame.mixer.Sound(bytes(buf))
    
    def create_defeat_sound(self):
        # 失败音效 - 下降的音阶
        sample_rate = 44100
        buf = bytearray()
        
        # 创建下降的音阶
        for freq in [523, 392, 330, 262]:  # C5, G4, E4, C4
            n_samples = int(round(150 * 0.001 * sample_rate))
            for i in range(n_samples):
                sample = int(127 * math.sin(2 * math.pi * freq * i / sample_rate) + 128)
                buf.append(sample)
                buf.append(sample)
        
        return pygame.mixer.Sound(bytes(buf))
    
    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def play_background_music(self):
        # 尝试播放背景音乐
        try:
            # 创建一个简单的背景音乐循环
            if not self.music_playing:
                # 这里可以添加实际的音乐文件，现在使用静音
                self.music_playing = True
        except:
            pass

# 玩家类
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, sound_system):
        super().__init__()
        self.sound_system = sound_system
        
        # 创建更精细的像素风格角色
        self.base_image = pygame.Surface((TILE_SIZE, TILE_SIZE * 2), pygame.SRCALPHA)
        
        # 绘制角色身体
        pygame.draw.rect(self.base_image, PLAYER_BLUE, (4, TILE_SIZE//2, TILE_SIZE-8, TILE_SIZE))
        pygame.draw.rect(self.base_image, PLAYER_ACCENT, (8, TILE_SIZE//2+4, TILE_SIZE-16, TILE_SIZE-8))
        
        # 绘制头部
        pygame.draw.rect(self.base_image, (255, 220, 177), (8, 4, TILE_SIZE-16, TILE_SIZE//2))
        
        # 绘制面部特征
        pygame.draw.rect(self.base_image, (0, 0, 0), (TILE_SIZE//3, 16, 4, 4))
        pygame.draw.rect(self.base_image, (0, 0, 0), (2*TILE_SIZE//3, 16, 4, 4))
        pygame.draw.rect(self.base_image, (0, 0, 0), (TILE_SIZE//2-6, 28, 12, 3))
        
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # 物理属性
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 6
        self.jump_power = 16
        self.gravity = 0.8
        self.max_fall_speed = 12
        
        # 游戏属性
        self.health = 100
        self.max_health = 100
        self.coins = 0
        self.direction = 1  # 1 for right, -1 for left
        self.on_ground = False
        self.invincible = 0
        self.invincible_flash = 0
        
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # 水平移动
        self.velocity_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -self.speed
            self.direction = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = self.speed
            self.direction = 1
            
        # 跳跃
        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.velocity_y = -self.jump_power
            self.on_ground = False
            self.sound_system.play_sound('jump')
            
    def update(self, platforms, enemies, coins, megapixels):
        # 处理输入
        self.handle_input()
        
        # 应用重力
        self.velocity_y += self.gravity
        if self.velocity_y > self.max_fall_speed:
            self.velocity_y = self.max_fall_speed
            
        # 更新位置
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
        # 屏幕边界检查
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity_y = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.on_ground = True
            self.velocity_y = 0
            
        # 平台碰撞检测
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # 从上方落在平台上
                if (self.velocity_y > 0 and 
                    self.rect.bottom > platform.rect.top and 
                    self.rect.top < platform.rect.top):
                    self.rect.bottom = platform.rect.top
                    self.on_ground = True
                    self.velocity_y = 0
                # 从下方碰到平台
                elif (self.velocity_y < 0 and 
                      self.rect.top < platform.rect.bottom and 
                      self.rect.bottom > platform.rect.bottom):
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0
                # 水平碰撞
                elif self.velocity_x > 0 and self.rect.right > platform.rect.left and self.rect.left < platform.rect.left:
                    self.rect.right = platform.rect.left
                elif self.velocity_x < 0 and self.rect.left < platform.rect.right and self.rect.right > platform.rect.right:
                    self.rect.left = platform.rect.right
        
        # 敌人碰撞检测
        if self.invincible <= 0:
            for enemy in enemies:
                if self.rect.colliderect(enemy.rect):
                    # 从上方跳到敌人头上
                    if self.velocity_y > 0 and self.rect.bottom <= enemy.rect.top + 10:
                        enemy.kill()
                        self.velocity_y = -self.jump_power * 0.7  # 反弹
                        self.coins += 5
                        self.sound_system.play_sound('enemy')
                    else:
                        self.health -= 15
                        self.invincible = 60  # 1秒无敌时间
                        self.sound_system.play_sound('hurt')
                        # 击退效果
                        if self.rect.centerx < enemy.rect.centerx:
                            self.velocity_x = -8
                        else:
                            self.velocity_x = 8
                        self.velocity_y = -5
        
        # 收集金币
        for coin in coins:
            if self.rect.colliderect(coin.rect):
                coin.kill()
                self.coins += 1
                self.sound_system.play_sound('coin')
                
        # 收集MegaPixel特殊物品
        for megapixel in megapixels:
            if self.rect.colliderect(megapixel.rect):
                megapixel.kill()
                self.coins += 10
                self.health = min(self.max_health, self.health + 25)
                self.sound_system.play_sound('megapixel')
        
        # 无敌时间处理
        if self.invincible > 0:
            self.invincible -= 1
            self.invincible_flash = (self.invincible_flash + 1) % 10
            
        # 更新角色图像（考虑方向和无敌闪烁）
        self.image = self.base_image.copy()
        if self.direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)
            
        if self.invincible > 0 and self.invincible_flash < 5:
            # 创建半透明效果
            alpha_surface = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            alpha_surface.fill((255, 255, 255, 128))
            self.image.blit(alpha_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # 确保生命值不会低于0
        if self.health <= 0:
            self.health = 0

# 平台类
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, platform_type="normal"):
        super().__init__()
        self.image = pygame.Surface((width, height))
        
        # 根据平台类型选择颜色
        if platform_type == "normal":
            base_color = PLATFORM_COLOR
            highlight_color = PLATFORM_HIGHLIGHT
        else:
            base_color = (80, 80, 120)
            highlight_color = (120, 120, 160)
            
        # 绘制平台顶部
        self.image.fill(base_color)
        pygame.draw.rect(self.image, highlight_color, (0, 0, width, 4))
        
        # 添加平台纹理
        for i in range(0, width, 8):
            pygame.draw.line(self.image, highlight_color, (i, 4), (i, height), 1)
            
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# 敌人类
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        
        # 绘制敌人身体
        pygame.draw.rect(self.image, ENEMY_RED, (4, 4, TILE_SIZE-8, TILE_SIZE-8))
        pygame.draw.rect(self.image, ENEMY_ACCENT, (8, 8, TILE_SIZE-16, TILE_SIZE-16))
        
        # 绘制眼睛
        pygame.draw.rect(self.image, (255, 255, 255), (12, 12, 6, 6))
        pygame.draw.rect(self.image, (255, 255, 255), (TILE_SIZE-18, 12, 6, 6))
        pygame.draw.rect(self.image, (0, 0, 0), (14, 14, 2, 2))
        pygame.draw.rect(self.image, (0, 0, 0), (TILE_SIZE-16, 14, 2, 2))
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.speed = random.choice([-2, -1, 1, 2])
        self.direction = 1 if self.speed > 0 else -1
        
    def update(self, *args):
        # 只使用第一个参数（platforms），忽略其他参数
        platforms = args[0] if args else []
        
        self.rect.x += self.speed
        
        # 平台边缘检测
        on_platform = False
        for platform in platforms:
            if (self.rect.bottom == platform.rect.top and 
                self.rect.right > platform.rect.left and 
                self.rect.left < platform.rect.right):
                on_platform = True
                
                # 检查是否在平台边缘
                if (self.speed > 0 and self.rect.right >= platform.rect.right - 5) or \
                   (self.speed < 0 and self.rect.left <= platform.rect.left + 5):
                    self.speed *= -1
                    self.direction *= -1
                break
                
        # 如果不在平台上，转向
        if not on_platform:
            self.speed *= -1
            self.direction *= -1
            
        # 屏幕边界检查
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speed *= -1
            self.direction *= -1

# 金币类
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE//2, TILE_SIZE//2), pygame.SRCALPHA)
        
        # 绘制金币
        pygame.draw.circle(self.image, COIN_YELLOW, (TILE_SIZE//4, TILE_SIZE//4), TILE_SIZE//4)
        pygame.draw.circle(self.image, COIN_GLOW, (TILE_SIZE//4, TILE_SIZE//4), TILE_SIZE//6)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.float_offset = random.random() * 2 * math.pi
        self.rotation = 0
        
    def update(self, *args):
        # 忽略所有参数
        # 浮动效果
        self.rect.y += math.sin(pygame.time.get_ticks() / 300 + self.float_offset) * 0.8
        
        # 旋转效果
        self.rotation = (self.rotation + 2) % 360
        orig_rect = self.image.get_rect()
        rotated_image = pygame.transform.rotate(self.image, self.rotation)
        rot_rect = orig_rect.copy()
        rot_rect.center = rotated_image.get_rect().center
        self.image = rotated_image.subsurface(rot_rect).copy()

# MegaPixel 特殊物品类
class MegaPixel(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.base_size = TILE_SIZE
        self.image = pygame.Surface((self.base_size, self.base_size), pygame.SRCALPHA)
        
        # 绘制MegaPixel
        pygame.draw.rect(self.image, MEGAPIXEL_PURPLE, (0, 0, self.base_size, self.base_size))
        pygame.draw.rect(self.image, (160, 60, 220), (4, 4, self.base_size-8, self.base_size-8))
        pygame.draw.rect(self.image, MEGAPIXEL_GLOW, (8, 8, self.base_size-16, self.base_size-16))
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.float_offset = random.random() * 2 * math.pi
        self.pulse_timer = 0
        
    def update(self, *args):
        # 忽略所有参数
        # 浮动效果
        self.rect.y += math.sin(pygame.time.get_ticks() / 250 + self.float_offset) * 1.2
        
        # 脉动效果
        self.pulse_timer += 1
        pulse_size = math.sin(self.pulse_timer / 10) * 4
        
        # 重新绘制带有脉动效果的MegaPixel
        self.image = pygame.Surface((self.base_size + int(pulse_size)*2, 
                                   self.base_size + int(pulse_size)*2), pygame.SRCALPHA)
        
        # 绘制发光效果
        pygame.draw.rect(self.image, (*MEGAPIXEL_GLOW[:3], 100), 
                        (0, 0, self.base_size + int(pulse_size)*2, self.base_size + int(pulse_size)*2))
        
        # 绘制MegaPixel核心
        pygame.draw.rect(self.image, MEGAPIXEL_PURPLE, 
                        (pulse_size, pulse_size, self.base_size, self.base_size))
        pygame.draw.rect(self.image, (160, 60, 220), 
                        (pulse_size+4, pulse_size+4, self.base_size-8, self.base_size-8))
        pygame.draw.rect(self.image, MEGAPIXEL_GLOW, 
                        (pulse_size+8, pulse_size+8, self.base_size-16, self.base_size-16))

# 创建背景星星
def create_stars(count):
    stars = []
    for _ in range(count):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        size = random.choice([1, 1, 1, 2, 2, 3])
        brightness = random.randint(150, 255)
        stars.append((x, y, size, brightness))
    return stars

# 初始化游戏
def init_game(sound_system):
    # 创建精灵组
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    megapixels = pygame.sprite.Group()
    
    # 创建玩家
    player = Player(SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2, sound_system)
    all_sprites.add(player)
    
    # 创建平台
    platform_data = [
        (0, SCREEN_HEIGHT - 60, SCREEN_WIDTH, 60, "ground"),
        (200, 600, 300, 20, "normal"),
        (600, 500, 200, 20, "normal"),
        (150, 400, 250, 20, "normal"),
        (500, 350, 180, 20, "normal"),
        (800, 300, 150, 20, "normal"),
        (300, 250, 200, 20, "normal"),
        (700, 200, 180, 20, "normal"),
        (100, 150, 150, 20, "normal"),
    ]
    
    for data in platform_data:
        platform = Platform(*data)
        platforms.add(platform)
        all_sprites.add(platform)
    
    # 创建敌人
    for i in range(6):
        x = random.randint(100, SCREEN_WIDTH - 100)
        y = random.choice([550, 450, 350, 250])
        enemy = Enemy(x, y)
        enemies.add(enemy)
        all_sprites.add(enemy)
    
    # 创建金币
    for i in range(15):
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = random.randint(50, SCREEN_HEIGHT - 100)
        coin = Coin(x, y)
        coins.add(coin)
        all_sprites.add(coin)
    
    # 创建MegaPixel物品
    for i in range(4):
        x = random.randint(100, SCREEN_WIDTH - 100)
        y = random.randint(100, SCREEN_HEIGHT - 200)
        megapixel = MegaPixel(x, y)
        megapixels.add(megapixel)
        all_sprites.add(megapixel)
    
    return all_sprites, platforms, enemies, coins, megapixels, player

# 创建顶部UI元素
def draw_top_ui(screen, player):
    # 绘制半透明UI背景
    ui_bg = pygame.Surface((SCREEN_WIDTH, 80), pygame.SRCALPHA)
    ui_bg.fill(UI_BACKGROUND)
    screen.blit(ui_bg, (0, 0))
    
    # 绘制生命值条
    health_bar_width = 300
    health_bar_height = 25
    health_fill = (player.health / player.max_health) * health_bar_width
    
    # 生命值条背景
    pygame.draw.rect(screen, (60, 60, 80), (20, 20, health_bar_width, health_bar_height), border_radius=5)
    # 生命值条填充
    pygame.draw.rect(screen, (50, 200, 100), (20, 20, health_fill, health_bar_height), border_radius=5)
    # 生命值条边框
    pygame.draw.rect(screen, UI_ACCENT, (20, 20, health_bar_width, health_bar_height), 2, border_radius=5)
    
    # 生命值文本
    health_text = medium_font.render(f"{player.health}/{player.max_health}", True, TEXT_COLOR)
    screen.blit(health_text, (25, 25))
    
    # 金币计数
    coins_text = medium_font.render(f"金币: {player.coins}/50", True, TEXT_COLOR)
    screen.blit(coins_text, (SCREEN_WIDTH - coins_text.get_width() - 20, 25))
    
    # 游戏标题
    title_text = small_font.render("MegaPixel v2.0", True, TEXT_COLOR)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 25))

# 创建底部菜单
def draw_bottom_menu(screen):
    # 绘制底部菜单背景
    bottom_bg = pygame.Surface((SCREEN_WIDTH, 60), pygame.SRCALPHA)
    bottom_bg.fill(UI_BOTTOM_BACKGROUND)
    screen.blit(bottom_bg, (0, SCREEN_HEIGHT - 60))
    
    # 绘制控制说明
    controls_text = small_font.render("移动: WASD/方向键 | 跳跃: 空格/W/上箭头", True, TEXT_COLOR)
    screen.blit(controls_text, (20, SCREEN_HEIGHT - 45))
    
    # 绘制按钮说明
    button_text = small_font.render("R - 重新开始 | ESC - 退出游戏", True, TEXT_COLOR)
    screen.blit(button_text, (SCREEN_WIDTH - button_text.get_width() - 20, SCREEN_HEIGHT - 45))
    
    # 绘制版本信息
    version_text = tiny_font.render("MegaPixel 版本: 2.0 | 版权所有 © 2025 赵瀚", True, TEXT_COLOR)
    screen.blit(version_text, (SCREEN_WIDTH // 2 - version_text.get_width() // 2, SCREEN_HEIGHT - 25))
    
    # 绘制底部装饰线
    pygame.draw.line(screen, UI_ACCENT, (0, SCREEN_HEIGHT - 60), (SCREEN_WIDTH, SCREEN_HEIGHT - 60), 2)

# 创建胜利界面
def draw_victory_screen(screen, player):
    # 创建半透明覆盖层
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # 绘制胜利框
    victory_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 150, 600, 300)
    pygame.draw.rect(screen, (40, 40, 80, 240), victory_rect, border_radius=20)
    pygame.draw.rect(screen, VICTORY_GOLD, victory_rect, 4, border_radius=20)
    
    # 绘制胜利标题
    victory_text = title_font.render("胜利!", True, VICTORY_GOLD)
    screen.blit(victory_text, (SCREEN_WIDTH//2 - victory_text.get_width()//2, SCREEN_HEIGHT//2 - 120))
    
    # 绘制分数
    score_text = large_font.render(f"得分: {player.coins}", True, TEXT_COLOR)
    screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 - 40))
    
    # 绘制胜利图标
    pygame.draw.circle(screen, VICTORY_GOLD, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40), 40, 6)
    pygame.draw.polygon(screen, VICTORY_GOLD, [
        (SCREEN_WIDTH//2 - 20, SCREEN_HEIGHT//2 + 20),
        (SCREEN_WIDTH//2 - 5, SCREEN_HEIGHT//2 + 40),
        (SCREEN_WIDTH//2 + 25, SCREEN_HEIGHT//2 + 10)
    ])

# 创建失败界面
def draw_defeat_screen(screen, player):
    # 创建半透明覆盖层
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    # 绘制失败框
    defeat_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 150, 600, 300)
    pygame.draw.rect(screen, (60, 40, 40, 240), defeat_rect, border_radius=20)
    pygame.draw.rect(screen, DEFEAT_RED, defeat_rect, 4, border_radius=20)
    
    # 绘制失败标题
    defeat_text = title_font.render("你tm输了", True, DEFEAT_RED)
    screen.blit(defeat_text, (SCREEN_WIDTH//2 - defeat_text.get_width()//2, SCREEN_HEIGHT//2 - 120))
    
    # 绘制分数
    score_text = large_font.render(f"得分: {player.coins}", True, TEXT_COLOR)
    screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 - 40))
    
    # 绘制失败图标
    pygame.draw.circle(screen, DEFEAT_RED, (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40), 40, 6)
    pygame.draw.line(screen, DEFEAT_RED, 
                    (SCREEN_WIDTH//2 - 25, SCREEN_HEIGHT//2 + 15),
                    (SCREEN_WIDTH//2 + 25, SCREEN_HEIGHT//2 + 65), 8)
    pygame.draw.line(screen, DEFEAT_RED, 
                    (SCREEN_WIDTH//2 + 25, SCREEN_HEIGHT//2 + 15),
                    (SCREEN_WIDTH//2 - 25, SCREEN_HEIGHT//2 + 65), 8)

# 主游戏函数
def main():
    # 初始化音效系统
    sound_system = SoundSystem()
    
    # 初始化游戏
    all_sprites, platforms, enemies, coins, megapixels, player = init_game(sound_system)
    stars = create_stars(100)
    
    # 游戏状态
    game_over = False
    game_won = False
    victory_sound_played = False
    defeat_sound_played = False
    running = True
    
    # 游戏主循环
    while running:
        # 控制游戏速度
        clock.tick(FPS)
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    # 重新开始游戏
                    all_sprites, platforms, enemies, coins, megapixels, player = init_game(sound_system)
                    game_over = False
                    game_won = False
                    victory_sound_played = False
                    defeat_sound_played = False
        
        if not game_over:
            # 分别更新不同类型的精灵
            player.update(platforms, enemies, coins, megapixels)
            
            # 更新敌人
            for enemy in enemies:
                enemy.update(platforms)
            
            # 更新金币
            for coin in coins:
                coin.update()
            
            # 更新MegaPixel
            for megapixel in megapixels:
                megapixel.update()
            
            # 检查游戏结束条件
            if player.health <= 0:
                game_over = True
                game_won = False
                if not defeat_sound_played:
                    sound_system.play_sound('defeat')
                    defeat_sound_played = True
                    
            if player.coins >= 50:
                game_over = True
                game_won = True
                if not victory_sound_played:
                    sound_system.play_sound('victory')
                    victory_sound_played = True
        
        # 绘制
        screen.fill(BACKGROUND)
        
        # 绘制星星
        for star in stars:
            x, y, size, brightness = star
            color = (brightness, brightness, brightness)
            pygame.draw.circle(screen, color, (x, y), size)
        
        # 绘制所有精灵
        all_sprites.draw(screen)
        
        # 绘制UI
        draw_top_ui(screen, player)
        draw_bottom_menu(screen)
        
        # 绘制游戏结束画面
        if game_over:
            if game_won:
                draw_victory_screen(screen, player)
            else:
                draw_defeat_screen(screen, player)
        
        # 更新显示
        pygame.display.flip()
    
    # 退出游戏
    pygame.quit()
    sys.exit()

# 运行游戏
if __name__ == "__main__":
    main()
