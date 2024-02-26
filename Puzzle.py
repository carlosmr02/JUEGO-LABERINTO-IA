import pygame
import sys
import heapq

# Constants
SCREEN_WIDTH = 648
SCREEN_HEIGHT = 480
GRID_SIZE = 24


class Wall:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = pygame.transform.scale(pygame.image.load('assets/images/muro.png'), (GRID_SIZE, GRID_SIZE))

    def draw(self, screen):
        screen.blit(self.image, (self.x * GRID_SIZE, self.y * GRID_SIZE))

    def get_position(self):
        return self.x, self.y


class FinishPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = pygame.transform.scale(pygame.image.load('assets/images/final.png'), (GRID_SIZE, GRID_SIZE))

    def draw(self, screen):
        screen.blit(self.image, (self.x * GRID_SIZE, self.y * GRID_SIZE))

    def get_coordinates(self):
        return self.x, self.y


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = pygame.transform.scale(pygame.image.load('assets/images/mozo.png'), (GRID_SIZE, GRID_SIZE))

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def draw(self, screen):
        screen.blit(self.image, (self.x * GRID_SIZE, self.y * GRID_SIZE))

    def get_position(self):
        return self.x, self.y


class ArrowButton:
    def __init__(self, x, y, image_path):
        self.rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
        self.image = pygame.transform.scale(pygame.image.load(image_path), (GRID_SIZE, GRID_SIZE))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


class Spike:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = pygame.transform.scale(pygame.image.load('assets/images/spikes.png'), (GRID_SIZE, GRID_SIZE))

    def draw(self, screen):
        screen.blit(self.image, (self.x * GRID_SIZE, self.y * GRID_SIZE))

    def get_position(self):
        return self.x, self.y


class PuzzleGame:
    def __init__(self, level):
        self.level = level
        self.walls = []
        self.finish_points = []
        self.spikes = []
        self.player = None
        self.load_level()
        self.game_over = False

    def load_level(self):
        for y, row in enumerate(self.level):
            for x, char in enumerate(row):
                if char == '#':
                    self.walls.append(Wall(x, y))
                elif char == 'F':
                    self.finish_points.append(FinishPoint(x, y))
                elif char == 'P':
                    self.player = Player(x, y)
                elif char == 'B':
                    self.spikes.append(Spike(x, y))

    def move_player(self, dx, dy):
        new_x = self.player.x + dx
        new_y = self.player.y + dy

        if new_x < 0 or new_x >= len(self.level[0]) or new_y < 0 or new_y >= len(self.level):
            return

        if (new_x, new_y) in [(wall.x, wall.y) for wall in self.walls]:
            return

        if (new_x, new_y) in [(spike.x, spike.y) for spike in self.spikes]:
            self.game_over = True

        self.player.move(dx, dy)

    def is_game_finished(self):
        if (self.player.x, self.player.y) in [(finish_point.x, finish_point.y) for finish_point in self.finish_points]:
            return True
        return False

    def draw(self, screen):
        # Draw the level
        for wall in self.walls:
            wall.draw(screen)
        for finish_point in self.finish_points:
            finish_point.draw(screen)
        for spike in self.spikes:
            spike.draw(screen)

        self.player.draw(screen)


def cargar_nivel(nombre_archivo):
    with open(nombre_archivo, 'r') as file:
        nivel = [line.strip() for line in file]
    return nivel


def show_message(screen, message):
    screen.fill((0, 0, 0))  # Llena la pantalla con color negro
    font = pygame.font.Font(None, 36)
    text = font.render(message, True, (255, 255, 255))
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.delay(2000)
    screen.fill((0, 0, 0))

def a_star(start, goal, walls, spikes):
    open_list = []
    closed_set = set()

    heapq.heappush(open_list, (0, start))
    came_from = {}

    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_list:
        current = heapq.heappop(open_list)[1]

        if current == goal:
            path = reconstruct_path(came_from, current)
            return path

        closed_set.add(current)

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)

            if neighbor in closed_set or neighbor in [(wall.x, wall.y) for wall in walls] or neighbor in [(spike.x, spike.y) for spike in spikes]:
                continue

            tentative_g_score = g_score[current] + 1

            if neighbor not in [item[1] for item in open_list] or tentative_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(open_list, (f_score[neighbor], neighbor))

    return None



def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def reconstruct_path(came_from, current):
    total_path = [current]

    while current in came_from:
        current = came_from[current]
        total_path.append(current)

    return total_path[::-1]


def run(map):
    nombre_archivo = map
    level_map = cargar_nivel(nombre_archivo)

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    game = PuzzleGame(level_map)
    start = game.player.get_position()
    goal = game.finish_points[0].get_coordinates()
    path = []
    movements = len(a_star(start, goal, game.walls, game.spikes)) + 10

    font_movement = pygame.font.Font(None, 24)
    movements_text = font_movement.render(f'Movimientos: {movements}', True, (255, 255, 255))
    movements_rect = movements_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))
    ia = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and ia == False:
                if event.key == pygame.K_UP:
                    game.move_player(0, -1)
                    start = game.player.get_position()
                    movements -= 1
                elif event.key == pygame.K_DOWN:
                    game.move_player(0, 1)
                    start = game.player.get_position()
                    movements -= 1
                elif event.key == pygame.K_LEFT:
                    game.move_player(-1, 0)
                    start = game.player.get_position()
                    movements -= 1
                elif event.key == pygame.K_RIGHT:
                    game.move_player(1, 0)
                    start = game.player.get_position()
                    movements -= 1
                elif event.key == pygame.K_1:
                    path = a_star(start, goal, game.walls, game.spikes)
                    ia = True
        screen.fill((0, 0, 0))

        if path:
            next_step = path.pop(0)
            dx = next_step[0] - start[0]
            dy = next_step[1] - start[1]
            game.move_player(dx, dy)
            start = next_step
            movements -= 1

        game.draw(screen)
        movements_text = font_movement.render(f'Movimientos: {movements}', True, (255, 255, 255))
        screen.blit(movements_text, movements_rect)

        pygame.display.flip()
        clock.tick(30)

        if movements == 0:
            game.game_over = True

        if game.is_game_finished():
            show_message(screen, "¡Juego completado!")
            pygame.time.delay(2000)
            pygame.quit()
            sys.exit()
        elif game.game_over:
            show_message(screen, "Has perdido")
            pygame.time.delay(2000)
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    run("assets/maps/Mapa 2.txt")
