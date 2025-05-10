import pygame as pg
import random as ra
from Angry_Tao_game import *
from Tao_config import Config

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((Config.game_width, Config.game_height))
        pg.display.set_caption("Angry Tao Project")
        self.ui = UI(self.screen)
        self.unlocked_weapons = ["Normal"]
        self.current_stage = 1
        self.character = Character(self.unlocked_weapons)
        self.stage = Stage(self.current_stage)
        self.drawer = Drawer(self.screen)
        self.clock = pg.time.Clock()
        self.running = True
        self.upgrade_available = False
        self.portal_cooldown = 0
        self.game_over = False
        self.explosive_blocks = pg.sprite.Group()

    def handle_collisions(self):
        # Explosive bullet collisions
        for bullet in list(self.character.bullets):
            if isinstance(bullet, ExplosiveBullet):
                hit_obstacles = pg.sprite.spritecollide(bullet, self.stage.stage_obstacles, False)
                if hit_obstacles:
                    for obstacle in hit_obstacles:
                        obstacle.kill()
                    bullet.explode(self, bullet.rect.center)
                    continue
                hit_enemies = pg.sprite.spritecollide(bullet, self.stage.enemies, False)
                if hit_enemies:
                    bullet.explode(self, bullet.rect.center)
                    continue
                hit_civilians = pg.sprite.spritecollide(bullet, self.stage.civilians, False)
                if hit_civilians:
                    bullet.explode(self, bullet.rect.center)
                    continue

        # Explosive blocks damage
        for block in self.explosive_blocks:
            hit_enemies = pg.sprite.spritecollide(block, self.stage.enemies, False)
            for enemy in hit_enemies:
                enemy.kill()
                self.character.score += 10
            hit_civilians = pg.sprite.spritecollide(block, self.stage.civilians, False)
            for civ in hit_civilians:
                civ.kill()
                self.character.score = max(0, self.character.score - 5)

        # Normal bullet hits enemies
        bullet_hits_enemy = pg.sprite.groupcollide(
            self.character.bullets, self.stage.enemies, True, False
        )
        for bullet, enemies in bullet_hits_enemy.items():
            for enemy in enemies:
                if enemy.take_damage(bullet.damage):
                    self.character.score += 10

        # Normal bullet hits civilians
        bullet_hits_civilians = pg.sprite.groupcollide(
            self.character.bullets, self.stage.civilians, True, False
        )
        for bullet, civilians in bullet_hits_civilians.items():
            for civ in civilians:
                self.character.score = max(0, self.character.score - 5)
                civ.take_damage(bullet.damage)

        # Normal bullet hits obstacles
        bullet_hits_obstacle = pg.sprite.groupcollide(
            self.character.bullets, self.stage.stage_obstacles, True, False
        )
        for bullet, obstacles in bullet_hits_obstacle.items():
            for obstacle in obstacles:
                if obstacle.take_damage(bullet.damage):
                    pass

    def check_game_over(self):
        if self.character.all_ammo_empty():
            self.game_over = True

    def draw_game_over(self):
        self.screen.fill((0, 0, 0))
        font = pg.font.Font(None, 72)
        text = font.render("GAME OVER", True, (255, 0, 0))
        score_text = font.render(f"Score: {self.character.score}", True, (255, 255, 255))
        button_font = pg.font.Font(None, 48)
        button_text = button_font.render("Continue", True, (0, 0, 0))

        self.screen.blit(text, (Config.game_width // 2 - text.get_width() // 2, 150))
        self.screen.blit(score_text, (Config.game_width // 2 - score_text.get_width() // 2, 250))

        button_rect = pg.Rect(Config.game_width // 2 - 100, 350, 200, 60)
        pg.draw.rect(self.screen, (255, 255, 255), button_rect)
        self.screen.blit(button_text, (button_rect.centerx - button_text.get_width() // 2, button_rect.centery - button_text.get_height() // 2))

        pg.display.flip()
        return button_rect

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
                self.character.rect.centerx = right_top.centerx
                self.character.rect.centery = right_top.centery + portal_h
                self.portal_cooldown = 30
            elif self.character.rect.colliderect(right_bottom):
                self.character.rect.centerx = left_bottom.centerx
                self.character.rect.centery = left_bottom.centery - portal_h
                self.portal_cooldown = 30
            elif self.character.rect.colliderect(right_top):
                self.character.rect.centerx = left_top.centerx
                self.character.rect.centery = left_top.centery + portal_h
                self.portal_cooldown = 30
            elif self.character.rect.colliderect(left_bottom):
                self.character.rect.centerx = right_bottom.centerx
                self.character.rect.centery = right_bottom.centery - portal_h
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
        self.stage.civilians.update()
        self.explosive_blocks.update()
        self.handle_collisions()
        self.handle_portals()

    def run(self):
        while self.running:
            if self.game_over:
                button_rect = self.draw_game_over()
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        self.running = False
                    elif event.type == pg.MOUSEBUTTONDOWN:
                        if button_rect.collidepoint(event.pos):
                            self.current_stage = 1
                            self.character = Character(self.unlocked_weapons)
                            self.stage = Stage(self.current_stage)
                            self.explosive_blocks.empty()
                            self.game_over = False
                self.clock.tick(Config.fps)
                continue

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False

            self.update_game()
            self.check_game_over()

            self.screen.fill(Config.game_color['BL'])
            self.drawer.draw_portal_lines()
            self.drawer.draw_stage(self.stage)
            self.drawer.draw_portals(self.character)
            self.drawer.draw_character(self.character)
            self.drawer.draw_bullets(self.character)
            self.drawer.draw_enemies(self.stage)
            self.drawer.draw_explosive_blocks(self.explosive_blocks)
            self.ui.draw_item_ui(self.character)
            self.ui.draw_score(self.character)
            pg.display.flip()
            self.clock.tick(Config.fps)

            if self.stage.check_stage_clear() and not self.upgrade_available:
                self.upgrade_available = True
                self.show_upgrade_menu()
                current_score = self.character.score
                self.current_stage += 1
                self.character = Character(self.unlocked_weapons)
                self.character.score = current_score
                self.stage = Stage(self.current_stage)
                self.upgrade_available = False

        pg.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
