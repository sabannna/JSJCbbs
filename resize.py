# coding: utf-8
import urllib.request, io
from PIL import Image

THUMB_SIZE = 120, 120
def cropimage(byteimg, originalname, secondname):

    imgfile = io.BytesIO(byteimg)
    img = Image.open(imgfile)
    img.save("./static/" + originalname)

    width, height = img.size

    if width > height:
        delta = width - height
        left = int(delta/2)
        upper = 0
        right = height + left
        lower = height
    else:
        delta = height - width
        left = 0
        upper = int(delta/2)
        right = width
        lower = width + upper

    img = img.crop((left, upper, right, lower))

    thumbnailed = img.copy()
    thumbnailed.thumbnail(THUMB_SIZE, getattr(Image, 'BILINEAR'))
    thumbnailed.save("./static/" + secondname)

    return True

