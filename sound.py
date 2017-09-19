import time
import pygame
pygame.mixer.init()
pygame.mixer.music.load("sounds/t1.mp3")
pygame.mixer.music.play()


i = 0
while pygame.mixer.music.get_busy() == True:
	time.sleep(1)
	i += 1
	print(str(i))
	continue