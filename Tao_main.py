import tkinter as tk  # While imported, tkinter isn't used in the provided code
from Angry_Tao_game import *
from Tao_config import Config


class Game:
    """
    Handle the game to run, reset and update
    """
    def __init__(self):
        pg.init()
        self.ui = UI()
        self.screen = self.ui.screen
        self.character = Character()
        self.drawer = Drawer(self.screen)
        self.stage = Stage()
        self.running = True
        self.clock = pg.time.Clock()
        self.stats = {
            "movement_up": [],
            "movement_down": [],
            "items_usage": {item.name: 0 for item in self.character.items_list},
            "enemies_defeated": [],
            "obstacles_destroyed": [],
            "ammo_used": [],
            "missed_shots": []
        }
        self.current_stage_ammo_used = 0
        self.current_stage_enemies_defeated = 0
        self.current_stage_obstacles_destroyed = 0
        self.game_over = False

    def game_reset(self):
        self.stats["movement_up"].append(self.character.movement_up)
        self.stats["movement_down"].append(self.character.movement_down)
        for i, item in enumerate(self.character.items_list):
            used_ammo = self.character.items_list[i].max_ammo - self.character.items_list[i].fixed_ammo
            self.stats["items_usage"][item.name] = self.stats["items_usage"].get(item.name, 0) + used_ammo
        self.stats["enemies_defeated"].append(self.current_stage_enemies_defeated)
        self.stats["obstacles_destroyed"].append(self.current_stage_obstacles_destroyed)
        self.stats["ammo_used"].append(self.current_stage_ammo_used)
        self.stats["missed_shots"].append(self.character.missed_shots)

        self.character = Character()
        self.stage = Stage()
        self.current_stage_ammo_used = 0
        self.current_stage_enemies_defeated = 0
        self.current_stage_obstacles_destroyed = 0
        self.game_over = False

    def update_game(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_UP]:
            self.character.move(-5)
        elif keys[pg.K_DOWN]:
            self.character.move(5)
        elif keys[pg.K_SPACE]:
            if self.character.shoot():
                self.current_stage_ammo_used += 1
        elif keys[pg.K_LEFT]:
            self.character.switch_item(-1)
        elif keys[pg.K_RIGHT]:
            self.character.switch_item(1)

        self.character.bullets.update()
        self.stage.enemies.update()

        self.handle_collisions()

        if self.stage.check_stage_clear():
            print("Stage Cleared!")
            self.game_reset() # For now, reset the game on stage clear

    def handle_collisions(self):
        # Bullet hits enemy
        bullet_hits_enemy = pg.sprite.groupcollide(self.character.bullets, self.stage.enemies, True, False)
        for bullet, enemies in bullet_hits_enemy.items():
            for enemy in enemies:
                if enemy.take_damage(1):
                    self.character.score += 10
                    self.current_stage_enemies_defeated += 1

        # Bullet hits obstacle
        bullet_hits_obstacle = pg.sprite.groupcollide(self.character.bullets, self.stage.stage_obstacles, True, False)
        for bullet, obstacles in bullet_hits_obstacle.items():
            for obstacle in obstacles:
                if obstacle.take_damage(1):
                    self.current_stage_obstacles_destroyed += 1
                    if obstacle.material.lower() == 'bomb':
                        # Handle bomb explosion - for now, just destroy nearby obstacles and enemies
                        explosion_radius = Config.obstacle_size * 1.5
                        for obs in self.stage.stage_obstacles:
                            if a.dist(obs.rect.center, obstacle.rect.center) < explosion_radius:
                                obs.kill()
                                self.current_stage_obstacles_destroyed += 1
                        for enemy in self.stage.enemies:
                            if a.dist(enemy.rect.center, obstacle.rect.center) < explosion_radius:
                                enemy.take_damage(2) # Increased damage from bomb
                                if not enemy.alive():
                                    self.character.score += 15
                                    self.current_stage_enemies_defeated += 1

        # Bullet hits border
        for bullet in self.character.bullets:
            if not self.stage.border_rect.contains(bullet.rect):
                if not (bullet.rect.left < Config.stage_side_width or bullet.rect.right > Config.game_width - Config.stage_side_width):
                    bullet.kill()
                    self.character.missed_shots += 1

    def run(self):
        self.running = True
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False

            self.update_game()

            self.screen.fill(Config.game_color['BL'])
            self.drawer.draw_stage(self.stage)
            self.drawer.draw_character(self.character)
            self.drawer.draw_bullets(self.character)
            self.drawer.draw_enemies(self.stage)
            self.ui.draw_item_ui(self.character)
            self.ui.draw_score(self.character)

            pg.display.flip()
            self.clock.tick(Config.fps)

        pg.quit()

if __name__ == "__main__":
    game = Game()
    game.run()