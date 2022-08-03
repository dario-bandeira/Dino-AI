import os
import pygame
import random
from pygame import *
import pygame.freetype
import numpy as np

pygame.init()
gamefont = pygame.freetype.Font(None, 16)

scr_size = (width, height) = (1240, 720)
FPS = 60
gravity = 0.6

black = (0, 0, 0)
white = (255, 255, 255)
background_col = (235, 235, 235)

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


class Dino(pygame.sprite.Sprite):
	def __init__(self, sizex=-1, sizey=-1):
		pygame.sprite.Sprite.__init__(self, self.containers)
		self.images, self.rect = load_sprite_sheet('dino.png', 5, 1, sizex, sizey, -1)
		self.images1, self.rect1 = load_sprite_sheet('dino_ducking.png', 2, 1, 59, sizey, -1)
		self.rect.bottom = int(0.98 * height)
		self.rect.left = width / random.randint(10, 20)
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

		self.ai_syn1 = np.random.randint(-1000, 1000, (6, 6))
		self.ai_syn2 = np.random.randint(-1000, 1000, (6, 2))

	def draw(self):
		screen.blit(self.image, self.rect)

	def checkbounds(self):
		if self.rect.bottom > int(0.98 * height):
			self.rect.bottom = int(0.98 * height)
			self.isJumping = False

	def update(self, input):
		hidden = np.matmul(input, self.ai_syn1)
		for i, x in enumerate(hidden):
			if hidden[i] < 0:
				hidden[i] = 0

		output = np.matmul(hidden, self.ai_syn2)
		if output[0] > 0:
			if self.rect.bottom == int(0.98 * height):
				self.isJumping = True
				self.movement[1] = -1 * self.jumpSpeed

		if output[1] > 0:
			self.isDucking = True
			if self.movement[1] < 0:
				self.movement[1] = 0
			self.movement[1] += 4
		else:
			self.isDucking = False

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


