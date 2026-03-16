import pygame, random

# ---- Initialize pygame ----
pygame.init()

# ---- Display Window ----
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Monster Wrangler")

# ---- FPS and Clock ----
FPS = 60
clock = pygame.time.Clock()


class Game():
    """A class to control gameplay"""

    def __init__(self, player, monster_group):
        """Initialize the game object"""
        self.score = 0
        self.round_number = 0
        self.round_time = 0
        self.frame_count = 0

        self.player = player
        self.monster_group = monster_group

        # Sound (Using try/except to prevent crashes if files are missing)
        try:
            self.next_level_sound = pygame.mixer.Sound("next_level.wav")
        except:
            self.next_level_sound = None

        # Font
        try:
            self.font = pygame.font.Font("Abrushow.ttf", 24)
        except:
            self.font = pygame.font.SysFont("Arial", 24)

        # Monster images
        self.target_monster_images = []
        monster_files = ["blue_monster.png", "green_monster.png", "purple_monster.png", "yellow_monster.png"]
        monster_colors = [(20, 176, 235), (87, 201, 47), (226, 73, 243), (243, 157, 20)]

        for i, file in enumerate(monster_files):
            try:
                img = pygame.image.load(file)
            except:
                # Create a colored square if the image file is missing
                img = pygame.Surface((64, 64))
                img.fill(monster_colors[i])
            self.target_monster_images.append(img)

        self.target_monster_type = 0
        self.target_monster_image = self.target_monster_images[self.target_monster_type]

        self.target_monster_rect = self.target_monster_image.get_rect()
        self.target_monster_rect.centerx = WINDOW_WIDTH // 2
        self.target_monster_rect.top = 30

    def update(self):
        """Update the game object"""
        self.frame_count += 1
        if self.frame_count == FPS:
            self.round_time += 1
            self.frame_count = 0

        self.check_collisions()

    def draw(self):
        """Draw the HUD to the display"""
        WHITE = (255, 255, 255)
        colors = [(20, 176, 235), (87, 201, 47), (226, 73, 243), (243, 157, 20)]

        catch_text = self.font.render("Current Catch", True, WHITE)
        catch_rect = catch_text.get_rect(centerx=WINDOW_WIDTH // 2, top=5)

        score_text = self.font.render("Score: " + str(self.score), True, WHITE)
        score_rect = score_text.get_rect(topleft=(5, 5))

        lives_text = self.font.render("Lives: " + str(self.player.lives), True, WHITE)
        lives_rect = lives_text.get_rect(topleft=(5, 35))

        round_text = self.font.render("Current Round: " + str(self.round_number), True, WHITE)
        round_rect = round_text.get_rect(topleft=(5, 65))

        time_text = self.font.render("Round Time: " + str(self.round_time), True, WHITE)
        time_rect = time_text.get_rect(topright=(WINDOW_WIDTH - 10, 5))

        warp_text = self.font.render("Warps: " + str(self.player.warps), True, WHITE)
        warp_rect = warp_text.get_rect(topright=(WINDOW_WIDTH - 10, 35))

        display_surface.blit(catch_text, catch_rect)
        display_surface.blit(score_text, score_rect)
        display_surface.blit(lives_text, lives_rect)
        display_surface.blit(round_text, round_rect)
        display_surface.blit(time_text, time_rect)
        display_surface.blit(warp_text, warp_rect)

        display_surface.blit(self.target_monster_image, self.target_monster_rect)

        pygame.draw.rect(display_surface, colors[self.target_monster_type],
                         (WINDOW_WIDTH // 2 - 32, 30, 64, 64), 2)

        pygame.draw.rect(display_surface, colors[self.target_monster_type],
                         (0, 100, WINDOW_WIDTH, WINDOW_HEIGHT - 200), 4)

    def check_collisions(self):
        """Check for collisions between player and monsters"""
        collided_monster = pygame.sprite.spritecollideany(self.player, self.monster_group)

        if collided_monster:
            # Check if it's the right monster
            if collided_monster.type == self.target_monster_type:
                self.score += 100 * self.round_number
                collided_monster.remove(self.monster_group)
                if self.player.catch_sound:
                    self.player.catch_sound.play()

                if self.monster_group:
                    self.choose_new_target()
                else:
                    self.player.reset()
                    self.start_new_round()
            else:
                # Wrong monster
                if self.player.die_sound:
                    self.player.die_sound.play()
                self.player.lives -= 1
                if self.player.lives <= 0:
                    self.pause_game("Final Score: " + str(self.score), "Press 'Enter' to play again")
                    self.reset_game()
                self.player.reset()

    def start_new_round(self):
        """Populate the board with new monsters"""
        self.round_number += 1
        self.round_time = 0
        self.frame_count = 0

        # Spawn monsters based on round
        for i in range(self.round_number):
            for m_type in range(4):
                x = random.randint(0, WINDOW_WIDTH - 64)
                y = random.randint(100, WINDOW_HEIGHT - 164)
                new_monster = Monster(x, y, self.target_monster_images[m_type], m_type)
                self.monster_group.add(new_monster)

        self.choose_new_target()
        if self.next_level_sound:
            self.next_level_sound.play()

    def choose_new_target(self):
        """Pick a new target from existing monsters"""
        if self.monster_group:
            target_monster = random.choice(self.monster_group.sprites())
            self.target_monster_type = target_monster.type
            self.target_monster_image = target_monster.image

    def pause_game(self, main_text, sub_text):
        global running
        WHITE, BLACK = (255, 255, 255), (0, 0, 0)

        main_surface = self.font.render(main_text, True, WHITE)
        main_rect = main_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        sub_surface = self.font.render(sub_text, True, WHITE)
        sub_rect = sub_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 64))

        display_surface.fill(BLACK)
        display_surface.blit(main_surface, main_rect)
        display_surface.blit(sub_surface, sub_rect)
        pygame.display.update()

        is_paused = True
        while is_paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    is_paused = False
                if event.type == pygame.QUIT:
                    is_paused = False
                    running = False

    def reset_game(self):
        self.score = 0
        self.round_number = 0
        self.player.lives = 5
        self.player.warps = 2
        self.monster_group.empty()
        self.start_new_round()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load("knight.png")
        except:
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 255, 255))

        self.rect = self.image.get_rect(centerx=WINDOW_WIDTH // 2, bottom=WINDOW_HEIGHT)
        self.lives, self.warps, self.velocity = 5, 2, 8

        try:
            self.catch_sound = pygame.mixer.Sound("catch.wav")
            self.die_sound = pygame.mixer.Sound("die.wav")
            self.warp_sound = pygame.mixer.Sound("warp.wav")
        except:
            self.catch_sound = self.die_sound = self.warp_sound = None

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0: self.rect.x -= self.velocity
        if keys[pygame.K_RIGHT] and self.rect.right < WINDOW_WIDTH: self.rect.x += self.velocity
        if keys[pygame.K_UP] and self.rect.top > 100: self.rect.y -= self.velocity
        if keys[pygame.K_DOWN] and self.rect.bottom < WINDOW_HEIGHT - 100: self.rect.y += self.velocity

    def warp(self):
        if self.warps > 0:
            self.warps -= 1
            if self.warp_sound: self.warp_sound.play()
            self.rect.bottom = WINDOW_HEIGHT

    def reset(self):
        self.rect.centerx = WINDOW_WIDTH // 2
        self.rect.bottom = WINDOW_HEIGHT


class Monster(pygame.sprite.Sprite):
    def __init__(self, x, y, image, monster_type):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.type = monster_type
        self.dx, self.dy = random.choice([-1, 1]), random.choice([-1, 1])
        self.velocity = random.randint(1, 5)

    def update(self):
        self.rect.x += self.dx * self.velocity
        self.rect.y += self.dy * self.velocity
        if self.rect.left <= 0 or self.rect.right >= WINDOW_WIDTH: self.dx *= -1
        if self.rect.top <= 100 or self.rect.bottom >= WINDOW_HEIGHT - 100: self.dy *= -1


# ---- Setup Groups ----
my_player_group = pygame.sprite.GroupSingle(Player())
my_monster_group = pygame.sprite.Group()
my_game = Game(my_player_group.sprite, my_monster_group)

my_game.pause_game("Monster Wrangler", "Press 'Enter' to begin")
my_game.start_new_round()

# ---- Main Game Loop ----
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            my_player_group.sprite.warp()

    display_surface.fill((0, 0, 0))
    my_player_group.update()
    my_player_group.draw(display_surface)
    my_monster_group.update()
    my_monster_group.draw(display_surface)
    my_game.update()
    my_game.draw()

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
