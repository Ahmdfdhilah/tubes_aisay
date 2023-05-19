from ast import With
from asyncio import current_task
from glob import iglob
from importlib.util import set_loader
from lib2to3.pytree import convert
from turtle import update
import pygame
import random
import os
from pygame.locals import *
import threading

BACKGROUND_WIDTH = 400
BACKGROUND_HEIGHT = 640
FPS = 80


# Warna
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BG = (100, 100, 100)

# Health Bar
HEALTH_WIDTH = 200
HEALTH_HEIGHT = 20

mouse_pos = (0, 0)
show_mouse_pos = True

game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, "Assets")
car_folder = os.path.join(img_folder, "Car")
life_folder = os.path.join(img_folder, "Lifebar")
object_folder = os.path.join(img_folder, "Object")

def play_sound(sound_file):
    pygame.mixer.Channel(1).play(pygame.mixer.Sound(sound_file))

def play_sound_threaded(sound_file):
    sound_thread = threading.Thread(target=play_sound, args=(sound_file,))
    sound_thread.start()

def draw_text(text, font_size, font_color, x, y):
    font = pygame.font.SysFont(None, font_size)
    text_surface = font.render(text, True, font_color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((BACKGROUND_WIDTH, BACKGROUND_HEIGHT))
pygame.display.set_caption('Car Racing')
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, car):
        super().__init__()
        self.image = pygame.image.load(os.path.join(car_folder, car)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 4
        self.slippery = False
        self.slide_direction = 0  # Menyimpan arah pergerakan saat efek slippery aktif
        self.slide_counter = 0 
        self.slide_duration = 60
    def update(self):
        key = pygame.key.get_pressed()
        if not self.slippery :
            if key[pygame.K_RIGHT] and self.rect.right < 357:
                self.rect.move_ip(self.speed, 0)
            if key[pygame.K_LEFT] and self.rect.left > 45:
                self.rect.move_ip(-self.speed, 0)
        else:
             # Logika pergerakan player saat efek slippery aktif
            self.slide_counter += 1
            if self.slide_counter >= 1 and self.slide_counter <= self.slide_duration:
                if self.slide_counter % 10 == 0:
                    # Setiap 10 frame, ubah arah pergerakan secara acak
                    self.slide_direction = random.choice([-1, 1])
                self.rect.move_ip(self.speed * self.slide_direction, 0)
            else:
                # Menghentikan efek slippery setelah durasi tertentu
                self.slide_counter = 0
                self.slide_direction = 0
                self.slippery = False

        if self.slippery and not self.slide_direction == 0:
            self.speed = 2  # Mengurangi kecepatan saat efek slippery aktif
        else:
            self.speed = 4


class PanahJalan(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(os.path.join(object_folder, "arrow_white.png")).convert_alpha(), (100, 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        if self.rect.y > BACKGROUND_HEIGHT:
            self.kill()

class Car(pygame.sprite.Sprite):
    def __init__(self, x, img):
        super().__init__()
        self.image = pygame.transform.rotate(img, 180)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = -250
        self.hit = False
        
    def update(self):
        if self.rect.y > BACKGROUND_HEIGHT:
            self.kill()
        else:
            self.rect.y += random.randint(1, 3)

class Oli(pygame.sprite.Sprite):
    def __init__(self, x, img):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = -50
        self.hit = False

    def update(self):
        if self.rect.y > BACKGROUND_HEIGHT:
            self.kill()

class Bensin(pygame.sprite.Sprite):
    def __init__(self, x, img):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = -50
        self.hit = False

    def update(self):
        if self.rect.y > BACKGROUND_HEIGHT:
            self.kill()
current_car = 0
tribune = pygame.transform.rotate(pygame.image.load(os.path.join(object_folder, "tribune.png")).convert_alpha(), 90)
tribune_kiri = pygame.transform.scale(tribune, (144, BACKGROUND_HEIGHT))
tribune_kanan = pygame.transform.scale(tribune, (144, BACKGROUND_HEIGHT))

def draw_main_menu():
       car_image = pygame.image.load(f"./Assets/Car/car_{current_car}.png").convert_alpha()
       car_rect = car_image.get_rect()
       car_rect.center = (BACKGROUND_WIDTH // 2, BACKGROUND_HEIGHT // 2 - 50)
       screen.blit(car_image, car_rect)
       draw_text("Press SPACE to Play", 30, WHITE, BACKGROUND_WIDTH // 2, BACKGROUND_HEIGHT // 2 + 200)
       draw_text("Press ESC to Exit", 30, WHITE, BACKGROUND_WIDTH // 2, BACKGROUND_HEIGHT // 2 + 250)
       selected_car_text = urutan_mobil[current_car]
       draw_text("<-  "+selected_car_text+"  ->", 30, WHITE, BACKGROUND_WIDTH // 2, BACKGROUND_HEIGHT // 2 + 150)

car_list = []
car_list_img = []
for i in range(8):
    img = pygame.image.load(os.path.join(car_folder, "car_{}.png".format(i))).convert_alpha()
    car_list.append(img)
    car_list_img.append(f"car_{i}.png")

oli_list = pygame.image.load(os.path.join(object_folder, "oil.png")).convert_alpha()

bensin_img = pygame.image.load(os.path.join(object_folder, "last.png")).convert_alpha()

all_sprites = pygame.sprite.Group()
panahGrup = pygame.sprite.Group()
cars = pygame.sprite.Group()
oils = pygame.sprite.Group()
bensins = pygame.sprite.Group()

objOli = Oli(random.randrange(82, 302), oli_list)
oils.add(objOli)
  

mobil = Car(random.randrange(82, 302), random.choice(car_list))
cars.add(mobil)

for i in range(3):
    panah = PanahJalan(BACKGROUND_WIDTH//2 -50, i * 230 + 40)
    panahGrup.add(panah)


urutan_mobil = ["Honda Jazz", "Rubicon", "Civic", "Taxi", "Camri", "SLK100", "Supra GTR"]

# Health Bar
health = 100

# Score
score = 0
score_font = pygame.font.SysFont(None, 30)
run = True
scene = {
    0: "MAIN MENU",
    1: "PLAY",
    2: "GAME OVER",
}


player = Player(BACKGROUND_WIDTH // 2 - 30, BACKGROUND_HEIGHT // 2 + 100, f"car_{current_car}.png")
all_sprites.add(player)
current_scene = 0
pygame.mixer.music.load("sound/backsound.mp3")  # Load file musik
pygame.mixer.music.set_volume(0.4)
pygame.mixer.music.play(-1)

while run:
    clock.tick(FPS)
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            run = False
        if event.type == KEYUP:
            if event.key == K_r and current_scene == 2:
                all_sprites.empty()
                panahGrup.empty()
                cars.empty()
                oils.empty()
                bensins.empty()
              
                objOli = Oli(random.randrange(82, 302), random.choice(oli_list))
                oils.add(objOli)

                mobil = Car(random.randrange(82, 302), random.choice(car_list))
                cars.add(mobil)

                for i in range(3):
                    panah = PanahJalan(BACKGROUND_WIDTH//2 -50, i * 230 + 40)
                    panahGrup.add(panah)

                player = Player(BACKGROUND_WIDTH // 2 - 30, BACKGROUND_HEIGHT // 2 + 100,f"car_{current_car}.png")
                all_sprites.add(player)
                # Reset health
                health = 100

                # Reset score
                score = 0

                current_scene = 1

        if event.type == KEYDOWN:
            if scene.get(current_scene) == "MAIN MENU":
                if event.key == K_RIGHT:
                    current_car = (current_car + 1) % len(urutan_mobil)
                elif event.key == K_LEFT:
                    current_car = (current_car - 1) % len(urutan_mobil)
                player.image = pygame.image.load(os.path.join(car_folder, f"car_{current_car}.png")).convert_alpha()    
            if event.key == K_x:
                show_mouse_pos = not show_mouse_pos

            mouse_pos = pygame.mouse.get_pos()
            if event.key == K_ESCAPE and current_scene == 0:
                run = False
            if event.key == K_ESCAPE and current_scene == 2:
                run = False
            if event.key == K_SPACE and current_scene == 0:
                current_scene = 1

    if scene.get(current_scene) == "PLAY": 
        for panah in panahGrup:
            panah.rect.y += 2
        for car in cars:
            car.rect.y += 3
        for oli in oils:
            oli.rect.y += 2
        for bensin in bensins:
            bensin.rect.y += 2
        while len(panahGrup) < 3:
            panah_new = PanahJalan(BACKGROUND_WIDTH // 2 - 50, -50)
            panahGrup.add(panah_new)
        while len(cars) < 1:
            mobil_new = Car(random.randrange(82, 302), random.choice(car_list))
            cars.add(mobil_new)
        while len(oils) < 1:
            oli_new = Oli(random.randrange(82, 302), oli_list)
            oils.add(oli_new)
        while len(bensins) < 1:
            bensin_new = Bensin(random.randrange(82, 302), bensin_img)
            bensins.add(bensin_new)
        # Check Collision
        kena_mobil = pygame.sprite.spritecollide(player, cars, True)
        if kena_mobil:
            for m in kena_mobil:
                if not m.hit:
                    m.hit = True
                    health -= 15
                    if health <= 0:
                        current_scene = 2
            play_sound_threaded("sound/Duar.mp3")
          
        kena_oli = pygame.sprite.spritecollide(player, oils, True)
        if kena_oli:
            for objOli in kena_oli:
                if not objOli.hit:
                    objOli.hit = True
                    health -= 5
                    if health <= 0:
                        current_scene = 2
            player.slippery = True
            play_sound_threaded("sound/ngepot.mp3")

        kena_bensin = pygame.sprite.spritecollide(player, bensins, True)
        if kena_bensin:
            for bensin in kena_bensin:
                if not bensin.hit:
                    bensin.hit = True
                    health += 5
                    if health > 100:
                        health = 100
        
        all_sprites.update()
        panahGrup.update()
        cars.update()
        oils.update()
        bensins.update()

        # Increase score
        score += 0.001
        score = round(score,3)

    screen.fill(BG)

    screen.blit(tribune_kiri, (-105, 0))
    screen.blit(tribune_kanan, (BACKGROUND_WIDTH - 40, 0))

    if scene.get(current_scene) == "MAIN MENU":
       draw_main_menu()
    if scene.get(current_scene) == "PLAY": 
        panahGrup.draw(screen)
        oils.draw(screen)
        cars.draw(screen)
        bensins.draw(screen)
        all_sprites.draw(screen)

        # Draw Health Bar
        pygame.draw.rect(screen, GREEN, (10, 10, health, 20))
        pygame.draw.rect(screen, WHITE, (10, 10, 100, 20), 2)

        # Draw Score
        score_text = score_font.render("Score: " + str(score), True, WHITE)
        screen.blit(score_text, (10, 40))

    if scene.get(current_scene) == "GAME OVER":
        draw_text("GAME OVER", 40, WHITE, BACKGROUND_WIDTH // 2 - 120, BACKGROUND_HEIGHT // 4)
        draw_text("Final Score : {}".format(score), 30, WHITE, BACKGROUND_WIDTH // 2 - 100, BACKGROUND_HEIGHT // 2 + 100)
        draw_text("Press R to Restart", 30, WHITE, BACKGROUND_WIDTH // 2 - 100, BACKGROUND_HEIGHT // 2)
        draw_text("Press ESC to Exit", 30, WHITE, BACKGROUND_WIDTH // 2 - 100, BACKGROUND_HEIGHT // 2 + 50)

    pygame.display.flip()

pygame.mixer.music.stop() 
pygame.quit()