def gameplay():
	global FPS
	gamespeed = 4
	gameover = False
	gamequit = False
	# playerdino = Dino(44, 47)
	# playerdino2 = Dino(44, 47)
	new_ground = Ground(-1 * gamespeed)
	counter = 0

	dinos = pygame.sprite.Group()
	cacti = pygame.sprite.Group()
	pteras = pygame.sprite.Group()
	clouds = pygame.sprite.Group()
	last_obstacle = pygame.sprite.Group()

	Dino.containers = dinos
	Cactus.containers = cacti
	Ptera.containers = pteras
	Cloud.containers = clouds

	for x in range(10):
		dinos.add(Dino(44, 47))

	temp_images, temp_rect = load_sprite_sheet('numbers.png', 12, 1, 11, int(11 * 6 / 5), -1)
	hi_image = pygame.Surface((22, int(11 * 6 / 5)))
	hi_rect = hi_image.get_rect()
	hi_image.fill(background_col)
	hi_image.blit(temp_images[10], temp_rect)
	temp_rect.left += temp_rect.width
	hi_image.blit(temp_images[11], temp_rect)
	hi_rect.top = height * 0.1
	hi_rect.left = width * 0.73

	# def jump():
	# 	if playerdino.rect.bottom == int(0.98 * height):
	# 		playerdino.isJumping = True
	# 		playerdino.movement[1] = -1 * playerdino.jumpSpeed
	#
	# def duck():
	# 	playerdino.isDucking = True
	# 	if playerdino.movement[1] < 0:
	# 		playerdino.movement[1] = 0
	# 	playerdino.movement[1] += 4

	while not gameover:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				gamequit = True
				gameover = True

			if event.type == pygame.KEYDOWN:
				# if event.key == pygame.K_SPACE:
				# 	jump()
				#
				# if event.key == pygame.K_DOWN:
				# 	duck()

				if event.key == pygame.K_EQUALS:
					FPS += 10
				if event.key == pygame.K_MINUS:
					FPS -= 10

			# if event.type == pygame.KEYUP:
			# 	if event.key == pygame.K_DOWN:
			# 		playerdino.isDucking = False

		# for c in cacti:
		# 	c.movement[0] = -1 * gamespeed
		# 	if pygame.sprite.collide_mask(playerdino, c):
		# 		playerdino.isDead = True
		#
		# for p in pteras:
		# 	p.movement[0] = -1 * gamespeed
		# 	if pygame.sprite.collide_mask(playerdino, p):
		# 		playerdino.isDead = True

		pygame.sprite.groupcollide(dinos, cacti, True, False)

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

		if pygame.display.get_surface() is not None:
			screen.fill(background_col)
			new_ground.draw()
			clouds.draw(screen)
			cacti.draw(screen)
			pteras.draw(screen)
			dinos.draw(screen)
			# playerdino.draw()
			# playerdino2.draw()

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

			# distancia = obstaculo_mais_proximo.rect[0] - playerdino.rect.left
			# do_chao = height - obstaculo_mais_proximo.rect[1] - obstaculo_mais_proximo.rect[2]
			# altura = obstaculo_mais_proximo.rect[3]
			# largura = obstaculo_mais_proximo.rect[2]
			# altura_dino = height - playerdino.rect[1] - playerdino.rect[2]
			#
			# distancia2 = obstaculo_mais_proximo.rect[0] - playerdino2.rect.left
			# do_chao2 = height - obstaculo_mais_proximo.rect[1] - obstaculo_mais_proximo.rect[2]
			# altura2 = obstaculo_mais_proximo.rect[3]
			# largura2 = obstaculo_mais_proximo.rect[2]
			# altura_dino2 = height - playerdino2.rect[1] - playerdino2.rect[2]
			#
			# gamefont.render_to(screen, (10, 10), "Distância: " + str(distancia), (0, 0, 0))
			# gamefont.render_to(screen, (10, 30), "Do chão: " + str(do_chao), (0, 0, 0))
			# gamefont.render_to(screen, (10, 50), "Altura: " + str(altura), (0, 0, 0))
			# gamefont.render_to(screen, (10, 70), "Largura: " + str(largura), (0, 0, 0))
			# gamefont.render_to(screen, (10, 100), "Velocidade: " + str(gamespeed), (0, 0, 0))
			# gamefont.render_to(screen, (10, 120), "Altura Dino: " + str(altura_dino), (0, 0, 0))
			# gamefont.render_to(screen, (10, 160), "FPS: " + str(FPS), (0, 0, 0))
			#
			# gamefont.render_to(screen, (200, 10), "Distância: " + str(distancia2), (0, 0, 0))
			# gamefont.render_to(screen, (200, 30), "Do chão: " + str(do_chao2), (0, 0, 0))
			# gamefont.render_to(screen, (200, 50), "Altura: " + str(altura), (0, 0, 0))
			# gamefont.render_to(screen, (200, 70), "Largura: " + str(largura), (0, 0, 0))
			# gamefont.render_to(screen, (200, 100), "Velocidade: " + str(gamespeed), (0, 0, 0))
			# gamefont.render_to(screen, (200, 120), "Altura Dino: " + str(altura_dino2), (0, 0, 0))
			# gamefont.render_to(screen, (200, 160), "FPS: " + str(FPS), (0, 0, 0))

			# testando
			ai_input = [1,1,1,1,1,1
				# distancia,
				# do_chao,
				# altura,
				# largura,
				# gamespeed,
				# altura_dino
			]

			# playerdino.update(ai_input)
			# playerdino2.update(ai_input)
			dinos.update(ai_input)
			cacti.update()
			pteras.update()
			clouds.update()
			new_ground.update()

			pygame.display.update()
		clock.tick(FPS)

		# if playerdino.isDead:
		# 	gameover = True

		if counter % 700 == 699 and gamespeed < 8:
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
