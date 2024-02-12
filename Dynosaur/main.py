# Kirjastojen "lisäys"
import pygame,sys,random

# Näppäinten "importtaus". Lähinnä helpottaa näppäin accessia myöhemmin koodissa.
from pygame.locals import(
    K_LEFT,
    K_RIGHT,
    K_ESCAPE,
    K_SPACE,
    KEYDOWN,
    QUIT    
)

# Pygame:n setuppausta
pygame.init()
pygame.font.init()
my_font = pygame.font.Font('Harjoitustyö\Fonts\PokemonGB.ttf', 15)
my_fontBIG = pygame.font.Font('Harjoitustyö\Fonts\PokemonGB.ttf', 25)
BLACK = (0,0,0)


# Määritellään globaaleja vakioita myöhempää käyttöä varten:
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
TARGET_FPS = 60
GAME_SPEED = 2
gameStarted = False
score = 0
LOPPUTEKSTI = ''
GAME_ENDED = False
new_line = '\n'
PLATFORMINTERVAL = 1600

screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))          # Näyttöikkunan luonti. Parametrinä ikkunan koko globaaleista muuttujista.
pygame_icon = pygame.image.load('Harjoitustyö\Assets\doux_icon.png')    # Näyttöikkunan "ikonin" lataus
pygame.display.set_icon(pygame_icon)                                    # Näyttöikkunan "ikoni"
pygame.display.set_caption('Dynosaur')                                  # Näyttöikkunan "title"
clock = pygame.time.Clock()                                             # Peliin lisättävä aikamuuttuja nopeuden hallitsemiseen.

# Pygamen "Sprite group":ien perustuksia. Käyttätarkoitus on "collision handlinggissa" ja renderöintijärjestyksessä.
collision_sprites = pygame.sprite.Group()
visible_sprites = pygame.sprite.Group()
active_sprites = pygame.sprite.Group()
start_sprites = pygame.sprite.Group()
cloud_sprites = pygame.sprite.Group()

# Luokat eri peliobjekteille
class Player(pygame.sprite.Sprite):                 # Perii Pygamen omia luokkastruktuureja.
    def __init__(self, pos, collision_sprites):     
        super().__init__()
        self.last_update = 0
        self.animation_cooldown = 100
        self.frame = 0
        self.currentframe = self.frame
        self.image = animation_list_IDLE[0]
        self.rect = pygame.Rect(0, 0, 35, 65)
        self.rect.topleft = (pos)
        active_sprites.add(self)
        
        # Pelaajan liikutushommat:
        self.direction = pygame.math.Vector2()
        self.speed = 8
        self.gravity = 1
        self.jump_speed = 20
        self.collision_sprites = collision_sprites
        self.is_grounded = False

        # Animoinnin orientaatio ja tarvittavien työkalujen setuppaus.
        self.status = 'IDLE'
        self.is_flipped = False
        self.lista = []

        # Pelaajaluokan omat funktiot.
        # Liikkuminen 
    def input(self):
        keys = pygame.key.get_pressed()

        if keys[K_RIGHT]:
            self.direction.x = 1
            self.is_flipped = False
        elif keys[K_LEFT]:
            self.isflipped = True
            self.direction.x = -1
        else:
            self.direction.x = 0        

        if keys[K_SPACE] and self.is_grounded == True:
            self.direction.y = -self.jump_speed

        # Törmäilyn checkaus
    def vertical_collisions(self):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if self.rect.centery < sprite.rect.bottom:
                    if self.direction.y > 0:
                        self.direction.y = 0
                        self.rect.bottom = sprite.rect.top
                        self.is_grounded = True
        if self.is_grounded and self.direction.y != 0:
            self.is_grounded = False

        # Animoinnin managerointityökalu
    def statusmanager(self):
        if self.direction.x < 0:
            self.lista = animation_list_RUN
            self.is_flipped = True
            #print('juoksee vasemmalle')
        if self.direction.x > 0:
            self.lista = animation_list_RUN
            self.flip = False
            #print('juoksee oikeelle')
        if self.direction.x == 0:
            self.lista = animation_list_IDLE
            #print('henggaa paikallaan')

        # Pelaajan näytöllä pysymisehdot
    def boundaries(self):
        if self.rect.x < 0:
            self.rect.x = 0

        if self.rect.x > SCREEN_WIDTH - 40:
            self.rect.x = SCREEN_WIDTH - 40

        # Animoinnin kuvaindeksin pyötiytystyökalu
    def animatorIndex(self, list):
        self.current_time = pygame.time.get_ticks()        
        if self.current_time - self.last_update >= self.animation_cooldown:
            self.currentframe +=1
            self.last_update = self.current_time
            if self.currentframe >= 4:
                self.currentframe = 0

        return self.currentframe

        # Pelaajaan vaikuttava "Vetovoima"
    def apply_gravity(self):
        self.direction.y += self.gravity
        self.rect.y += self.direction.y

        # Pelaajan renderöintifunktio (jostain syystä en saanut toimimaan animointia spritegroupin kautta renderöitynä)
    def draw(self):
        screen.blit(pygame.transform.flip(self.lista[self.animatorIndex(self.lista)].convert_alpha(), self.is_flipped, False), (self.rect.x - 17, self.rect.y+10))

        # Updatefunktio, joka kutsuu kaikkia pelaajan handlaamiseen tavittavia funktioita, ettei kaikkia tarvitse erikseen kutsua "Game loopissa"
    def update(self):
        self.input()
        self.rect.x += self.direction.x * self.speed
        self.apply_gravity()
        self.vertical_collisions()
        self.boundaries()
        self.statusmanager()
        self.draw()

