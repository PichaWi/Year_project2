import pygame as pg
import random as ra
import math as a
import tkinter as tk
from Tao_config import Config

class Obstacle(pg.sprite.Sprite):
    def __init__(self, x, y, material):
        super().__init__()
        self.image = pg.Surface([Config.obstacle_size, Config.obstacle_size])
        self.material = material
        self.color = Config.game_color.get(material.upper(), Config.game_color['LIGHTGRAY'])
        self.image.fill(self.color)
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
            return 1 # Bomb will explode on hit
        elif material.lower() == 'vibranium':
            return 10
        else:
            return 2

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            if self.material.lower() == 'bomb':
                return True # Indicate explosion
            self.kill()
        return False

class Enemy(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.Surface([Config.enemy_size, Config.enemy_size])
        self.image.fill(Config.game_color['R'])
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.health = 2 # Example enemy health

    def update(self):
        # Basic enemy movement (you can make this more sophisticated)
        speed = 1
        if self.rect.centerx < Config.stage_side_width + Config.stage_middle_width // 2:
            self.rect.x += speed
        else:
            self.rect.x -= speed
        if self.rect.centery < 100 + Config.stage_height // 2:
            self.rect.y += speed
        else:
            self.rect.y -= speed

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill()
            return True
        return False

class Stage:
    """
    Handle enemy and obstacle location along with health and type for each of it
    """
    def __init__(self):
        self.health = 100
        self.name = "Stage 1"
        self.stage_obstacles = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.generate_level()
        self.border_rect = pg.Rect(Config.stage_side_width, 100, Config.stage_middle_width, Config.stage_height)

    def generate_level(self):
        num_obstacles = ra.randint(6, 7)
        obstacle_materials = ['glass', 'wood', 'iron', 'diamond', 'gold'] + ['bomb'] * 2 + ['vibranium'] * 1
        for _ in range(num_obstacles):
            material = ra.choice(obstacle_materials)
            x = ra.randint(Config.stage_side_width + Config.obstacle_size // 2,
                           Config.stage_side_width + Config.stage_middle_width - Config.obstacle_size // 2)
            y = ra.randint(100 + Config.obstacle_size // 2, 100 + Config.stage_height - Config.obstacle_size // 2)
            self.stage_obstacles.add(Obstacle(x, y, material))

        num_enemies = ra.randint(2, 4)
        for _ in range(num_enemies):
            x = ra.randint(Config.stage_side_width + Config.enemy_size // 2,
                           Config.stage_side_width + Config.stage_middle_width - Config.enemy_size // 2)
            y = ra.randint(100 + Config.enemy_size // 2, 100 + Config.stage_height - Config.enemy_size // 2)
            self.enemies.add(Enemy(x, y))

    def check_stage_clear(self):
        return not self.enemies

class Items:
    """
    Handle items skill, fixed ammo and information to provide for user to know
    """
    def __init__(self, name, skill, ammo, color_code):
        self.name = name
        self.skill = skill
        self.fixed_ammo = ammo
        self.max_ammo = ammo  # Store initial ammo
        self.color_code = color_code

    def use_skill(self):
        if self.fixed_ammo > 0:
            self.fixed_ammo -= 1
            return True # Indicate skill used
        return False # No ammo left

class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y, direction, skill):
        super().__init__()
        self.image = pg.Surface([Config.bullet_radius * 2, Config.bullet_radius * 2])
        self.image.fill(Config.game_color['BL'])
        pg.draw.circle(self.image, Config.game_color['BL'], (Config.bullet_radius, Config.bullet_radius), Config.bullet_radius)
        self.image = self.image.convert_alpha() # Make background transparent
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = Config.bullet_speed
        self.skill = skill
        self.game = game
        self.color = Config.skill_properties[skill]['color']
        
    def apply_skill_effect(self, target):
        if self.skill == 'SPREAD':
            self.handle_spread()
        elif self.skill == 'EXPLOSIVE':
            self.handle_explosive()
    
    def handle_spread(self):
        # Create 2 additional bullets at angles
        for angle in [-15, 15]:
            new_bullet = Bullet(self.rect.x, self.rect.y, 
                              self.direction, self.skill, self.game)
            new_bullet.rect.y += angle * 2
            self.game.character.bullets.add(new_bullet)
            
    def handle_explosive(self):
        # Damage all enemies in radius
        explosion_radius = 100
        for enemy in self.game.stage.enemies:
            if a.dist(enemy.rect.center, self.rect.center) < explosion_radius:
                enemy.take_damage(2)

    def update(self):
        self.rect.x += self.speed * self.direction
        # Check if bullet goes out of the stage box (excluding character sides)
        if self.direction > 0 and self.rect.left > Config.stage_side_width + Config.stage_middle_width:
            self.kill()
        elif self.direction < 0 and self.rect.right < Config.stage_side_width:
            self.kill()

class Character(pg.sprite.Sprite):
    """
    Handle character information and current situation of the character items, location and ammo of item
    """
    def __init__(self):
        super().__init__()
        self.image = pg.Surface([Config.character_radius * 2, Config.character_radius * 2])
        self.image.fill(Config.game_color['G'])
        pg.draw.circle(self.image, Config.game_color['G'], (Config.character_radius, Config.character_radius), Config.character_radius)
        self.rect = self.image.get_rect(center=(Config.game_width // 4, Config.game_height // 2)) # Spawn on left side
        self.items_list = [
            Items("Normal", "Normal Shot", 50, "NORMAL"),
            Items("Spread", "Triple Shot", 20, "SPREAD"),
            Items("Explosive", "Bomb Shot", 5, "EXPLOSIVE")
        ] # Initial item pool
        self.current_item_index = 0
        self.bullets = pg.sprite.Group()
        self.score = 0
        self.movement_up = 0
        self.movement_down = 0
        self.missed_shots = 0

    def move(self, dy):
        self.rect.y += dy
        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > Config.game_height:
            self.rect.bottom = Config.game_height
        if dy < 0:
            self.movement_up += 1
        elif dy > 0:
            self.movement_down += 1

    def switch_item(self, direction):
        self.current_item_index = (self.current_item_index + direction) % len(self.items_list)

    def shoot(self):
        current_item = self.items_list[self.current_item_index]
        if current_item.use_skill():
            direction = 1 if self.rect.centerx < Config.game_width // 2 else -1
            if current_item.skill == "Normal Shot":
                bullet = Bullet(self.rect.centerx, self.rect.centery, direction, "normal")
                self.bullets.add(bullet)
            elif current_item.skill == "Triple Shot":
                bullet1 = Bullet(self.rect.centerx, self.rect.centery - 10, direction, "normal")
                bullet2 = Bullet(self.rect.centerx, self.rect.centery, direction, "normal")
                bullet3 = Bullet(self.rect.centerx, self.rect.centery + 10, direction, "normal")
                self.bullets.add(bullet1, bullet2, bullet3)
            elif current_item.skill == "Bomb Shot":
                bullet = Bullet(self.rect.centerx, self.rect.centery, direction, "explosive")
                self.bullets.add(bullet)
            return True
        return False

class Drawer:
    """
    Handle drawing stage, character, enemy, obstacle and items look
    """
    def __init__(self, screen):
        self.screen = screen

    def draw_stage(self, stage):
        pg.draw.rect(self.screen, Config.game_color['BORDER'], stage.border_rect, 5) # Draw stage border
        for obstacle in stage.stage_obstacles:
            pg.draw.rect(self.screen, obstacle.color, obstacle.rect)

    def draw_character(self, character):
        self.screen.blit(character.image, character.rect)

    def draw_bullets(self, character):
        character.bullets.draw(self.screen)

    def draw_enemies(self, stage):
        for enemy in stage.enemies:
            pg.draw.rect(self.screen, Config.game_color['R'], enemy.rect)

class UI:
    """
    Handle UI of the game
    """
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode(
            (Config.game_width, Config.game_height))
        pg.display.set_caption("Angry Tao Project")
        self.clock = pg.time.Clock()
        self.font = pg.font.Font(None, 36)

    def draw_text(self, text, pos, color=Config.game_color['W']):
        rendered_text = self.font.render(text, True, color)
        self.screen.blit(rendered_text, pos)

    def draw_item_ui(self, character):
        x_offset = 20
        y_offset = Config.game_height - 50
        for i, item in enumerate(character.items_list):
            color = Config.game_color.get(item.color_code.upper(), Config.game_color['LIGHTGRAY'])
            pg.draw.rect(self.screen, color, (x_offset + i * 60, y_offset, 50, 30))
            ammo_text = f"{item.fixed_ammo}/{item.max_ammo}"
            self.draw_text(ammo_text, (x_offset + i * 60, y_offset + 30), Config.game_color['W'])

        current_item_text = f"Current Item: {character.items_list[character.current_item_index].name}"
        self.draw_text(current_item_text, (20, Config.game_height - 80))

    def draw_score(self, character):
        score_text = f"Score: {character.score}"
        self.draw_text(score_text, (Config.game_width - 150, 20))