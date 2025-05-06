import pygame as pg
import random as ra
import math as a
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
        self.image = pg.Surface([Config.enemy_size, Config.enemy_size])
        self.image.fill(Config.game_color['R'])
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.health = 2
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
    def __init__(self):
        self.stage_obstacles = pg.sprite.Group()
        self.enemies = pg.sprite.Group()
        self.generate_level()
        self.border_rect = pg.Rect(Config.stage_side_width, 100, Config.stage_middle_width, Config.stage_height)

    def generate_level(self):
        num_obstacles = ra.randint(6, 7)
        obstacle_materials = ['glass', 'wood', 'iron', 'diamond', 'gold', 'bomb', 'vibranium']
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

class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y, direction, skill):
        super().__init__()
        self.image = pg.Surface([Config.bullet_radius * 2, Config.bullet_radius * 2], pg.SRCALPHA)
        pg.draw.circle(self.image, (255,255,0), (Config.bullet_radius, Config.bullet_radius), Config.bullet_radius)  # Yellow bullet
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = Config.bullet_speed
        self.skill = skill

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right < Config.stage_side_width or self.rect.left > Config.stage_side_width + Config.stage_middle_width:
            self.kill()

class Character(pg.sprite.Sprite):
    def __init__(self, unlocked_weapons=None):
        super().__init__()
        self.image = pg.Surface([Config.character_radius * 2, Config.character_radius * 2], pg.SRCALPHA)
        pg.draw.circle(self.image, Config.game_color['G'], (Config.character_radius, Config.character_radius), Config.character_radius)
        self.rect = self.image.get_rect(center=(Config.stage_side_width // 2, Config.game_height // 2))
        if unlocked_weapons is None:
            unlocked_weapons = ["Normal"]
        self.items_list = []
        if "Normal" in unlocked_weapons:
            self.items_list.append(Items("Normal", "NORMAL", 50, "NORMAL"))
        if "Spread" in unlocked_weapons:
            self.items_list.append(Items("Spread", "SPREAD", 20, "SPREAD"))
        if "Explosive" in unlocked_weapons:
            self.items_list.append(Items("Explosive", "EXPLOSIVE", 5, "EXPLOSIVE"))
        self.current_item_index = 0
        self.bullets = pg.sprite.Group()
        self.score = 0
        self.movement_up = 0
        self.movement_down = 0
        self.missed_shots = 0

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
        if len(self.items_list) > 1:
            self.current_item_index = (self.current_item_index + direction) % len(self.items_list)

    def shoot(self):
        current_item = self.items_list[self.current_item_index]
        if current_item.use_skill():
            direction = 1
            if current_item.skill == "NORMAL":
                bullet = Bullet(self.rect.centerx, self.rect.centery, direction, "NORMAL")
                self.bullets.add(bullet)
            elif current_item.skill == "SPREAD":
                for offset in [-10, 0, 10]:
                    bullet = Bullet(self.rect.centerx, self.rect.centery + offset, direction, "SPREAD")
                    self.bullets.add(bullet)
            elif current_item.skill == "EXPLOSIVE":
                bullet = Bullet(self.rect.centerx, self.rect.centery, direction, "EXPLOSIVE")
                self.bullets.add(bullet)
            return True
        return False

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

    def draw_portals(self, character):
        portal_color = (0, 255, 255)
        portal_w, portal_h = 40, 20
        char_x = character.rect.centerx
        pg.draw.rect(self.screen, portal_color, (char_x - portal_w // 2, 100, portal_w, portal_h))
        pg.draw.rect(self.screen, portal_color, (char_x - portal_w // 2, 100 + Config.stage_height - portal_h, portal_w, portal_h))
        right_x = Config.game_width - char_x
        pg.draw.rect(self.screen, portal_color, (right_x - portal_w // 2, 100, portal_w, portal_h))
        pg.draw.rect(self.screen, portal_color, (right_x - portal_w // 2, 100 + Config.stage_height - portal_h, portal_w, portal_h))

    def draw_portal_lines(self):
        portal_h = 20
        y_top = 100 + portal_h // 2
        y_bottom = 100 + Config.stage_height - portal_h // 2
        pg.draw.line(self.screen, (255, 255, 255), (0, y_top), (Config.game_width, y_top), 3)
        pg.draw.line(self.screen, (255, 255, 255), (0, y_bottom), (Config.game_width, y_bottom), 3)

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
