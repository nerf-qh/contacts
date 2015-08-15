'''
Created on 16 февр. 2014 г.

@author: shkalar

Copyright 2014 Aleh Krautsou
Licensed under the Apache License, Version 2.0
'''

from PIL import Image
max_size = 720

def resize(path):
    im = Image.open(path)
    if im.size[0] == im.size[1]:
        return
    min_size = min(max(im.size), max_size)
    k = min_size / max(im.size)
    im = im.resize((round(im.size[0]*k), round(im.size[1]*k)), Image.ANTIALIAS)
    im_new = Image.new('RGB', (min_size, min_size), 'black')
    im_new.paste(im, (int((min_size - im.size[0])/2), int((min_size - im.size[1])/2)))
    im_new.save(path)