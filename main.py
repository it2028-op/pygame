# import knihoven random a pygame a souboru button
import pygame
from pygame import mixer
import random
import button
#
pygame.init()

# nastavení času a fps spolu s oknem hry

clock = pygame.time.Clock()
fps = 60

bottom_pan = 150
screen_width = 800
screen_height = 400 + bottom_pan

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Knights and bandits')

# nastavení basic proměnných, které ovlivňují základ hry a které se budou měnit jen vzácně
current_fighter = 1
act_cooldown = 0
act_wait_time = 90
attack = False
potion = False
heal = 15
target = False
marked = False
game_over = 0
speed = False
level = 1

# definice grafických proměnných pro text

font = pygame.font.SysFont('Times New Roman', 26)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (112, 207, 225)
yellow = (232, 229, 49)

# načtení zvukových efektů do proměnných a spuštění hudby na pozadí

mixer.music.load('sound/bg_music.wav')
pygame.mixer.music.set_volume(0.1)
mixer.music.play(-1)
hurt_sound = mixer.Sound('sound/hurt.wav')
death1_sound = mixer.Sound('sound/death1.wav')
death2_sound = mixer.Sound('sound/death2.wav')

# načtení obrázků

bg_img = pygame.image.load('graphics/bg.png').convert_alpha()
pan_img = pygame.image.load('graphics/stone_floor.png').convert_alpha()
pt_img = pygame.image.load('graphics/ico/hp_potion.png').convert_alpha()
str_pt_img = pygame.image.load('graphics/ico/str_potion.png').convert_alpha()
speed_pt_img = pygame.image.load('graphics/ico/speed_pt.png').convert_alpha()
rst_png = pygame.image.load('graphics/replay.png').convert_alpha()
next_png = pygame.image.load('graphics/next.png').convert_alpha()
vict_img = pygame.image.load('graphics/victory.png').convert_alpha()
def_img = pygame.image.load('graphics/defeat.png').convert_alpha()
mouse_img = pygame.image.load('graphics/ico/sword.png').convert_alpha()

# textové funkce

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def draw_bg():
    screen.blit(bg_img, (0,0))

def draw_pan():
    screen.blit(pan_img, (0, screen_height - bottom_pan))
    draw_text(f'{hero.name} HP: {hero.hp}', font, red, 100, screen_height - bottom_pan + 10)
    for count, i  in enumerate(bandit_list):
        draw_text(f'{i.name} HP: {i.hp}', font, red, 550, (screen_height - bottom_pan +1) + count * 40)


