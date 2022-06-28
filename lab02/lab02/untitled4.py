# -*- coding: utf-8 -*-
"""
Created on Wed Sep 29 18:42:11 2021

@author: Louis Martinez
"""
from lab import *
im = {'height': 4, 
      'width': 9, 
      'pixels': [200, 160, 160, 160, 153, 160, 160, 160, 200, 200, 160, 160, 160, 153, 160, 160, 160, 200, 0, 153, 160, 160, 160, 160, 160, 153, 0, 0, 153, 153, 160, 160, 160, 153, 153, 0]
      }

image = {
    'height': 6,
    'width': 5,
    'pixels': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]
    }

result = minimum_energy_seam(image)

energy_map = compute_energy(im)
g = [2, 11, 21, 31]
cumulative_energy = cumulative_energy_map(energy_map)
list_to_erase = minimum_energy_seam(cumulative_energy)
for i in range(len(list_to_erase)):
    if list_to_erase[i] != g[i]:
        print(False)
print(list_to_erase)
new_image = image_without_seam(image, list_to_erase)