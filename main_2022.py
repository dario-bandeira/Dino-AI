import os
import pygame
import random
from pygame import *
import pygame.freetype

pygame.init()
gamefont = pygame.freetype.Font(None, 16)

scr_size = (width, height) = (1240, 720)
FPS = 60
gravity = 0.6

black = (0, 0, 0)
white = (255, 255, 255)
background_col = (235, 235, 235)

high_score = 0

screen = pygame.display.set_mode(scr_size)
clock = pygame.time.Clock()
pygame.display.set_caption("T-Rex Rush")


def load_image(
		name,
		sizex=-1,
		sizey=-1,
		colorkey=None,
):
	fullname = os.path.join('sprites', name)
	image = pygame.image.load(fullname)
	image = image.convert()
	if colorkey is not None:
		if colorkey == -1:
			colorkey = image.get_at((0, 0))
		image.set_colorkey(colorkey, RLEACCEL)

	if sizex != -1 or sizey != -1:
		image = pygame.transform.scale(image, (sizex, sizey))

	return image, image.get_rect()


def load_sprite_sheet(
		sheetname,
		nx,
		ny,
		scalex=-1,
		scaley=-1,
		colorkey=None,
):
	fullname = os.path.join('sprites', sheetname)
	sheet = pygame.image.load(fullname)
	sheet = sheet.convert()

	sheet_rect = sheet.get_rect()

	sprites = []

	sizex = sheet_rect.width / nx
	sizey = sheet_rect.height / ny

	for i in range(0, ny):
		for j in range(0, nx):
			rect = pygame.Rect((j * sizex, i * sizey, sizex, sizey))
			image = pygame.Surface(rect.size)
			image = image.convert()
			image.blit(sheet, (0, 0), rect)

			if colorkey is not None:
				if colorkey == -1:
					colorkey = image.get_at((0, 0))
				image.set_colorkey(colorkey, RLEACCEL)

			if scalex != -1 or scaley != -1:
				image = pygame.transform.scale(image, (scalex, scaley))

			sprites.append(image)

	sprite_rect = sprites[0].get_rect()

	return sprites, sprite_rect


def extract_digits(number):
	if number > -1:
		digits = []
		# i = 0
		while number / 10 != 0:
			digits.append(number % 10)
			number = int(number / 10)

		digits.append(number % 10)
		for i in range(len(digits), 5):
			digits.append(0)
		digits.reverse()
		return digits


class Dino:
	def __init__(self, sizex=-1, sizey=-1):
		self.images, self.rect = load_sprite_sheet('dino.png', 5, 1, sizex, sizey, -1)
		self.images1, self.rect1 = load_sprite_sheet('dino_ducking.png', 2, 1, 59, sizey, -1)
		self.rect.bottom = int(0.98 * height)
		self.rect.left = width / 15
		self.image = self.images[0]
		self.index = 0
		self.counter = 0
		self.score = 0
		self.isJumping = False
		self.isDead = False
		self.isDucking = False
		self.isBlinking = False
		self.movement = [0, 0]
		self.jumpSpeed = 11.5

		self.stand_pos_width = self.rect.width
		self.duck_pos_width = self.rect1.width

	def draw(self):
		screen.blit(self.image, self.rect)

	def checkbounds(self):
		if self.rect.bottom > int(0.98 * height):
			self.rect.bottom = int(0.98 * height)
			self.isJumping = False

	def update(self):
		if self.isJumping:
			self.movement[1] = self.movement[1] + gravity

		if self.isJumping:
			self.index = 0
		elif self.isBlinking:
			if self.index == 0:
				if self.counter % 400 == 399:
					self.index = (self.index + 1) % 2
			else:
				if self.counter % 20 == 19:
					self.index = (self.index + 1) % 2

		elif self.isDucking:
			if self.counter % 5 == 0:
				self.index = (self.index + 1) % 2
		else:
			if self.counter % 5 == 0:
				self.index = (self.index + 1) % 2 + 2

		if self.isDead:
			self.index = 4

		if not self.isDucking:
			self.image = self.images[self.index]
			self.rect.width = self.stand_pos_width
		else:
			self.image = self.images1[self.index % 2]
			self.rect.width = self.duck_pos_width

		self.rect = self.rect.move(self.movement)
		self.checkbounds()

		if not self.isDead and self.counter % 7 == 6 and self.isBlinking is False:
			self.score += 1

		self.counter = (self.counter + 1)


class Cactus(pygame.sprite.Sprite):
	def __init__(self, speed=5, sizex=-1, sizey=-1):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.images, self.rect = load_sprite_sheet('cacti-small.png', 3, 1, sizex, sizey, -1)
		self.rect.bottom = int(0.98 * height)
		self.rect.left = width + self.rect.width
		self.image = self.images[random.randrange(0, 3)]
		self.movement = [-1 * speed, 0]

	def draw(self):
		screen.blit(self.image, self.rect)

	def update(self):
		self.rect = self.rect.move(self.movement)

		if self.rect.right < 0:
			self.kill()


