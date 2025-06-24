import pgzrun

WIDTH, HEIGHT = 800, 550
TITLE = "Moon Escape"


class Hero:
    def __init__(self, pos):
        self.actor = Actor("hero/idle/hero_idle", pos)
        self.actor.scale = 2
        self.vy = 0
        self.on_ground = False
        self.facing = "right"
        self.walk_left = [f"hero/walk/hero_walk_left{i}" for i in range(1, 7)]
        self.walk_right = [f"hero/walk/hero_walk_right{i}" for i in range(1, 7)]
        self.walk_idle = ["hero/idle/hero_idle", "hero/idle/hero_idle1"]
        self.img_idx = 0
        self.anim_timer = 0
        self.alive = True
        self.update_hitbox()

    def update_hitbox(self):
        self.hitbox = Rect(self.actor.x - 15, self.actor.y - 35, 30, 60)

    def update(self):
        if not self.alive:
            return
        self.vy += 0.5
        self.actor.y += self.vy
        self.on_ground = False
        for plat in platforms:
            if (
                self.vy >= 0 and self.actor.bottom <= plat.top + self.vy and
                self.actor.bottom + self.vy >= plat.top and
                self.actor.right > plat.left and self.actor.left < plat.right
            ):
                self.actor.bottom = plat.top
                self.vy = 0
                self.on_ground = True

        if self.actor.y >= 500:
            self.actor.y = 500
            self.vy = 0
            self.on_ground = True

        if keyboard.left:
            self.actor.x -= 3
            self.facing = "left"
        elif keyboard.right:
            self.actor.x += 3
            self.facing = "right"

        self.actor.x = max(self.actor.width // 2, min(WIDTH - self.actor.width // 2, self.actor.x))

        if keyboard.space and self.on_ground:
            self.vy = -10
            self.on_ground = False
            sounds.jump.play()

        self.animate()
        self.update_hitbox()

    def die(self):
        self.alive = False
        sounds.hero_hurt.play()

    def animate(self):
        self.anim_timer += 1
        if keyboard.right:
            if self.anim_timer % 8 == 0:
                self.img_idx = (self.img_idx + 1) % len(self.walk_right)
                self.actor.image = self.walk_right[self.img_idx]
            self.actor.flip_x = False
        elif keyboard.left:
            if self.anim_timer % 8 == 0:
                self.img_idx = (self.img_idx + 1) % len(self.walk_left)
                self.actor.image = self.walk_left[self.img_idx]
            self.actor.flip_x = True
        else:
            if self.anim_timer % 15 == 0:
                self.img_idx = (self.img_idx + 1) % len(self.walk_idle)
                self.actor.image = self.walk_idle[self.img_idx]

    def draw(self):
        self.actor.draw()


class Enemy:
    def __init__(self, pos, path_range):
        self.actor = Actor("enemies/walk/enemy_walk1", pos)
        self.actor.scale = 2
        self.walk_images = [f"enemies/walk/enemy_walk{i}" for i in range(1, 5)]
        self.img_idx = 0
        self.anim_timer = 0
        self.speed = 2
        self.path_start, self.path_end = path_range
        self.is_dead = False
        self.death_timer = 0
        self.update_hitbox()

    def update_hitbox(self):
        self.hitbox = Rect(self.actor.x - 20, self.actor.y - 30, 40, 50)

    def update(self):
        if self.is_dead:
            self.death_timer -= 1
            if self.death_timer <= 0:
                enemies.remove(self)
            return

        self.actor.x += self.speed
        if self.actor.left < self.path_start or self.actor.right > self.path_end:
            self.speed *= -1

        if self.anim_timer % 10 == 0:
            self.img_idx = (self.img_idx + 1) % len(self.walk_images)
            self.actor.image = self.walk_images[self.img_idx]

        self.anim_timer += 1
        self.actor.flip_x = self.speed < 0
        self.update_hitbox()

    def die(self):
        self.is_dead = True
        self.actor.image = "enemies/dead/enemy_dead"
        self.death_timer = 30

    def draw(self):
        self.actor.draw()


def restart():
    global hero, enemies, coins, game_state
    hero = Hero((160, 480))
    coins_pos = [(260, 200), (390, 100), (390, 260), (540, 200)]
    coins.clear()
    coins.extend([Actor("coin", pos, scale=2) for pos in coins_pos])
    enemies.clear()
    enemies.extend([
        Enemy((250, 215), (210, 290)),
        Enemy((370, 145), (330, 440)),
        Enemy((540, 215), (480, 600)),
    ])
    game_state = "playing"
    music.play("game_moon_music")


def update():
    global game_state
    if game_state != "playing":
        return

    hero.update()

    for enemy in enemies:
        enemy.update()
        if hero.hitbox.colliderect(enemy.hitbox) and not enemy.is_dead:
            if hero.vy > 0 and hero.actor.y < enemy.actor.y:
                enemy.die()
                hero.vy = -7
                sounds.enemy_smash.play()
            else:
                hero.die()
                game_state = "game_over"
                sounds.game_over.play()

    for c in coins[:]:
        if hero.actor.colliderect(c):
            coins.remove(c)
            sounds.coin.play()

    if not coins:
        game_state = "victory"
        music.stop()
        sounds.win.play()


def draw_platforms():
    for plat in platforms:
        screen.draw.filled_rect(plat, (150, 150, 150))


def menu():
    screen.fill("black")
    screen.blit("backgrounds/menu_background.png", (0, 0))
    screen.draw.text("MOON ESCAPE", center=(WIDTH // 2, 150), fontsize=60, color="white", fontname="menu_font.ttf")
    screen.draw.text("Start Game", center=(WIDTH // 2, 250), fontsize=40, color="white", fontname="menu_options_font")
    screen.draw.text("Exit", center=(WIDTH // 2, 310), fontsize=40, color="white", fontname="menu_options_font")
    screen.blit("ui/unmute_menu.png" if muted else "ui/mute_menu.png", (710, 470))


def game():
    screen.fill("black")
    screen.blit("backgrounds/moon_surface", (0, 0))
    draw_platforms()
    hero.draw()
    for enemy in enemies:
        enemy.draw()
    for c in coins:
        c.draw()


def pause_menu():
    screen.fill("black")
    screen.blit("backgrounds/pause_menu", (0, 0))
    screen.draw.text("PAUSED", center=(WIDTH // 2, 150), fontsize=60, color="white", fontname="menu_font.ttf")
    for i, txt in enumerate(["Resume Game", "Restart", "Back to menu"]):
        screen.draw.text(txt, center=(WIDTH // 2, 250 + i * 60), fontsize=40, color="white", fontname="menu_options_font")


def victory():
    screen.fill("black")
    screen.draw.text("YOU WON!", center=(WIDTH // 2, 150), fontsize=60, color="yellow", fontname="menu_font.ttf")
    screen.draw.text("Restart", center=(WIDTH // 2, 250), fontsize=40, color="white", fontname="menu_options_font")
    screen.draw.text("Exit", center=(WIDTH // 2, 310), fontsize=40, color="white", fontname="menu_options_font")
    screen.blit("hero/expressions/happy_hero", (WIDTH // 2 - 75, 350))


def game_over():
    music.stop()
    screen.fill("black")
    screen.draw.text("GAME OVER", center=(WIDTH // 2, 150), fontsize=60, color="red", fontname="menu_font.ttf")
    screen.draw.text("Restart", center=(WIDTH // 2, 250), fontsize=40, color="white", fontname="menu_options_font")
    screen.draw.text("Exit", center=(WIDTH // 2, 310), fontsize=40, color="white", fontname="menu_options_font")
    screen.blit("hero/expressions/hero_sad", (WIDTH // 2 - 55, 350))


def draw():
    if game_state == "menu":
        menu()
    elif game_state == "playing":
        game()
    elif game_state == "pause":
        pause_menu()
    elif game_state == "game_over":
        game_over()
    elif game_state == "victory":
        victory()


def on_key_down(key):
    global game_state
    if key == keys.ESCAPE:
        if game_state == "playing":
            game_state = "pause"
            music.pause()
        else:
            game_state = "playing"
            music.unpause()


def on_mouse_down(pos):
    if game_state in ["menu", "pause", "game_over", "victory"]:
        handle_menu_click(pos)


def handle_menu_click(pos):
    global game_state, muted

    def within(rect):
        return rect.collidepoint(pos)

    if game_state == "menu":
        if within(Rect((300, 230), (200, 40))):
            restart()
        elif within(Rect((300, 290), (200, 40))):
            quit()
        elif within(Rect((710, 470), (50, 50))):
            muted = not muted
            music.pause() if muted else music.unpause()

    elif game_state == "pause":
        actions = ["playing", "restart", "menu"]
        for i, (rect_pos, action) in enumerate(zip([(300, 230), (300, 290), (300, 350)], actions)):
            if within(Rect(rect_pos, (200, 40))):
                if action == "restart":
                    restart()
                    music.play("game_moon_music")
                elif action == "playing":
                    game_state = "playing"
                    music.unpause()
                elif action == "menu":
                    game_state = "menu"
                    music.stop()
                    music.play("menu_space_music.mp3")

    elif game_state in ["game_over", "victory"]:
        if within(Rect((300, 230), (200, 40))):
            restart()
            music.play("game_moon_music")
        elif within(Rect((300, 290), (200, 40))):
            if game_state == "game_over":
                game_state = "menu"
                music.play("menu_space_music")
            elif game_state == "victory":
                game_state = "menu"
                music.play("menu_space_music")


hero = None
enemies = []
coins = []
platforms = [
    Rect((100, 500), (120, 20)),
    Rect((220, 430), (100, 20)),
    Rect((150, 360), (120, 20)),
    Rect((270, 290), (100, 20)),
    Rect((200, 220), (120, 20)),
    Rect((320, 150), (100, 20)),
    Rect((WIDTH - 220, 500), (120, 20)),
    Rect((WIDTH - 340, 430), (100, 20)),
    Rect((WIDTH - 270, 360), (120, 20)),
    Rect((WIDTH - 440, 290), (160, 20)),
    Rect((WIDTH - 320, 220), (120, 20)),
    Rect((WIDTH - 440, 150), (100, 20)),
]
game_state = "menu"
muted = False
music.play("menu_space_music.mp3")
music.set_volume(0.5)

pgzrun.go()
