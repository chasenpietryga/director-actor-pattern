# director_actor_factory_pro.py
# ULTIMATE VISUAL DEMO – Optimus Factory Edition
# Press SPACE to trigger a "bad lesson" for drama

import pygame
import random
import time
import sys

pygame.init()
WIDTH, HEIGHT = 1100, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Director/Actor Pattern – Optimus Factory Live Demo")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Consolas", 18)
bigfont = pygame.font.SysFont("Consolas", 28, bold=True)

DIRECTOR_POS = (WIDTH//2, HEIGHT//2)
NUM_ACTORS = 120
CANARY_RATIO = 0.1

class Director:
    def __init__(self):
        self.lessons = 0
        self.mood = "relaxed"
        self.total_actors_terminated = 0

    def draw(self):
        pygame.draw.circle(screen, (0, 100, 255), DIRECTOR_POS, 60)
        pygame.draw.circle(screen, (255, 255, 255), DIRECTOR_POS, 60, 6)
        t = bigfont.render("DIRECTOR", True, (255, 255, 255))
        screen.blit(t, (DIRECTOR_POS[0]-70, DIRECTOR_POS[1]-100))

class Actor:
    def __init__(self, director, is_canary=False, has_bad_lesson=False):
        self.director = director
        self.is_canary = is_canary
        self.has_bad_lesson = has_bad_lesson
        angle = random.uniform(0, 6.28)
        dist = random.randint(120, 380)
        self.pos = pygame.Vector2(DIRECTOR_POS) + pygame.Vector2(dist, 0).rotate_rad(angle)
        self.target = pygame.Vector2(DIRECTOR_POS)
        self.alive = True
        self.escalating = False
        self.birth = time.time()

    def update(self, bad_lesson_active):
        if not self.alive: return
        # Move toward director
        dir_vec = self.target - self.pos
        if dir_vec.length() > 8:
            self.pos += dir_vec.normalize() * 2.5

        # Bad lesson = higher defect chance
        if self.has_bad_lesson and bad_lesson_active:
            if random.random() < 0.008:
                self.escalating = True

    def draw(self):
        if not self.alive: return
        color = (255, 255, 0) if self.is_canary else (0, 220, 100)
        if self.has_bad_lesson and bad_lesson_active:
            color = (255, 100, 100)  # Red if suffering
        pygame.draw.circle(screen, color, (int(self.pos.x), int(self.pos.y)), 16)
        if self.escalating:
            pygame.draw.line(screen, (255, 0, 0), self.pos, DIRECTOR_POS, 3)

# Global state
director = Director()
actors = []
shift = 0
start_time = time.time()
bad_lesson_active = False
defect_rate = 0.0
throughput = 0
lessons = 0

def spawn_shift():
    global actors, shift, bad_lesson_active, lessons
    shift += 1
    actors = []
    canary_count = int(NUM_ACTORS * CANARY_RATIO)
    for i in range(NUM_ACTORS):
        is_canary = i < canary_count
        has_bad = is_canary and bad_lesson_active and random.random() < 0.7
        actors.append(Actor(director, is_canary, has_bad))
    lessons += random.randint(2, 4)
    print(f"Shift {shift} spawned – {canary_count} canaries")

spawn_shift()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bad_lesson_active = not bad_lesson_active
                print("BAD LESSON TOGGLED:", bad_lesson_active)
            if event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

    screen.fill((15, 15, 35))

    # Update
    completed = 0
    defects = 0
    for a in actors[:]:
        a.update(bad_lesson_active)
        if a.pos.distance_to(pygame.Vector2(DIRECTOR_POS)) < 70:
            if a.escalating or (a.has_bad_lesson and bad_lesson_active):
                defects += 1
            completed += 1
            director.total_actors_terminated += 1
            a.alive = False

    # Auto-rollback simulation
    current_defect = defects / max(1, completed) if completed > 20 else 0
    global defect_rate
    defect_rate = defect_rate * 0.9 + current_defect * 0.1

    if defect_rate > 0.12 and bad_lesson_active:
        bad_lesson_active = False
        print("AUTOMATIC ROLLBACK – Defect rate too high!")

    throughput = completed / max(0.1, time.time() - start_time)

    if time.time() - start_time > 10:
        spawn_shift()
        start_time = time.time()

    # Draw
    director.draw()
    for a in actors:
        a.draw()

    # HUD
    y = 20
    def txt(t, c=(255,255,255)):
        nonlocal y
        screen.blit(font.render(t, True, c), (WIDTH-380, y))
        y += 28

    screen.fill((0,0,0), (WIDTH-400, 0, 400, HEIGHT))
    y = 20
    txt("DIRECTOR/ACTOR PATTERN", (255,255,100))
    txt(f"Shift: {shift}          Actors: {len(actors)}", (200,255,200))
    txt(f"Throughput: {throughput:.1f} parts/sec")
    txt(f"Defect Rate: {defect_rate:.3f}", (255,100,100) if defect_rate>0.08 else (100,255,100))
    txt(f"Lessons Learned: {lessons}", (100,255,255))
    txt(f"Canaries: {int(NUM_ACTORS*CANARY_RATIO)} (yellow)")
    txt("Bad lesson active:" if bad_lesson_active else "All lessons safe", (255,100,100) if bad_lesson_active else (100,255,100))
    txt("SPACE = toggle bad lesson", (180,180,180))
    txt("Only the Director needs GPUs", (255,200,100))
    txt("100× cheaper than full brains", (255,200,100))

    pygame.display.flip()
    clock.tick(60)