class Ptera(pygame.sprite.Sprite):
	def __init__(self, speed=5, sizex=-1, sizey=-1):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.images, self.rect = load_sprite_sheet('ptera.png', 2, 1, sizex, sizey, -1)
		self.ptera_height = [height - 27, height - 38, height - 70]
		self.rect.centery = self.ptera_height[random.randrange(0, 3)]
		self.rect.left = width + self.rect.width
		self.image = self.images[0]
		self.movement = [-1 * speed, 0]
		self.index = 0
		self.counter = 0

	def draw(self):
		screen.blit(self.image, self.rect)

	def update(self):
		if self.counter % 10 == 0:
			self.index = (self.index + 1) % 2
		self.image = self.images[self.index]
		self.rect = self.rect.move(self.movement)
		self.counter = (self.counter + 1)
		if self.rect.right < 0:
			self.kill()


class Ground:
	def __init__(self, speed=-5):
		self.image, self.rect = load_image('ground.png', -1, -1, -1)
		self.image1, self.rect1 = load_image('ground.png', -1, -1, -1)
		self.rect.bottom = height
		self.rect1.bottom = height
		self.rect1.left = self.rect.right
		self.speed = speed

	def draw(self):
		screen.blit(self.image, self.rect)
		screen.blit(self.image1, self.rect1)

	def update(self):
		self.rect.left += self.speed
		self.rect1.left += self.speed

		if self.rect.right < 0:
			self.rect.left = self.rect1.right

		if self.rect1.right < 0:
			self.rect1.left = self.rect.right