class Fighter():
    def __init__(self, x, y, name, max_hp, strenght, potions, strenght_potion):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strenght = strenght
        self.org_str = strenght
        self.start_potios = potions
        self.potions = potions
        self.str_potion = strenght_potion
        self.speed_pt = 0
        self.alive = True
        self.anim_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.score = 0

        # načítání jednotlivých galerií obrázků pro animaci do temp_list, z kterého se hodnoty převádí do anim_list a následně se čistí

        temp_list = []
        for i in range(8):
            img = pygame.image.load(f'graphics/{self.name}/Idle/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.anim_list.append(temp_list)

        temp_list = []
        for i in range(7):
            img = pygame.image.load(f'graphics/{self.name}/Attack/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.anim_list.append(temp_list)

        temp_list = []
        for i in range(3):
            img = pygame.image.load(f'graphics/{self.name}/Hurt/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.anim_list.append(temp_list)

        temp_list = []
        for i in range(10):
            img = pygame.image.load(f'graphics/{self.name}/Death/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.anim_list.append(temp_list)

        temp_list = []
        for i in range(7):
            img = pygame.image.load(f'graphics/{self.name}/Run/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.anim_list.append(temp_list)

        self.image = self.anim_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    # updatovací funkce, která po určitém čase ukončí přehrávání animací a nastaví postoj na idle
    def update(self):
        anim_cooldown = 100
        self.image = self.anim_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > anim_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        if self.frame_index >= len(self.anim_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.anim_list[self.action]) -1
            else:
                self.idle()
    # jednotlivé funkce prováděné během animací
    # základní klidová animace
    def idle(self):
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def attack(self, target):
        # na základě síly a prvku náhody se získá velikost poškození, která se následně odečte od životů cíle
        prob = self.org_str/2
        rand = random.randint(-prob, prob)
        pt = random.randint(0,10)
        dmg = self.strenght + rand
        target.hp -= dmg
        target.hurt()
        # pokud životy cíle klesnou pod nulu, nastaví se na nulu a je označen jako mrtví
        if target.hp < 1:
            target.hp = 0
            target.alive = False
            target.death()
            # útočník může získat jeden z lektvarů n aprincipu nahodilosti
            if pt == 0:
                self.potions += 1
            if (pt == 1) or (pt == 2):
                self.str_potion += 1
            if pt in range(3,6):
                self.speed_pt += 1
            if self.name == 'Hero':
                self.score += 50
            print(pt)
        # zobrazení poškození, nastavení animace na útok a vrácení síly do původních hodnot, pokud byla zvýšena lektvarem
        dmg_txt = DmgText(target.rect.centerx, target.rect.y, str(dmg), red)
        dmg_text.add(dmg_txt)
        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        if self.strenght > self.org_str:
            self.strenght = self.org_str

    def hurt(self):
        self.action = 2
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        mixer.Sound.play(hurt_sound)

    def death(self):
        mixer.Sound.play(death1_sound)
        self.action = 3
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        mixer.Sound.play(death2_sound)
    # vrátí vše ve vstupní proměnné do původního stavu
    def reset(self):
        self.alive = True
        self.potions = self.start_potios
        self.str_potion = 0
        self.speed_pt = 0
        self.hp = self.max_hp
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.score = 0

    def draw(self):
        screen.blit(self.image, self.rect)
# nastavení červeného pruhu vespod a zeleného nahoře, který se postupně zkracuje
class HealthBar():
    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp

    def draw(self, hp):
        self.hp = hp
        ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, red, (self.x, self.y, 150, 10))
        pygame.draw.rect(screen, green, (self.x, self.y, 150 * ratio, 10))
# animace a zobrazení velikosti poškození a následné odplynutí
class DmgText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, colour):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, colour)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        self.rect.y -= 1
        self.counter += 1
        if self.counter > 30:
            self.kill()

dmg_text = pygame.sprite.Group()

# vytvoření hrajících proměnných a tlačítek podle formátu Button ze souboru button
hero = Fighter(200, 260, 'Hero', 50, 10, 3, 0)
bandit1 = Fighter(550, 270, 'Bandit', 5 + 5*level, 3 + 3*level, 1, 0)
bandit2 = Fighter(625, 270, 'Bandit', 5 + 5*level, 3 + 3*level, 1, 0)
bandit3 = Fighter(700, 270, 'Bandit', 5 + 5*level, 3 + 3*level, 1, 0)
hero_hb = HealthBar(100, screen_height - bottom_pan + 40, hero.hp, hero.max_hp)

bandit_list = []
bandit_hbs = []

bandit_list.append(bandit1)
bandit_list.append(bandit2)
bandit_list.append(bandit3)

bandit1_hb = HealthBar(550, screen_height - bottom_pan + 30, bandit1.hp, bandit1.max_hp)
bandit2_hb = HealthBar(550, screen_height - bottom_pan + 70, bandit2.hp, bandit2.max_hp)
bandit3_hb = HealthBar(550, screen_height - bottom_pan + 110, bandit2.hp, bandit2.max_hp)

pt_button = button.Button(screen, 80, screen_height - bottom_pan + 70, pt_img, 64, 64)
str_button = button.Button(screen, 144, screen_height - bottom_pan + 70, str_pt_img, 64, 60)
speed_button = button.Button(screen, 210, screen_height - bottom_pan + 68, speed_pt_img, 60, 60)
rst_button = button.Button(screen, 250, 120, rst_png, 120, 30)
next_button = button.Button(screen, 390, 120, next_png, 120, 30)

# hra běží, dokud se nezmění hodnota game_over

run = True
while run:


    clock.tick(fps)

    draw_bg()
    draw_pan()

    hero_hb.draw(hero.hp)
    bandit1_hb.draw(bandit1.hp)
    bandit2_hb.draw(bandit2.hp)
    bandit3_hb.draw(bandit3.hp)

    hero.update()
    hero.draw()
    for bandit in bandit_list:
        bandit.update()
        bandit.draw()

    dmg_text.update()
    dmg_text.draw(screen)
    # vynulování a výchozí stav akcí
    attack = False
    potion = False
    str_potion = False
    speed_pt = False
    target = None
    # změna vzhledu kurzoru po setkání s pozicí bandity
    pygame.mouse.set_visible(True)
    pos = pygame.mouse.get_pos()
    for count, bandit in enumerate(bandit_list):
        if bandit.rect.collidepoint(pos) and bandit.alive:
            pygame.mouse.set_visible(False)
            screen.blit(mouse_img, pos)
            if marked:
                attack = True
                target = bandit_list[count]

    if pt_button.draw():
        potion = True

    if str_button.draw():
        str_potion = True

    if speed_button.draw():
        speed_pt = True

    draw_text(str(hero.potions), font, red, 130, screen_height - bottom_pan + 70)
    draw_text(str(hero.str_potion), font, blue, 196, screen_height - bottom_pan + 70)
    draw_text(str(hero.speed_pt), font, yellow, 265, screen_height - bottom_pan + 70)
    # zjišťování jestli hra ještě pokračuje a co který Fighter dělá za akci
    if game_over == 0:
        if hero.alive:
            if current_fighter == 1:
                act_cooldown += 1
                if act_cooldown >= act_wait_time:
                    if attack == True and target != None:
                        hero.attack(target)
                        if speed:
                            act_cooldown = 0
                            speed = False
                        else:
                            current_fighter += 1
                            act_cooldown = 0
                    if potion:
                        if hero.potions > 0:
                            if hero.max_hp - hero.hp > heal:
                                heal_amount = heal
                            else:
                                heal_amount = hero.max_hp - hero.hp
                            hero.hp += heal_amount
                            hero.potions -= 1
                            dmg_txt = DmgText(hero.rect.centerx, hero.rect.y, str(heal_amount), green)
                            dmg_text.add(dmg_txt)
                            current_fighter += 1
                            act_cooldown = 0
                    if str_potion:
                        if hero.str_potion > 0:
                            hero.strenght = hero.strenght * 2
                            hero.str_potion -= 1
                            print(hero.name, hero.strenght, hero.str_potion)
                    if speed_pt:
                        if hero.speed_pt > 0:
                            speed = True
                            hero.speed_pt -= 1

        else:
            game_over = -1

        for count, bandit in enumerate(bandit_list):
            if current_fighter == 2 + count:
                if bandit.alive:
                    act_cooldown += 1
                    if act_cooldown >= act_wait_time:
                        if (bandit.max_hp/ bandit.hp >= 2) and bandit.potions > 0:
                            if bandit.max_hp - bandit.hp > heal:
                                heal_amount = heal
                            else:
                                heal_amount = bandit.max_hp - bandit.hp
                            bandit.hp += heal_amount
                            bandit.potions -= 1
                            dmg_txt = DmgText(bandit.rect.centerx, bandit.rect.y, str(heal_amount), green)
                            dmg_text.add(dmg_txt)
                            current_fighter += 1
                            act_cooldown = 0
                        else:
                            bandit.attack(hero)
                            current_fighter += 1
                            act_cooldown = 0
                else:
                    current_fighter += 1

        if current_fighter > (len(bandit_list) + 1):
            current_fighter = 1
            print(hero.name, hero.strenght, hero.str_potion, level, hero.score)

    # zjišťování počtu živých banditů
    alive_bandits = 0
    for bandit in bandit_list:
        if bandit.alive:
            alive_bandits += 1
    if alive_bandits == 0:
        game_over = 1
    # pokud se změní hodnota game_over, zjišťuje se kdo vyhrál
    if game_over != 0:
        if game_over == 1:
            screen.blit(vict_img, (250, 50))
            hero.score += 100
        else:
            screen.blit(def_img, (250, 50))
        # restart všeho
        if rst_button.draw():
            hero.reset()
            for bandit in bandit_list:
                bandit.reset()
            current_fighter = 1
            act_cooldown
            game_over = 0
        # pokud hrdina vyhrál, může obnovit bandity, ale sebe nemusí
        if game_over == 1:
            if next_button.draw():
                hero.potions += 1
                for bandit in bandit_list:
                    bandit.reset()
                current_fighter = 1
                act_cooldown
                game_over = 0
                level += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            marked = True
        else:
            marked = False

    pygame.display.update()

pygame.quit()
