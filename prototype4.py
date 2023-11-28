import pygame
import sys
import random
import mysql.connector as ms

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 300
GROUND_HEIGHT = 50

# Colors
WHITE = (0, 182, 255)
BLACK = (0, 0, 0)
DINOSAUR_COLOR = (0, 128, 255)  # Blue color for the dinosaur
OBSTACLE_COLOR = (255, 0, 0)  # Red color for the obstacles

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dinosaur Game")

# Dinosaur properties
dinosaur_radius = 15
dinosaur_position = [SCREEN_WIDTH // 4, SCREEN_HEIGHT - GROUND_HEIGHT - dinosaur_radius]
dinosaur_y_velocity = 0
on_ground = True
double_jump_available = True

# Obstacle properties
obstacles_bottom = []
obstacles_top = []
obstacle_speed = 6
obstacle_frequency = 40

# Jump properties
jump_force = 15
double_jump_force = 20

# Game state
game_active = False
score = 0

# Player information
player_name = ""

# Fonts
font = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)

# Input box
def draw_input_box(rect, text, active):
    color = WHITE if not active else (200, 200, 255)
    pygame.draw.rect(screen, color, rect, border_radius=10)

    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=rect.center)

    screen.blit(text_surface, text_rect)

def get_player_name():
    global player_name
    input_text = font.render("Enter your name and press ENTER to start:", True, BLACK)
    name_input = ""
    name_input_rect = pygame.Rect(SCREEN_WIDTH // 4, 150, 200, 32)
    active = True

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if name_input_rect.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
            elif event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        player_name = name_input
                        return
                    elif event.key == pygame.K_BACKSPACE:
                        name_input = name_input[:-1]
                    else:
                        name_input += event.unicode

        screen.fill(WHITE)
        screen.blit(input_text, (SCREEN_WIDTH // 4, 100))
        draw_input_box(name_input_rect, name_input, active)
        pygame.display.flip()

def show_welcome_screen():
    screen.fill(WHITE)
    title_text = big_font.render("Dinosaur Game", True, BLACK)
    instruction_text = font.render("Press SPACE to jump (Double tap for higher jump)", True, BLACK)
    screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 100))
    screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, 200))
    pygame.display.flip()
    pygame.time.wait(2000)

