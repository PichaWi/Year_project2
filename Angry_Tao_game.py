import pygame as pg
import random as ra
import math as math
from Tao_config import Config

BULLET_COLORS = {
    "Normal": (128, 128, 128),    # Gray
    "Spread": (0, 200, 0),        # Green
    "Shotgun": (220, 0, 0),       # Red
    "Sniper": (255, 255, 255),    # White
    "Explosive": (255, 140, 0),   # Orange
}

class Obstacle(pg.sprite.Sprite):
    def __init__(self, x, y, material):
        super().__init__()
        self.image = pg.Surface([Config.obstacle_size, Config.obstacle_size])
        self.material = material
        self.color = Config.game_color.get(material.upper(), Config.game_color['LIGHTGRAY'])
        self.image.fill(self.color)
        border_color = (0, 0, 0)  
        border_thickness = 2
        pg.draw.rect(self.image, border_color, self.image.get_rect(), border_thickness)
        
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.health = self.get_health(material)

    def get_health(self, material):
        if material.lower() == 'glass':
            return 1
        elif material.lower() == 'wood':
            return 3
        elif material.lower() == 'iron':
            return 5
        elif material.lower() == 'diamond':
            return 8
        elif material.lower() == 'gold':
            return 4
        elif material.lower() == 'bomb':
            return 1
        elif material.lower() == 'vibranium':
            return 10
        else:
            return 2

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            exploded = self.material.lower() == 'bomb'
            self.kill()
            return exploded
        return False

