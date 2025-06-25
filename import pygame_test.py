import pygame
import time
import random
import os

TILE_SIZE = 50
BACKGROUND_COLOR = (110, 110, 5)

class Apple:
    def __init__(self, game_surface):
        self.game_surface = game_surface
        if os.path.exists("resources/apple.jpg"):
            self.image = pygame.image.load("resources/apple.jpg").convert()
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        else:
            self.image = None
        self.position = [TILE_SIZE * 3, TILE_SIZE * 3]

    def draw(self):
        if self.image:
            self.game_surface.blit(self.image, self.position)
        else:
            pygame.draw.rect(self.game_surface, (255, 0, 0), (*self.position, TILE_SIZE, TILE_SIZE))

    def move(self):
        self.position[0] = random.randint(1, 19) * TILE_SIZE
        self.position[1] = random.randint(1, 14) * TILE_SIZE

class Snake:
    def __init__(self, game_surface, length=1):
        self.game_surface = game_surface
        if os.path.exists("resources/snake_body.jpg"):
            self.image = pygame.image.load("resources/snake_body.jpg").convert()
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        else:
            self.image = None
        self.length = length
        self.positions = [[TILE_SIZE] * length, [TILE_SIZE] * length]
        self.direction = 'down'

    def change_direction(self, new_direction):
        if new_direction in ['left', 'right', 'up', 'down']:
            self.direction = new_direction

    def move(self):
        for i in range(self.length - 1, 0, -1):
            self.positions[0][i] = self.positions[0][i-1]
            self.positions[1][i] = self.positions[1][i-1]

        if self.direction == 'left':
            self.positions[0][0] -= TILE_SIZE
        elif self.direction == 'right':
            self.positions[0][0] += TILE_SIZE
        elif self.direction == 'up':
            self.positions[1][0] -= TILE_SIZE
        elif self.direction == 'down':
            self.positions[1][0] += TILE_SIZE

        self.draw()

    def draw(self):
        self.game_surface.fill(BACKGROUND_COLOR)
        for i in range(self.length):
            if self.image:
                self.game_surface.blit(self.image, (self.positions[0][i], self.positions[1][i]))
            else:
                pygame.draw.rect(self.game_surface, (255, 255, 0), (self.positions[0][i], self.positions[1][i], TILE_SIZE, TILE_SIZE))

    def grow(self):
        self.length += 1
        self.positions[0].append(-1)
        self.positions[1].append(-1)

class Obstacle:
    def __init__(self, game_surface):
        self.game_surface = game_surface
        self.positions = [
            (200, 200), (250, 200), (300, 200),
            (600, 400), (650, 400), (700, 400),
            (500, 100), (500, 250), (500, 200),
            (900, 400), (900, 400), (900, 400)
        ]

    def draw(self):
        for pos in self.positions:
            pygame.draw.rect(self.game_surface, (100, 100, 100), (pos[0], pos[1], TILE_SIZE, TILE_SIZE))

    def check_collision(self, x, y):
        for pos in self.positions:
            if x >= pos[0] and x < pos[0] + TILE_SIZE and y >= pos[1] and y < pos[1] + TILE_SIZE:
                return True
        return False

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake and Apple Game")
        pygame.mixer.init()
        self.play_background_music()

        self.surface = pygame.display.set_mode((1000, 800))
        self.snake = Snake(self.surface, length=1)
        self.apple = Apple(self.surface)
        self.obstacle = Obstacle(self.surface)

    def play_background_music(self):
        if os.path.exists('resources/bg_music_1.mp3'):
            pygame.mixer.music.load('resources/bg_music_1.mp3')
            pygame.mixer.music.play(-1, 0)

    def play_sound_effect(self, sound_name):
        sound = None
        if sound_name == "crash" and os.path.exists("resources/crash.mp3"):
            sound = pygame.mixer.Sound("resources/crash.mp3")
        elif sound_name == 'ding' and os.path.exists("resources/ding.mp3"):
            sound = pygame.mixer.Sound("resources/ding.mp3")
        if sound:
            pygame.mixer.Sound.play(sound)

    def reset_game(self):
        self.snake = Snake(self.surface, length=1)
        self.apple = Apple(self.surface)
        self.obstacle = Obstacle(self.surface)

    def check_collision(self, x1, y1, x2, y2):
        return x1 >= x2 and x1 < x2 + TILE_SIZE and y1 >= y2 and y1 < y2 + TILE_SIZE

    def render_background(self):
        if os.path.exists("resources/background.jpg"):
            bg = pygame.image.load("resources/background.jpg")
            self.surface.blit(bg, (0, 0))
        else:
            self.surface.fill((0, 0, 0))

    def play(self):
        self.render_background()
        self.snake.move()
        self.apple.draw()
        self.obstacle.draw()
        self.display_score()
        pygame.display.flip()

        head_x = self.snake.positions[0][0]
        head_y = self.snake.positions[1][0]

        if (head_x < 0 or head_x >= self.surface.get_width() or
            head_y < 0 or head_y >= self.surface.get_height()):
            self.play_sound_effect('crash')
            raise Exception("Oops! The snake collided with the boundary.")

        if self.check_collision(head_x, head_y, self.apple.position[0], self.apple.position[1]):
            self.play_sound_effect("ding")
            self.snake.grow()
            self.apple.move()

        for i in range(3, self.snake.length):
            if self.check_collision(head_x, head_y, self.snake.positions[0][i], self.snake.positions[1][i]):
                self.play_sound_effect('crash')
                raise Exception("Oops! The snake collided with itself.")

        if self.obstacle.check_collision(head_x, head_y):
            self.play_sound_effect('crash')
            raise Exception("Oops! The snake hit an obstacle!")

    def display_score(self):
        font = pygame.font.SysFont('arial', 30)
        score_text = font.render(f"Score: {self.snake.length}", True, (200, 200, 200))
        self.surface.blit(score_text, (850, 10))

    def show_game_over(self):
        self.render_background()
        font = pygame.font.SysFont('arial', 30)
        line1 = font.render(f"Game over! Your score: {self.snake.length}", True, (255, 255, 255))
        self.surface.blit(line1, (200, 300))
        line2 = font.render("Press Enter to play again or Escape to exit.", True, (255, 255, 255))
        self.surface.blit(line2, (200, 350))
        pygame.mixer.music.pause()
        pygame.display.flip()

    def run(self):
        running = True
        pause = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_RETURN:
                        pygame.mixer.music.unpause()
                        pause = False
                    elif event.key == pygame.K_SPACE:
                        pause = not pause  # Toggle pause state
                    if pause:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                        
                    if not pause:
                        if event.key == pygame.K_LEFT:
                            self.snake.change_direction('left')
                        elif event.key == pygame.K_RIGHT:
                            self.snake.change_direction('right')
                        elif event.key == pygame.K_UP:
                            self.snake.change_direction('up')
                        elif event.key == pygame.K_DOWN:
                            self.snake.change_direction('down')

                elif event.type == pygame.QUIT:
                    running = False

            try:
                if not pause:
                    self.play()

            except Exception as e:
                self.show_game_over()
                pause = True
                self.reset_game()

            time.sleep(0.2)

if __name__ == '__main__':
    game = Game()
    game.run()
