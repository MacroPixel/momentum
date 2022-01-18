import pygame

pygame.init()

clock = pygame.time.Clock()
i = 0
total_time = 0

while total_time < 1000:
  i += 1
  total_time += clock.tick()

print( i )