class Enemy(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        original_image = pg.image.load("image/Enemy.png").convert_alpha()
        desired_width, desired_height = 50, 50
        self.image = pg.transform.scale(original_image, (desired_width, desired_height))        
        self.rect = self.image.get_rect(center=(x, y))
        self.health = 2

    def update(self):
        pass

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()
            return True
        return False

class Civilian(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.image.load("image/civilian.webp").convert_alpha()
        desired_width, desired_height = Config.enemy_size, Config.enemy_size * 2
        self.image = pg.transform.scale(self.image, (desired_width, desired_height))
        self.rect = self.image.get_rect(center=(x, y))
        self.health = 1
        self.move_timer = ra.randint(30, 120)
        self.direction = ra.choice([-1, 0, 1]), ra.choice([-1, 0, 1])

    def update(self):
        self.move_timer -= 1
        if self.move_timer <= 0:
            self.direction = ra.choice([-1, 0, 1]), ra.choice([-1, 0, 1])
            self.move_timer = ra.randint(30, 120)
        dx, dy = self.direction
        self.rect.x += dx
        self.rect.y += dy
        self.rect.clamp_ip(pg.Rect(Config.stage_side_width, 100, Config.stage_middle_width, Config.stage_height))

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()
            return True
        return False

class Stage:
    def __init__(self, stage_number=1):
        self.stage_number = stage_number
        self.stage_obstacles = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.civilians = pg.sprite.Group()
        self.generate_level()
        self.border_rect = pg.Rect(Config.stage_side_width, 100, Config.stage_middle_width, Config.stage_height)

    def generate_level(self):
        base_obstacles = 6
        base_civilians = 1

        num_obstacles = min(base_obstacles + self.stage_number, 15)
        num_civilians = min(base_civilians + self.stage_number // 2, 10)

        obstacle_materials = ['glass', 'wood', 'iron', 'diamond', 'gold', 'bomb', 'vibranium']
        attempts = 0
        while len(self.stage_obstacles) < num_obstacles and attempts < 300:
            material = ra.choice(obstacle_materials)
            x = ra.randint(Config.stage_side_width,
                           Config.stage_side_width + Config.stage_middle_width - Config.obstacle_size)
            y = ra.randint(100,
                           100 + Config.stage_height - Config.obstacle_size)
            new_rect = pg.Rect(x, y, Config.obstacle_size, Config.obstacle_size)
            if not any(ob.rect.colliderect(new_rect) for ob in self.stage_obstacles):
                self.stage_obstacles.add(Obstacle(x, y, material))
            attempts += 1

        num_enemies = ra.randint(2, 4)
        attempts = 0
        portal_h = 20
        min_y = 100 + portal_h + Config.enemy_size // 2 + 10
        max_y = 100 + Config.stage_height - portal_h - Config.enemy_size // 2 - 10
        while len(self.enemies) < num_enemies and attempts < 200:
            x = ra.randint(Config.stage_side_width + Config.enemy_size // 2,
                           Config.stage_side_width + Config.stage_middle_width - Config.enemy_size // 2)
            y = ra.randint(min_y, max_y)
            new_rect = pg.Rect(x - Config.enemy_size // 2, y - Config.enemy_size // 2, Config.enemy_size, Config.enemy_size)
            if not any(ob.rect.colliderect(new_rect) for ob in self.stage_obstacles) and \
               not any(en.rect.colliderect(new_rect) for en in self.enemies):
                self.enemies.add(Enemy(x, y))
            attempts += 1

        attempts = 0
        while len(self.civilians) < num_civilians and attempts < 300:
            x = ra.randint(Config.stage_side_width + Config.enemy_size // 2,
                           Config.stage_side_width + Config.stage_middle_width - Config.enemy_size // 2)
            y = ra.randint(min_y, max_y)
            new_rect = pg.Rect(x - Config.enemy_size // 2, y - Config.enemy_size // 2, Config.enemy_size, Config.enemy_size)
            if not any(ob.rect.colliderect(new_rect) for ob in self.stage_obstacles) and \
               not any(en.rect.colliderect(new_rect) for en in self.enemies) and \
               not any(civ.rect.colliderect(new_rect) for civ in self.civilians):
                self.civilians.add(Civilian(x, y))
            attempts += 1

    def check_stage_clear(self):
        return len(self.enemies) == 0

class Items:
    def __init__(self, name, skill, ammo, color_code):
        self.name = name
        self.skill = skill
        self.fixed_ammo = ammo
        self.max_ammo = ammo
        self.color_code = color_code

    def use_skill(self):
        if self.fixed_ammo > 0:
            self.fixed_ammo -= 1
            return True
        return False

class ExplosiveBlock(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        size = Config.obstacle_size * 2
        self.image = pg.Surface((size, size), pg.SRCALPHA)
        self.image.fill((255, 100, 0, 150))
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = 60  

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.kill()

class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y, direction, skill, speed=None, damage=1):
        super().__init__()
        self.image = pg.Surface([Config.bullet_radius * 2, Config.bullet_radius * 2], pg.SRCALPHA)
        color = BULLET_COLORS.get(skill.capitalize(), (255, 255, 0))  
        pg.draw.circle(self.image, color, (Config.bullet_radius, Config.bullet_radius), Config.bullet_radius)
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = speed if speed else Config.bullet_speed
        self.skill = skill
        self.damage = damage

    def update(self):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed
        if (self.rect.right < 0 or self.rect.left > Config.game_width or
            self.rect.bottom < 0 or self.rect.top > Config.game_height):
            self.kill()

class ExplosiveBullet(Bullet):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction, "EXPLOSIVE")
        self.speed = Config.bullet_speed * 0.8
        self.damage = 3

    def update(self):
        super().update()

    def explode(self, game, hit_pos):
        block = ExplosiveBlock(*hit_pos)
        game.explosive_blocks.add(block)
        self.kill()

class Character(pg.sprite.Sprite):
    def __init__(self, unlocked_weapons=None):
        super().__init__()
        self.image = pg.image.load("image/AngryTao.jpg").convert_alpha()
        desired_size = Config.character_radius * 2
        self.image = pg.transform.scale(self.image, (desired_size, desired_size))
        self.rect = self.image.get_rect()
    
        portal_x = Config.stage_side_width // 2
        spawn_y = Config.game_height // 2
        self.rect.center = (portal_x, spawn_y)
        
        if unlocked_weapons is None:
            unlocked_weapons = ["Normal"]
        self.items_list = []
        for skill in unlocked_weapons:
            if skill == "Normal":
                self.items_list.append(Items("Normal", "NORMAL", 50, "NORMAL"))
            elif skill == "Spread":
                self.items_list.append(Items("Spread", "SPREAD", 10, "SPREAD"))
            elif skill == "Shotgun":
                self.items_list.append(Items("Shotgun", "SHOTGUN", 15, "SHOTGUN"))
            elif skill == "Sniper":
                self.items_list.append(Items("Sniper", "SNIPER", 5, "SNIPER"))
            elif skill == "Explosive":
                self.items_list.append(Items("Explosive", "EXPLOSIVE", 5, "EXPLOSIVE"))
        self.current_item_index = 0
        self.bullets = pg.sprite.Group()
        self.score = 0
        self.movement_up = 0
        self.movement_down = 0
        self.missed_shots = 0
        self.shoot_cooldown = 0
        self.switch_cooldown = 0

    def move(self, dy):
        portal_h = 20
        top_limit = 100 + portal_h // 2 + Config.character_radius
        bottom_limit = 100 + Config.stage_height - portal_h // 2 - Config.character_radius

        self.rect.y += dy
        if self.rect.centery < top_limit:
            self.rect.centery = top_limit
        elif self.rect.centery > bottom_limit:
            self.rect.centery = bottom_limit
        if dy < 0:
            self.movement_up += 1
        elif dy > 0:
            self.movement_down += 1

    def switch_item(self, direction):
        if self.switch_cooldown > 0:
            return
        if len(self.items_list) > 1:
            self.current_item_index = (self.current_item_index + direction) % len(self.items_list)
            self.switch_cooldown = 10

    def shoot(self):
        if self.shoot_cooldown > 0:
            return False
        current_item = self.items_list[self.current_item_index]
        if not current_item.use_skill():
            return False

        middle_x = Config.stage_side_width + Config.stage_middle_width // 2
        direction = (1, 0) if self.rect.centerx < middle_x else (-1, 0)
        skill = current_item.skill

        if skill == "NORMAL":
            bullet = Bullet(self.rect.centerx, self.rect.centery, direction, "NORMAL")
            self.bullets.add(bullet)

        elif skill == "SPREAD":
            angles = [-15, -7.5, 0, 7.5, 15]
            for angle in angles:
                rad = math.radians(angle)
                dx = math.cos(rad) * direction[0] - math.sin(rad) * direction[1]
                dy = math.sin(rad) * direction[0] + math.cos(rad) * direction[1]
                bullet = Bullet(self.rect.centerx, self.rect.centery, (dx, dy), "SPREAD")
                self.bullets.add(bullet)

        elif skill == "SHOTGUN":
            offsets = [-15, 0, 15]
            for offset in offsets:
                bullet = Bullet(self.rect.centerx, self.rect.centery + offset, direction, "SHOTGUN")
                self.bullets.add(bullet)

        elif skill == "SNIPER":
            bullet = Bullet(self.rect.centerx, self.rect.centery, direction, "SNIPER", speed=Config.bullet_speed*1.5, damage=5)
            self.bullets.add(bullet)

        elif skill == "EXPLOSIVE":
            bullet = ExplosiveBullet(self.rect.centerx, self.rect.centery, direction)
            self.bullets.add(bullet)

        else:
            bullet = Bullet(self.rect.centerx, self.rect.centery, direction, "NORMAL")
            self.bullets.add(bullet)

        self.shoot_cooldown = 10
        return True

    def update_cooldown(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.switch_cooldown > 0:
            self.switch_cooldown -= 1

    def all_ammo_empty(self):
        return all(item.fixed_ammo <= 0 for item in self.items_list)

class Drawer:
    def __init__(self, screen):
        self.screen = screen

    def draw_stage(self, stage):
        pg.draw.rect(self.screen, Config.game_color['BORDER'], stage.border_rect, 5)
        for obstacle in stage.stage_obstacles:
            self.screen.blit(obstacle.image, obstacle.rect)

    def draw_character(self, character):
        self.screen.blit(character.image, character.rect)

    def draw_bullets(self, character):
        character.bullets.draw(self.screen)

    def draw_enemies(self, stage):
        for enemy in stage.enemies:
            self.screen.blit(enemy.image, enemy.rect)
        for civ in stage.civilians:
            self.screen.blit(civ.image, civ.rect)

    def draw_portals(self, character):
        portal_color = (0, 255, 255)
        portal_w, portal_h = 40, 20

        left_x = Config.stage_side_width // 2
        right_x = Config.stage_side_width + Config.stage_middle_width + (Config.stage_side_width // 2)

        pg.draw.rect(self.screen, portal_color, (left_x - portal_w // 2, 100, portal_w, portal_h))
        pg.draw.rect(self.screen, portal_color, (left_x - portal_w // 2, 100 + Config.stage_height - portal_h, portal_w, portal_h))

        pg.draw.rect(self.screen, portal_color, (right_x - portal_w // 2, 100, portal_w, portal_h))
        pg.draw.rect(self.screen, portal_color, (right_x - portal_w // 2, 100 + Config.stage_height - portal_h, portal_w, portal_h))

    def draw_portal_lines(self):
        portal_h = 20
        y_top = 100 + portal_h // 2
        y_bottom = 100 + Config.stage_height - portal_h // 2
        pg.draw.line(self.screen, (255, 255, 255), (0, y_top), (Config.game_width, y_top), 3)
        pg.draw.line(self.screen, (255, 255, 255), (0, y_bottom), (Config.game_width, y_bottom), 3)

    def draw_explosive_blocks(self, blocks):
        blocks.draw(self.screen)

class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pg.font.Font(None, 36)

    def draw_text(self, text, pos, color=(255, 255, 255)):
        rendered_text = self.font.render(text, True, color)
        self.screen.blit(rendered_text, pos)

    def draw_item_ui(self, character):
        x_offset = 20
        y_offset = Config.game_height - 50
        for i, item in enumerate(character.items_list):
            color = Config.game_color.get(item.color_code.upper(), Config.game_color['LIGHTGRAY'])
            pg.draw.rect(self.screen, color, (x_offset + i * 60, y_offset, 50, 30))
            ammo_text = f"{item.fixed_ammo}/{item.max_ammo}"
            self.draw_text(ammo_text, (x_offset + i * 60, y_offset + 30), (255, 255, 255))
        current_item_text = f"Current Item: {character.items_list[character.current_item_index].name}"
        self.draw_text(current_item_text, (20, Config.game_height - 80))

    def draw_score(self, character):
        score_text = f"Score: {character.score}"
        self.draw_text(score_text, (Config.game_width - 200, 20))
