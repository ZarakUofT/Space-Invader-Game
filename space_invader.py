import pygame
import os
import time
import random
import ctypes
pygame.font.init()
pygame.init()

ctypes.windll.user32.SetProcessDPIAware()
WIDTH, HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
ENEMY_SHIP_SIZE_TRANSFORM = 0.08
WIN = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Space Shooter")

# Load images
RED_SPACE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png")), (int(
    WIDTH * ENEMY_SHIP_SIZE_TRANSFORM), int(HEIGHT * ENEMY_SHIP_SIZE_TRANSFORM)))
GREEN_SPACE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png")), (int(
    WIDTH * ENEMY_SHIP_SIZE_TRANSFORM), int(HEIGHT * ENEMY_SHIP_SIZE_TRANSFORM)))
BLUE_SPACE_SHIP = pygame.transform.scale(pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png")), (int(
    WIDTH * ENEMY_SHIP_SIZE_TRANSFORM), int(HEIGHT * ENEMY_SHIP_SIZE_TRANSFORM)))

# PLayer ship
YELLOW_SPACE_SHIP = pygame.image.load(
    os.path.join("assets", "pixel_ship_yellow.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(
    os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(
    os.path.join("assets", "pixel_laser_yellow.png"))

# Background
BG = pygame.transform.scale(pygame.image.load(
    os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 15

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        enem_killed = 0
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        enem_killed += 1
                        if laser in self.lasers:
                            self.lasers.remove(laser)
        return enem_killed

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y +
                                               self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() +
                                               10, self.ship_img.get_width() * (self.health/self.max_health), 10))

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)


class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 27, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = int(obj2.x - obj1.x)
    offset_y = int(obj2.y - obj1.y)
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def menu_display_text(text, y_offset):
    title_font = pygame.font.SysFont("comicsans", 70)
    title_label = title_font.render(text, 1, (255, 255, 255))
    WIN.blit(title_label, (WIDTH/2-title_label.get_width()/2,
                           (HEIGHT/2-title_label.get_height()/2) - y_offset))

    # title_label1 = title_font.render("Press Enter to begin the game", 1, (255, 255, 255))
    # title_label2 = title_font.render("OR", 1, (255, 255, 255))
    # title_label3 = title_font.render("Press Esc to Exit", 1, (255, 255, 255))

    # WIN.blit(title_label1, (WIDTH/2-title_label1.get_width()/2, (HEIGHT/2-title_label1.get_height()/2) - 150))
    # WIN.blit(title_label2, (WIDTH/2-title_label2.get_width()/2, (HEIGHT/2-title_label2.get_height()/2) - 75))
    # WIN.blit(title_label3, (WIDTH/2-title_label3.get_width()/2, (HEIGHT/2-title_label3.get_height()/2) - 0))


def main_menu():
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        menu_display_text("Press Enter to begin the game..", 150)
        menu_display_text("Or", 75)
        menu_display_text("Press Esc to Exit", 0)

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                run = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                main()

    pygame.quit()


def main():
    run = True
    FPS = 60
    level = 0
    lives = 5
    main_font = pygame.font.SysFont("comicsans", 40)
    lost_font = pygame.font.SysFont("comicsans", 75)
    level_update_font = pygame.font.SysFont("comicsans", 50)

    enemies = []
    wave_length = 5
    enemy_vel = 2

    enemies_to_kill = 0
    enemies_killed = 0

    player_vel = 20
    laser_vel = 15
    player = Player(WIDTH*9/20, HEIGHT-100)

    clock = pygame.time.Clock()
    lost = False
    killed_less = False
    lost_count = 0

    def level_update():
        WIN.blit(BG, (0, 0))

        level_label = lost_font.render(f"Level: {level}", 1, (255, 69, 0))
        enemies_in_wave_label = level_update_font.render(
            f"Enemy ships in Level: {wave_length}", 1, (255, 255, 255))
        enemy_to_kill_label = level_update_font.render(
            f"Enemy ships to destroy: {enemies_to_kill}", 1, (255, 255, 255))

        WIN.blit(level_label, (WIDTH/2 - level_label.get_width()/2, HEIGHT/2 - 60))
        WIN.blit(enemies_in_wave_label, (WIDTH/2 -
                                         enemies_in_wave_label.get_width()/2, HEIGHT/2))
        WIN.blit(enemy_to_kill_label, (WIDTH/2 -
                                       enemy_to_kill_label.get_width()/2, HEIGHT/2 + 60))

        pygame.display.update()

        time.sleep(3)

    def redraw_window():
        WIN.blit(BG, (0, 0))

        # draw text
        lives_label = main_font.render(
            f"Enemy ships destroyed: {enemies_killed}", 1, (255, 255, 255))
        level_label = main_font.render(f"Level: {level}", 1, (255, 255, 255))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(WIN)

        player.draw(WIN)

        if lost:
            lost_label = lost_font.render("You Lost!", 1, (255, 0, 0))
            needed_label = level_update_font.render(
                f"You needed to destroy {enemies_to_kill} Enemy ships", 1, (255, 255, 255))
            base_taken_label = level_update_font.render(
                "Enemy ships have taken the base!", 1, (255, 20, 20))
            WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width() /
                                  2, HEIGHT/2 - lost_label.get_height() - 20))
            WIN.blit(needed_label, (WIDTH/2 -
                                    needed_label.get_width() / 2, HEIGHT/2))
            WIN.blit(base_taken_label, (WIDTH/2 - base_taken_label.get_width() /
                                        2, HEIGHT/2 + needed_label.get_height() + 20))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if killed_less or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 2:
                run = False
            else:
                continue

        if len(enemies) == 0:
            if enemies_killed < enemies_to_kill:
                killed_less = True
                continue
            level += 1
            enemy_vel += 1 if level < player_vel/2 else player_vel/2
            player_vel += 5 if level % 3 == 0 else 0
            Ship.COOLDOWN -= 2 if Ship.COOLDOWN > 2 else 2
            wave_length += (3 * level)
            enemies_to_kill = int(wave_length * 0.7)
            enemies_killed = 0
            level_update()
            for _ in range(wave_length):
                enemy = Enemy(random.randrange(
                    50, WIDTH-100), random.randrange(-1500, -100), random.choice(["red", "blue", "green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and (player.x - player_vel > 0):  # left
            player.x -= player_vel
        if keys[pygame.K_d] and (player.x + player_vel + player.get_width() < WIDTH):  # right
            player.x += player_vel
        if keys[pygame.K_w] and (player.y - player_vel > 0):  # up
            player.y -= player_vel
        if keys[pygame.K_s] and (player.y + player_vel + player.get_height() + 30 < HEIGHT):  # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(laser_vel, player)

            if random.randrange(0, 2*FPS) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > HEIGHT:
                # lives -= 1
                enemies.remove(enemy)

        enemies_killed += player.move_lasers(-laser_vel, enemies)


main_menu()