class Platform(pygame.sprite.Sprite):
    def __init__(self):
        super(Platform, self).__init__()
        self.image = pygame.transform.scale(platform, (((50) + random.random() * 200)*(1-(1/score)), 20 )) # Platformin koko (leveys, korkeus)
        self.rect = self.image.get_rect(
            center = (
                random.randint(0, SCREEN_WIDTH), 0)                     # Platformin spawnikohta (x, y)
        )

    def update(self):
        if gameStarted == True:
            self.rect.y += GAME_SPEED
        if self.rect.y > SCREEN_HEIGHT:
            self.kill()

class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super(Cloud, self).__init__()
        self.image = pygame.transform.scale(cloud, (random.randint(60,120), random.randint(40,70)))
        self.rect = self.image.get_rect()
        self.speed = random.randrange(1,4)-2
        self.rect = self.image.get_rect(
            center = (
                random.randint(-50, SCREEN_WIDTH + 50), -40)                     # Platformin spawnikohta (x, y)
        )

    def update(self):
        self.rect.y += 1
        self.rect.x += self.speed
        if self.rect.y > SCREEN_HEIGHT + 20:
            self.kill()
        # Pelin alkuun "hard koodattujen" tasojen luokka.
class Surface(pygame.sprite.Sprite):
    def __init__(self, x, y, width):
        super(Surface, self).__init__()
        self.image = pygame.transform.scale(platform, (width, 20))
        self.rect = self.image.get_rect()
        self.rect = self.image.get_rect(topleft = (x,y))
        visible_sprites.add(self)
        collision_sprites.add(self)
        start_sprites.add(self)
    
    def update(self):
        if gameStarted == True:
            self.rect.y += GAME_SPEED
        if self.rect.y > SCREEN_HEIGHT + 40:
            self.kill()