def show_top_players():
    con = ms.connect(host="localhost", user="root", passwd="immastudyiniitgoa")
    cuz = con.cursor()

    cuz.execute("CREATE DATABASE IF NOT EXISTS JUMP")
    cuz.execute("USE JUMP")

    cuz.execute("SELECT * FROM mvp ORDER BY score DESC LIMIT 5")
    top_players = cuz.fetchall()

    screen.fill(WHITE)
    top_players_text = big_font.render("Top Players", True, BLACK)
    screen.blit(top_players_text, (SCREEN_WIDTH // 2 - top_players_text.get_width() // 2, 100))

    y_position = 150
    for rank, (name, player_score) in enumerate(top_players, start=1):
        player_text = font.render(f"{rank}. {name}: {player_score}", True, BLACK)
        screen.blit(player_text, (SCREEN_WIDTH // 2 - player_text.get_width() // 2, y_position))
        y_position += 50

    pygame.display.flip()
    pygame.time.wait(5000)

def show_game_over_screen():
    con = ms.connect(host="localhost", user="root", passwd="immastudyiniitgoa")
    cuz = con.cursor()

    print(f"Player: {player_name}")
    print(f"Final Score: {score}")

    cuz.execute("CREATE DATABASE IF NOT EXISTS JUMP")
    cuz.execute("USE JUMP")

    cuz.execute("CREATE TABLE IF NOT EXISTS mvp (name VARCHAR(100), score INT)")

    query = f"INSERT INTO mvp (name, score) VALUES ('{player_name}', {score})"
    cuz.execute(query)

    con.commit()

    cuz.execute("SELECT * FROM mvp ORDER BY score DESC LIMIT 5")
    top_players = cuz.fetchall()

    screen.fill(WHITE)
    game_over_text = big_font.render("Game Over", True, BLACK)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 100))

    y_position = 150
    for rank, (name, player_score) in enumerate(top_players, start=1):
        player_text = font.render(f"{rank}. {name}: {player_score}", True, BLACK)
        screen.blit(player_text, (SCREEN_WIDTH // 2 - player_text.get_width() // 2, y_position))
        y_position += 50

    restart_text = font.render("Press R to play again", True, BLACK)
    screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, y_position + 50))

    pygame.display.flip()

get_player_name()
show_welcome_screen()

clock = pygame.time.Clock()

def draw_triangle(x, y, size, upside_down=False):
    if upside_down:
        pygame.draw.polygon(screen, OBSTACLE_COLOR, [
            (x, y + size),
            (x - size, y - size),
            (x + size, y - size)
        ])
    else:
        pygame.draw.polygon(screen, OBSTACLE_COLOR, [
            (x, y - size),
            (x - size, y + size),
            (x + size, y + size)
        ])

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if on_ground:
                    dinosaur_y_velocity = -jump_force
                    double_jump_available = True
                elif double_jump_available:
                    dinosaur_y_velocity = -double_jump_force
                    double_jump_available = False

            elif not game_active and event.key == pygame.K_r:
                get_player_name()
                show_welcome_screen()
                game_active = False
                obstacles_bottom = []
                obstacles_top = []
                dinosaur_position = [SCREEN_WIDTH // 4, SCREEN_HEIGHT - GROUND_HEIGHT - dinosaur_radius]
                score = 0

    keys = pygame.key.get_pressed()
    if game_active:
        show_game_over_screen()
        show_top_players()


 
      
        
    dinosaur_y_velocity += 1
    dinosaur_position[1] += dinosaur_y_velocity

    if dinosaur_position[1] >= SCREEN_HEIGHT - GROUND_HEIGHT - dinosaur_radius:
        dinosaur_position[1] = SCREEN_HEIGHT - GROUND_HEIGHT - dinosaur_radius
        on_ground = True
        double_jump_available = True

    if random.randrange(0, obstacle_frequency) == 0:
        obstacle_type = random.choice(["small", "medium", "large"])
        obstacle_size = {"small": 20, "medium": 40, "large": 60}
        obstacle_rect = pygame.Rect(
            SCREEN_WIDTH,
            SCREEN_HEIGHT - GROUND_HEIGHT - obstacle_size[obstacle_type],
            obstacle_size[obstacle_type],
            obstacle_size[obstacle_type],
        )
        obstacles_bottom.append(obstacle_rect)

    if random.randrange(0, obstacle_frequency) == 0:
        obstacle_type = random.choice(["small", "medium", "large"])
        obstacle_size = {"small": 20, "medium": 40, "large": 60}
        obstacle_rect = pygame.Rect(
            SCREEN_WIDTH,
            0,
            obstacle_size[obstacle_type],
            obstacle_size[obstacle_type],
        )
        obstacles_top.append(obstacle_rect)

    for obstacle in obstacles_bottom:
        obstacle.x -= obstacle_speed

    for obstacle in obstacles_top:
        obstacle.x -= obstacle_speed

    obstacles_bottom = [obstacle for obstacle in obstacles_bottom if obstacle.right > 0]

    obstacles_top = [obstacle for obstacle in obstacles_top if obstacle.right > 0]

    for obstacle in obstacles_bottom:
        obstacle_tri = pygame.Rect(obstacle.x, obstacle.y, obstacle.width, obstacle.height)
        if pygame.Rect(dinosaur_position[0] - dinosaur_radius, dinosaur_position[1] - dinosaur_radius,
                        2 * dinosaur_radius, 2 * dinosaur_radius).colliderect(obstacle_tri):
            game_active = False
            show_game_over_screen()
            show_top_players()

    for obstacle in obstacles_top:
        obstacle_tri = pygame.Rect(obstacle.x, obstacle.y, obstacle.width, obstacle.height)
        if pygame.Rect(dinosaur_position[0] - dinosaur_radius, dinosaur_position[1] - dinosaur_radius,
                        2 * dinosaur_radius, 2 * dinosaur_radius).colliderect(obstacle_tri):
            game_active = False
            show_game_over_screen()
            show_top_players()
            break

    screen.fill(WHITE)
    pygame.draw.rect(screen, BLACK, (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
    pygame.draw.circle(screen, DINOSAUR_COLOR, (int(dinosaur_position[0]), int(dinosaur_position[1])), dinosaur_radius)

    for obstacle in obstacles_bottom:
        draw_triangle(obstacle.x + obstacle.width // 2, obstacle.y + obstacle.height // 2, obstacle.width // 2)

    for obstacle in obstacles_top:
        draw_triangle(obstacle.x + obstacle.width // 2, obstacle.y + obstacle.height // 2, obstacle.width // 2, upside_down=True)

    score += 1
    score_text = font.render(f"Score: {score}", True, OBSTACLE_COLOR)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(37)
