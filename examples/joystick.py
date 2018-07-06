import pygame.joystick as j

j.init()
count = j.get_count()
print("Number of joysticks: {}".format(count))
