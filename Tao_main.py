import pygame as pg
import random as ra
import math as a
from Angry_Tao_game import *
from Tao_config import Config

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((Config.game_width, Config.game_height))
        pg.display.set_caption("Angry Tao Project")
        self.ui = UI(self.screen)
        self.unlocked_weapons = ["Normal"]
        self.character = Character(self.unlocked_weapons)
        self.drawer = Drawer(self.screen)
        self.stage = Stage()
        self.clock = pg.time.Clock()
        self.running = True
        self.current_stage = 1
        self.upgrade_available = False
        self.portal_cooldown = 0

    def handle_collisions(self):
        bullet_hits_enemy = pg.sprite.groupcollide(
            self.character.bullets, self.stage.enemies, True, False
        )
        for bullet, enemies in bullet_hits_enemy.items():
            for enemy in enemies:
                if enemy.take_damage(bullet.damage):
                    self.character.score += 10

        bullet_hits_obstacle = pg.sprite.groupcollide(
            self.character.bullets, self.stage.stage_obstacles, True, False
        )
        for bullet, obstacles in bullet_hits_obstacle.items():
            for obstacle in obstacles:
                if obstacle.take_damage(bullet.damage):
                    if bullet.skill == 'EXPLOSIVE':
                        # Explode and scatter bullets
                        for b in self.character.bullets:
                            if isinstance(b, ExplosiveBullet) and b.rect.colliderect(obstacle.rect):
                                b.explode(self)
                                break

    def handle_portals(self):
        portal_w, portal_h = 40, 20
        left_x = Config.stage_side_width // 2
        right_x = Config.stage_side_width + Config.stage_middle_width + (Config.stage_side_width // 2)

        left_top = pg.Rect(left_x - portal_w // 2, 100, portal_w, portal_h)
        left_bottom = pg.Rect(left_x - portal_w // 2, 100 + Config.stage_height - portal_h, portal_w, portal_h)
        right_top = pg.Rect(right_x - portal_w // 2, 100, portal_w, portal_h)
        right_bottom = pg.Rect(right_x - portal_w // 2, 100 + Config.stage_height - portal_h, portal_w, portal_h)

        if self.portal_cooldown > 0:
            self.portal_cooldown -= 1

        if self.portal_cooldown == 0:
            if self.character.rect.colliderect(left_top):
                # Align character X to right_bottom portal center X
                self.character.rect.centerx = right_bottom.centerx
                # Position character slightly below portal center Y to avoid immediate re-teleport
                self.character.rect.centery = right_bottom.centery + portal_h
                self.portal_cooldown = 30
            elif self.character.rect.colliderect(right_bottom):
                self.character.rect.centerx = left_top.centerx
                self.character.rect.centery = left_top.centery - portal_h
                self.portal_cooldown = 30
            elif self.character.rect.colliderect(right_top):
                self.character.rect.centerx = left_bottom.centerx
                self.character.rect.centery = left_bottom.centery + portal_h
                self.portal_cooldown = 30
            elif self.character.rect.colliderect(left_bottom):
                self.character.rect.centerx = right_top.centerx
                self.character.rect.centery = right_top.centery - portal_h
                self.portal_cooldown = 30


    def show_upgrade_menu(self):
        options = []
        if "Spread" not in self.unlocked_weapons:
            options.append(("Unlock Spread", lambda: self.unlocked_weapons.append("Spread")))
        if "Shotgun" not in self.unlocked_weapons:
            options.append(("Unlock Shotgun", lambda: self.unlocked_weapons.append("Shotgun")))
        if "Sniper" not in self.unlocked_weapons:
            options.append(("Unlock Sniper", lambda: self.unlocked_weapons.append("Sniper")))
        if "Explosive" not in self.unlocked_weapons:
            options.append(("Unlock Explosive", lambda: self.unlocked_weapons.append("Explosive")))
        options.append(("+10 Ammo", lambda: [setattr(item, 'max_ammo', item.max_ammo + 10) for item in self.character.items_list]))
        options.append(("+5 Score", lambda: setattr(self.character, 'score', self.character.score + 5)))
        options = ra.sample(options, min(3, len(options)))
        menu_rect = pg.Rect(400, 200, 700, 300)
        pg.draw.rect(self.screen, (50, 50, 50), menu_rect)
        for i, (text, _) in enumerate(options):
            self.ui.draw_text(text, (420, 250 + i * 60))
        pg.display.flip()
        selecting = True
        while selecting:
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    if 420 <= x <= 1080:
                        idx = (y - 250) // 60
                        if 0 <= idx < len(options):
                            options[idx][1]()
                            selecting = False

    def update_game(self):
        self.character.update_cooldown()
        keys = pg.key.get_pressed()
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.character.move(-5)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.character.move(5)
        if keys[pg.K_SPACE]:
            self.character.shoot()
        if keys[pg.K_LEFT] or keys[pg.K_q]:
            self.character.switch_item(-1)
        elif keys[pg.K_RIGHT] or keys[pg.K_e]:
            self.character.switch_item(1)

        self.character.bullets.update()
        self.stage.enemies.update()
        self.handle_collisions()
        self.handle_portals()

    def run(self):
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False

            self.update_game()

            self.screen.fill(Config.game_color['BL'])
            self.drawer.draw_portal_lines()
            self.drawer.draw_stage(self.stage)
            self.drawer.draw_portals(self.character)
            self.drawer.draw_character(self.character)
            self.drawer.draw_bullets(self.character)
            self.drawer.draw_enemies(self.stage)
            self.ui.draw_item_ui(self.character)
            self.ui.draw_score(self.character)
            pg.display.flip()
            self.clock.tick(Config.fps)

            if self.stage.check_stage_clear() and not self.upgrade_available:
                self.upgrade_available = True
                self.show_upgrade_menu()
                current_score = self.character.score
                self.character = Character(self.unlocked_weapons)
                self.character.score = current_score
                self.stage = Stage()
                self.upgrade_available = False

        pg.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