class SpriteSheet():
    def __init__(self, image):
        self.sheet = image

    def get_image(self, frame, width, height, scale, colour):
        image = pygame.Surface((width, height)).convert_alpha()
        image.blit(self.sheet, (0,0), ((frame * width), 0, width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        image.set_colorkey(colour)
        return image

        # Pelin alku ja lopputilanteiden funktiot.
def endgame():
        with open('Harjoitustyö\ennätykset.txt', 'w') as f:
            
            if score > highscoreint:
                f.writelines(f'{score}')
                result = 'WIN'
            else:
                f.writelines(f'{highscore}')
                result = 'LOOSE'
        return result

def startgame():
        screen.blit(my_font.render(f'Welcome to ', False, (0, 0, 0)), (115,20))
        screen.blit(my_fontBIG.render(f'Dynosaur ', False, (0, 0, 0)), (100,50))
        screen.blit(my_font.render(f'Arrows to move', False, (0, 0, 0)), (90,100))
        screen.blit(my_font.render(f'Space to jump', False, (0, 0, 0)), (100,120))
        screen.blit(my_font.render(f'Esc to quit', False, (0, 0, 0)), (120,140))
        screen.blit(my_font.render(f'credits in another file', False, (0, 0, 0)), (30,180))
        
# Grafiikat
# Grafiikka listojen setuppaus ja kuvien importtaus.
DinoSHEET = pygame.image.load('Harjoitustyö\Assets\doux.png').convert_alpha()
sprite_sheet = SpriteSheet(DinoSHEET)

animation_list_IDLE = []
animation_list_RUN = []
animation_list_DEATH = []

animation_list_IDLE.append(sprite_sheet.get_image(0, 24, 24, 3, BLACK))
animation_list_IDLE.append(sprite_sheet.get_image(1, 24, 24, 3, BLACK))
animation_list_IDLE.append(sprite_sheet.get_image(2, 24, 24, 3, BLACK))
animation_list_IDLE.append(sprite_sheet.get_image(3, 24, 24, 3, BLACK))
animation_list_RUN.append(sprite_sheet.get_image(4, 24, 24, 3, BLACK))
animation_list_RUN.append(sprite_sheet.get_image(5, 24, 24, 3, BLACK))
animation_list_RUN.append(sprite_sheet.get_image(6, 24, 24, 3, BLACK))
animation_list_RUN.append(sprite_sheet.get_image(7, 24, 24, 3, BLACK))
animation_list_RUN.append(sprite_sheet.get_image(8, 24, 24, 3, BLACK))
animation_list_RUN.append(sprite_sheet.get_image(9, 24, 24, 3, BLACK))
animation_list_DEATH.append(sprite_sheet.get_image(10, 24, 24, 3, BLACK))

bg = pygame.image.load('Harjoitustyö\Assets\skybox.png').convert_alpha()
cloud = pygame.image.load('Harjoitustyö\Assets\cloud.png').convert_alpha()
platform = pygame.image.load('Harjoitustyö\Assets\platform.png').convert_alpha()
panel = pygame.image.load('Harjoitustyö\Assets\panel.jpg').convert_alpha()
panel = pygame.transform.scale(panel, (400, 60))

# Pygamen Event handlerin koodi.
ADDPLATFORM = pygame.USEREVENT + 1
pygame.time.set_timer(ADDPLATFORM, PLATFORMINTERVAL)

ADDCLOUD = pygame.USEREVENT + 2
pygame.time.set_timer(ADDCLOUD, 2000)

# Hard koodatut aloituspalat
surface1 = Surface(50, SCREEN_HEIGHT - 200, 150)
surface2 = Surface(120, SCREEN_HEIGHT - 400, 100)
surface3 = Surface(250, SCREEN_HEIGHT - 600, 50)
surface1 = Surface(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH)

# Ennätystpisteiden luku tekstitiedostosta Lisäksi Error handling, jos joku kehveli on peukaloinut tiedostoa
with open('Harjoitustyö\ennätykset.txt', 'r') as ennatykset:
    try:
        highscore = str(ennatykset.readlines()).strip("['] ")
        highscoreint = int(highscore)
    except ValueError:
        highscore = 100
        highscoreint = int(highscore)
        

# Pelaaja -olion luonti "Pelaaja" -luokasta
player = Player((SCREEN_WIDTH // 2,SCREEN_HEIGHT - 250), collision_sprites)

# Pelin käyntiehto ja apumuuttujan perustus
running = True
apu = 0

# Game loop:
while running:

    # Taustakuvan piirto:
    screen.blit(bg, (0,0))
    # Eri spritejen päivitys ja piirto
    visible_sprites.draw(pygame.display.get_surface())
    active_sprites.update()
    start_sprites.update()

    # Pygamen "event system" Tähän "eventit"
    for event in pygame.event.get():
        # Pelin sulkemistaphtuma
        if event.type == KEYDOWN:
            # Sulkeminen Esc näppäimellä
            if event.key == K_ESCAPE:
                running = False
        # Sulkeminen yläkulman ruksista
        elif event.type == QUIT:
            running = False

        elif event.type == ADDPLATFORM:
            if gameStarted == True:
                new_platform = Platform()
                active_sprites.add(new_platform)
                collision_sprites.add(new_platform)
                visible_sprites.add(new_platform)
                
        elif event.type == ADDCLOUD:
            if gameStarted == True:
                new_cloud = Cloud()
                cloud_sprites.add(new_cloud)

    cloud_sprites.update()
    cloud_sprites.draw(pygame.display.get_surface())            
    if gameStarted == False:
        startgame()
    if gameStarted == True:
        score += 1
        PLATFORMINTERVAL += score
    
    if player.rect.y < SCREEN_HEIGHT // 2:
        gameStarted = True
    if player.rect.y > SCREEN_HEIGHT:
        GAME_ENDED = True

    screen.blit(panel, (0,SCREEN_HEIGHT-40))
    screen.blit(my_font.render(f'High: {str(highscore)}, Current: {score}', False, (0, 0, 0)), (5,SCREEN_HEIGHT - 22))
    if GAME_ENDED == True:
        apu += 1
        if endgame() == 'WIN':
            screen.blit(my_fontBIG.render(f'GAME OVER!!!', False, (0, 0, 0)), (60,SCREEN_HEIGHT//2 - 100))
            screen.blit(my_font.render(f'Congratulations!', False, (0, 0, 0)), (60 ,SCREEN_HEIGHT//2- 40))
            screen.blit(my_font.render(f'You beat the high score!!', False, (0, 0, 0)), (10 ,SCREEN_HEIGHT//2 - 10))
            screen.blit(my_font.render(f'Game will quit...', False, (0, 0, 0)), (80 ,SCREEN_HEIGHT//2 + 80))

        elif endgame() == 'LOOSE':
            screen.blit(my_fontBIG.render(f'GAME OVER!!!', False, (0, 0, 0)), (60,SCREEN_HEIGHT//2 - 100))
            screen.blit(my_font.render(f'Senkin lurjus!', False, (0, 0, 0)), (90 ,SCREEN_HEIGHT//2 - 40))
            screen.blit(my_font.render(f'Game will quit...', False, (0, 0, 0)), (80 ,SCREEN_HEIGHT//2 + 80))

        if apu > 1:
            pygame.time.delay(3000)
            running = False
            break
                    
    pygame.display.flip()
    clock.tick(TARGET_FPS)

pygame.quit()
sys.exit()
