import time
import pygame
pygame.mixer.init()
<<<<<<< HEAD
pygame.mixer.music.load("sounds/t1.mp3")
pygame.mixer.music.play()

=======
pygame.mixer.music.load("sound/t1.mp3")
pygame.mixer.music.play()

print("wut")
>>>>>>> dev

i = 0
while pygame.mixer.music.get_busy() == True:
	time.sleep(1)
	i += 1
	print(str(i))
	continue