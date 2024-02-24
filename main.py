import pygame
import sys
import time
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
SHIP_WIDTH, SHIP_HEIGHT = 60, 40
BULLET_WIDTH, BULLET_HEIGHT = 4, 10
ENEMY_ROWS = 5
ENEMY_COLS = 10
WALL_PADDING = 50  # Padding above the wall
HIGH_SCORE_FILE = "data.txt"  # File to store the high score

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Create the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")

# Clock to control the frame rate
clock = pygame.time.Clock()

# Load ship image
ship_image = pygame.image.load('ship.png').convert_alpha()
ship_width, ship_height = 60, 40  # Set width and height of ship image
ship_image = pygame.transform.scale(ship_image, (ship_width, ship_height))

# Load alien image
alien_image = pygame.image.load('alien.png').convert_alpha()
alien_width, alien_height = 40, 40  # Set width and height of alien image
alien_image = pygame.transform.scale(alien_image, (alien_width, alien_height))

# Ship
ship = pygame.Rect((WIDTH - SHIP_WIDTH) // 2, HEIGHT - SHIP_HEIGHT - 10, SHIP_WIDTH, SHIP_HEIGHT)

# Bullet
bullet = None
bullet_speed = 5
bullet_active = False

# Enemies
enemies = []
for row in range(ENEMY_ROWS):
    for col in range(ENEMY_COLS):
        enemy_rect = alien_image.get_rect()
        enemy_rect.x = col * (alien_width + 10) + 50
        enemy_rect.y = row * (alien_height + 10) + WALL_PADDING
        enemies.append(enemy_rect)

# Enemy movement variables
enemy_direction = 1
enemy_drop_amount = 10
enemy_speed = 1  # Adjusted enemy speed to match original game

# Enemy firing variables
bullet_cooldown = 1000  # Cooldown between enemy shots in milliseconds
last_bullet_time = time.time()
enemy_bullets = []  # List to store enemy bullets

# Score and High Score
score = 0
high_score = 0

# Read the high score from the file
try:
    with open(HIGH_SCORE_FILE, "r") as file:
        content = file.read().strip()
        high_score = int(content) if content.isdigit() else 0
except FileNotFoundError:
    # If the file doesn't exist, create it with an initial high score of 0
    with open(HIGH_SCORE_FILE, "w") as file:
        file.write("0")

# Game over flag
game_over = False


# Function to generate a new wave of enemies
def new_wave_of_enemies():
    global enemies
    enemies = [pygame.Rect(col * (alien_width + 10) + 50, row * (alien_height + 10) + WALL_PADDING, alien_width, alien_height) for row in range(ENEMY_ROWS) for col in range(ENEMY_COLS)]


# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Save the high score before quitting
            with open(HIGH_SCORE_FILE, "w") as file:
                file.write(str(high_score))
            pygame.quit()
            sys.exit()

    if not game_over:
        keys = pygame.key.get_pressed()
        # Move ship with left and right arrow keys
        if keys[pygame.K_LEFT] and ship.left > 0:
            ship.move_ip(-5, 0)
        if keys[pygame.K_RIGHT] and ship.right < WIDTH:
            ship.move_ip(5, 0)

        # Shoot bullet
        if keys[pygame.K_SPACE] and not bullet_active:
            bullet = pygame.Rect(ship.centerx - BULLET_WIDTH // 2, ship.top, BULLET_WIDTH, BULLET_HEIGHT)
            bullet_active = True

        # Move bullet
        if bullet_active:
            bullet.y -= bullet_speed
            if bullet.y <= 0:
                bullet_active = False

        # Move enemies
        for enemy in enemies:
            enemy.x += enemy_direction * enemy_speed
            if enemy.x >= WIDTH - enemy.width or enemy.x <= 0:
                enemy_direction *= -1
                for e in enemies:
                    e.y += enemy_drop_amount

            # Enemy firing logic
            if time.time() - last_bullet_time > bullet_cooldown / 1000:
                # Randomly select an enemy to fire
                if random.randint(0, 100) < 5:
                    enemy_bullet = pygame.Rect(enemy.centerx - BULLET_WIDTH // 2, enemy.bottom, BULLET_WIDTH, BULLET_HEIGHT)
                    enemy_bullets.append(enemy_bullet)  # Add the enemy bullet to the list
                    last_bullet_time = time.time()

        # Move enemy bullets
        for enemy_bullet in enemy_bullets[:]:
            enemy_bullet.y += bullet_speed
            if enemy_bullet.y >= HEIGHT:
                enemy_bullets.remove(enemy_bullet)

        # Check for collisions between bullet and enemies
        if bullet_active:
            for enemy in enemies[:]:
                if bullet.colliderect(enemy):
                    enemies.remove(enemy)
                    bullet_active = False
                    score += 10
                    break

        # Check for collisions between enemy bullets and the ship
        for enemy_bullet in enemy_bullets[:]:
            if ship.colliderect(enemy_bullet):
                game_over = True
                if score > high_score:
                    high_score = score

        # Check for game over (enemies reach the bottom)
        if any(enemy.y + enemy.height >= HEIGHT for enemy in enemies):
            game_over = True
            if score > high_score:
                high_score = score

        # Spawn new wave of enemies if all enemies are destroyed
        if not enemies:
            new_wave_of_enemies()

        # Increase enemy speed as their numbers decrease
        if len(enemies) < 10:
            enemy_speed = 1.8  # Adjusted speed to match original game
        elif len(enemies) < 20:
            enemy_speed = 1.5  # Adjusted speed to match original game
        elif len(enemies) < 30:
            enemy_speed = 1.2  # Adjusted speed to match original game
        else:
            enemy_speed = 1  # Adjusted speed to match original game

    # Draw everything
    screen.fill(BLACK)
    screen.blit(ship_image, ship.topleft)  # Draw ship image
    if bullet_active:
        pygame.draw.rect(screen, GREEN, bullet)
    for enemy in enemies:
        screen.blit(alien_image, enemy.topleft)
    for enemy_bullet in enemy_bullets:
        pygame.draw.rect(screen, RED, enemy_bullet)

    # Draw the score and high score
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    high_score_text = font.render(f"High Score: {high_score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(high_score_text, (WIDTH - high_score_text.get_width() - 10, 10))

    # Display "Game Over" message
    if game_over:
        game_over_text = font.render("Game Over! ", True, RED)
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(game_over_text, game_over_rect)

        # Reset the game state after a delay
        pygame.display.flip()
        pygame.time.delay(3000)  # Pause for 3 seconds
        game_over = False
        bullet_active = False
        bullet = None
        ship.x = (WIDTH - ship_width) // 2
        new_wave_of_enemies()
        score = 0
        enemy_direction = 1  # Reset enemy movement direction
        enemy_drop_amount = 10  # Reset enemy drop amount
        enemy_speed = 1  # Reset enemy speed
        enemy_bullets = []  # Reset enemy bullets

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)