class Cloud(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.image, self.rect = load_image('cloud.png', int(90 * 30 / 42), 30, -1)
		self.speed = 1
		self.rect.left = x
		self.rect.top = y
		self.movement = [-1 * self.speed, 0]

	def draw(self):
		screen.blit(self.image, self.rect)

	def update(self):
		self.rect = self.rect.move(self.movement)
		if self.rect.right < 0:
			self.kill()


class Scoreboard:
	def __init__(self, x=-1, y=-1):
		self.score = 0
		self.tempimages, self.temprect = load_sprite_sheet('numbers.png', 12, 1, 11, int(11 * 6 / 5), -1)
		self.image = pygame.Surface((55, int(11 * 6 / 5)))
		self.rect = self.image.get_rect()
		if x == -1:
			self.rect.left = width * 0.89
		else:
			self.rect.left = x
		if y == -1:
			self.rect.top = height * 0.1
		else:
			self.rect.top = y

	def draw(self):
		screen.blit(self.image, self.rect)

	def update(self, score):
		score_digits = extract_digits(score)
		self.image.fill(background_col)
		for s in score_digits:
			self.image.blit(self.tempimages[s], self.temprect)
			self.temprect.left += self.temprect.width
		self.temprect.left = 0


def introscreen():
	temp_dino = Dino(44, 47)
	temp_dino.isBlinking = True
	gamestart = False

	callout, callout_rect = load_image('call_out.png', 196, 45, -1)
	callout_rect.left = width * 0.05
	callout_rect.top = height * 0.4

	temp_ground, temp_ground_rect = load_sprite_sheet('ground.png', 15, 1, -1, -1, -1)
	temp_ground_rect.left = width / 20
	temp_ground_rect.bottom = height

	logo, logo_rect = load_image('logo.png', 240, 40, -1)
	logo_rect.centerx = width * 0.6
	logo_rect.centery = height * 0.6
	while not gamestart:
		if pygame.display.get_surface() is None:
			print("Couldn't load display surface")
			return True
		else:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					return True
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
						temp_dino.isJumping = True
						temp_dino.isBlinking = False
						temp_dino.movement[1] = -1 * temp_dino.jumpSpeed

		temp_dino.update()

		if pygame.display.get_surface() is not None:
			screen.fill(background_col)
			screen.blit(temp_ground[0], temp_ground_rect)
			if temp_dino.isBlinking:
				screen.blit(logo, logo_rect)
				screen.blit(callout, callout_rect)
			temp_dino.draw()

			pygame.display.update()

		clock.tick(FPS)
		if temp_dino.isJumping is False and temp_dino.isBlinking is False:
			gamestart = True


def gameplay():
	global high_score
	gamespeed = 4
	gameover = False
	gamequit = False
	playerdino = Dino(44, 47)
	new_ground = Ground(-1 * gamespeed)
	scb = Scoreboard()
	highsc = Scoreboard(width * 0.78)
	counter = 0

	cacti = pygame.sprite.Group()
	pteras = pygame.sprite.Group()
	clouds = pygame.sprite.Group()
	last_obstacle = pygame.sprite.Group()

	Cactus.containers = cacti
	Ptera.containers = pteras
	Cloud.containers = clouds

	temp_images, temp_rect = load_sprite_sheet('numbers.png', 12, 1, 11, int(11 * 6 / 5), -1)
	hi_image = pygame.Surface((22, int(11 * 6 / 5)))
	hi_rect = hi_image.get_rect()
	hi_image.fill(background_col)
	hi_image.blit(temp_images[10], temp_rect)
	temp_rect.left += temp_rect.width
	hi_image.blit(temp_images[11], temp_rect)
	hi_rect.top = height * 0.1
	hi_rect.left = width * 0.73

	while not gameover:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				gamequit = True
				gameover = True

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					if playerdino.rect.bottom == int(0.98 * height):
						playerdino.isJumping = True
						playerdino.movement[1] = -1 * playerdino.jumpSpeed

				if event.key == pygame.K_DOWN:
					if not (playerdino.isJumping and playerdino.isDead):
						playerdino.isDucking = True

			if event.type == pygame.KEYUP:
				if event.key == pygame.K_DOWN:
					playerdino.isDucking = False

		for c in cacti:
			c.movement[0] = -1 * gamespeed
			if pygame.sprite.collide_mask(playerdino, c):
				playerdino.isDead = True

		for p in pteras:
			p.movement[0] = -1 * gamespeed
			if pygame.sprite.collide_mask(playerdino, p):
				playerdino.isDead = True

		if len(cacti) < 2:
			if len(cacti) == 0:
				last_obstacle.empty()
				last_obstacle.add(Cactus(gamespeed, 40, 40))
			else:
				for l in last_obstacle:
					if l.rect.right < width * 0.7 and random.randrange(0, 50) == 10:
						last_obstacle.empty()
						last_obstacle.add(Cactus(gamespeed, 40, 40))

		if len(pteras) == 0 and random.randrange(0, 200) == 10 and counter > 500:
			for l in last_obstacle:
				if l.rect.right < width * 0.8:
					last_obstacle.empty()
					last_obstacle.add(Ptera(gamespeed, 46, 40))

		if len(clouds) < 5 and random.randrange(0, 300) == 10:
			Cloud(width, random.randrange(int(height / 5), int(height / 2)))

		playerdino.update()
		cacti.update()
		pteras.update()
		clouds.update()
		new_ground.update()
		scb.update(playerdino.score)
		highsc.update(high_score)

		if pygame.display.get_surface() is not None:
			screen.fill(background_col)
			new_ground.draw()
			clouds.draw(screen)
			scb.draw()
			if high_score != 0:
				highsc.draw()
				screen.blit(hi_image, hi_rect)
			cacti.draw(screen)
			pteras.draw(screen)
			playerdino.draw()

			# texto
			if not cacti and not pteras:
				gamefont.render_to(screen, (10, 10), "Distância: " + str(width), (0, 0, 0))
				gamefont.render_to(screen, (10, 30), "Altura: " + str(15), (0, 0, 0))
			elif cacti and not pteras:
				obstaculo_mais_proximo = cacti.sprites()[0]
			elif not cacti and pteras:
				obstaculo_mais_proximo = pteras.sprites()[0]
			else:
				if cacti.sprites()[0].rect[0] < pteras.sprites()[0].rect[0]:
					obstaculo_mais_proximo = cacti.sprites()[0]
				else:
					obstaculo_mais_proximo = pteras.sprites()[0]

			gamefont.render_to(screen, (10, 10), "Distância: " + str(obstaculo_mais_proximo.rect[0]), (0, 0, 0))
			gamefont.render_to(screen, (10, 30), "Do chão: " + str(height - obstaculo_mais_proximo.rect[1] - obstaculo_mais_proximo.rect[2]), (0, 0, 0))
			gamefont.render_to(screen, (10, 50), "Altura: " + str(obstaculo_mais_proximo.rect[3]), (0, 0, 0))
			gamefont.render_to(screen, (10, 70), "Largura: " + str(obstaculo_mais_proximo.rect[2]), (0, 0, 0))
			gamefont.render_to(screen, (10, 100), "Velocidade: " + str(gamespeed), (0, 0, 0))
			gamefont.render_to(screen, (10, 120), "Altura Dino: " + str(height - playerdino.rect[1] - playerdino.rect[2]), (0, 0, 0))

			pygame.display.update()
		clock.tick(FPS)

		if playerdino.isDead:
			gameover = True
			if playerdino.score > high_score:
				high_score = playerdino.score

		if counter % 700 == 699:
			new_ground.speed -= 1
			gamespeed += 1

		counter = (counter + 1)

		if gamequit:
			break

		if gameover:
			gameplay()

	pygame.quit()
	quit()


gameplay()
