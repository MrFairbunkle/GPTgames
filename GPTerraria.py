import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
TURRET_WIDTH, TURRET_HEIGHT = 50, 30
SHIP_SIZES = {'small': (40, 20), 'medium': (60, 30), 'large': (80, 40)}
SHIP_TYPES = ['small', 'medium', 'large']
BULLET_SPEED = 10
SHIP_BULLET_SPEED = 7  # Speed of bullets fired by ships
BASE_SHIP_SPEED = 5  # Base speed of the ships
MAX_SPAWN_RATE_MULTIPLIER = 30  # Maximum multiplier for spawn rate
MAX_SPEED_MULTIPLIER = 15  # Maximum multiplier for ship speed
FIRE_RATE = 1000  # Milliseconds (1 second between shots)

# Setup the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("10 More Bullets")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Turret class
class Turret:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - TURRET_WIDTH // 2, HEIGHT - TURRET_HEIGHT, TURRET_WIDTH, TURRET_HEIGHT)
        self.alive = True  # Flag to check if the turret is alive

    def draw(self):
        if self.alive:
            pygame.draw.rect(screen, WHITE, self.rect)

# Ship class
class Ship:
    def __init__(self, ship_type, speed):
        self.size = SHIP_SIZES[ship_type]
        
        # Randomly decide to spawn on left or right side
        if random.choice([True, False]):  # True for left, False for right
            self.rect = pygame.Rect(-self.size[0], random.randint(50, HEIGHT // 2), *self.size)  # Spawn on the left
            self.direction = 1  # Moving right
        else:
            self.rect = pygame.Rect(WIDTH, random.randint(50, HEIGHT // 2), *self.size)  # Spawn on the right
            self.direction = -1  # Moving left
        
        self.ship_type = ship_type
        self.speed = speed

    def update(self):
        # Move the ship based on its direction and speed
        self.rect.x += self.speed * self.direction

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)

# Bullet class (for turret)
class Bullet:
    def __init__(self, x, y, angle):
        self.rect = pygame.Rect(x, y, 5, 5)
        self.angle = angle

    def update(self):
        # Move bullet in the direction of the angle
        self.rect.x += BULLET_SPEED * math.cos(math.radians(self.angle))
        self.rect.y -= BULLET_SPEED * math.sin(math.radians(self.angle))

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

# Ship Bullet class
class ShipBullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 5, 5)  # Define the bullet size and position
        self.speed = SHIP_BULLET_SPEED

    def update(self):
        self.rect.y += self.speed  # Move the bullet downward

    def draw(self):
        pygame.draw.rect(screen, YELLOW, self.rect)

# Create the turret
turret = Turret()
bullets = []
ships = []
ship_bullets = []  # List to hold ship bullets

# Variables to manage spawn rate and ship speed
spawn_rate_multiplier = 1
ship_speed_multiplier = 1
ship_speed = BASE_SHIP_SPEED

# Timer for shooting
last_shot_time = pygame.time.get_ticks()

# Function to create exploding bullets
def create_exploding_bullets(x, y, ship_type):
    if ship_type == 'small':
        bullet_count = 4
    elif ship_type == 'medium':
        bullet_count = 6
    else:
        bullet_count = 8

    for i in range(bullet_count):
        angle = i * (360 / bullet_count)  # Distribute angles evenly around the circle
        bullets.append(Bullet(x, y, angle))

# Main game loop
running = True
while running:
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Shoot when left mouse button is pressed
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
            current_time = pygame.time.get_ticks()
            if current_time - last_shot_time >= FIRE_RATE and turret.alive:  # Ensure fire rate is respected
                bullets.append(Bullet(turret.rect.centerx, turret.rect.top, 90))  # shoot upward
                last_shot_time = current_time  # Update the last shot time

    keys = pygame.key.get_pressed()
    if turret.alive:  # Only allow movement if the turret is alive
        if keys[pygame.K_a] and turret.rect.x > 0:
            turret.rect.x -= 5
        if keys[pygame.K_d] and turret.rect.x < WIDTH - TURRET_WIDTH:
            turret.rect.x += 5
        if keys[pygame.K_w] and turret.rect.y > HEIGHT // 2:  # Prevent moving too high
            turret.rect.y -= 5
        if keys[pygame.K_s] and turret.rect.y < HEIGHT - TURRET_HEIGHT:  # Prevent moving off the bottom
            turret.rect.y += 5
    
    # Create ships with a chance to spawn based on the spawn rate multiplier
    if random.randint(1, 50 // spawn_rate_multiplier) == 1:  # Adjust the frequency of ship creation
        ship_type = random.choice(SHIP_TYPES)
        ships.append(Ship(ship_type, ship_speed))

    # Update and draw bullets (from turret)
    for bullet in bullets[:]:
        bullet.update()
        if bullet.rect.y < 0 or bullet.rect.x < 0 or bullet.rect.x > WIDTH:  # Remove bullet if it goes off-screen
            bullets.remove(bullet)
        bullet.draw()

    # Update and draw ships
    for ship in ships[:]:
        ship.update()  # Update ship position
        if ship.rect.x > WIDTH or ship.rect.x < -ship.size[0]:  # Remove if off-screen
            ships.remove(ship)
        
        # Each ship randomly fires bullets
        if random.randint(1, 100) == 1:  # Chance to fire a bullet
            ship_bullets.append(ShipBullet(ship.rect.centerx, ship.rect.bottom))  # Ship fires downward
        
        ship.draw()

    # Update and draw ship bullets
    for ship_bullet in ship_bullets[:]:
        ship_bullet.update()
        if ship_bullet.rect.y > HEIGHT:  # Remove ship bullet if off-screen
            ship_bullets.remove(ship_bullet)
        ship_bullet.draw()

    # Check for collisions with turret and ship bullets
    if turret.alive:
        for ship_bullet in ship_bullets:
            if ship_bullet.rect.colliderect(turret.rect):
                turret.alive = False  # Turret dies when hit
                break

    # Check for collisions with bullets (from turret) and ships
    for bullet in bullets[:]:
        for ship in ships[:]:
            if bullet.rect.colliderect(ship.rect):
                create_exploding_bullets(ship.rect.centerx, ship.rect.centery, ship.ship_type)
                bullets.remove(bullet)
                ships.remove(ship)
                
                # Increase spawn rate and ship speed upon hitting a ship
                if spawn_rate_multiplier < MAX_SPAWN_RATE_MULTIPLIER:
                    spawn_rate_multiplier += 0.1  # Increase by a small amount
                if ship_speed_multiplier < MAX_SPEED_MULTIPLIER:
                    ship_speed_multiplier += 0.05  # Increase by a small amount

                # Update ship speed based on the multiplier
                ship_speed = BASE_SHIP_SPEED * ship_speed_multiplier
                break

    # End game if turret dies
    if not turret.alive:
        font = pygame.font.SysFont(None, 75)
        text = font.render('Game Over', True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    else:
        turret.draw()

    pygame.display.flip()
    pygame.time.delay(30)

pygame.quit()
