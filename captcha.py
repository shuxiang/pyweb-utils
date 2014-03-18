# -*- coding: utf-8 -*-
__all__ = ['captcha', 'captchacn']

try:
    import Image,ImageDraw,ImageFont
except ImportError:
    from PIL import Image,ImageDraw,ImageFont
from random import randint, choice
import math, string
from cStringIO import StringIO

_STR = '0123456789'#u'ABCDEFGHIJKLMNPQRSTUVWXYZ123456789'

class RandomChar():
  """用于随机生成汉字"""

  @staticmethod
  def Unicode():
    val = randint(0x4E00, 0x9FBF)
    return unichr(val)  

  @staticmethod
  def GB2312():
    head = randint(0xB0, 0xCF)
    body = randint(0xA, 0xF)
    tail = randint(0, 0xF)
    val = ( head << 8 ) | (body << 4) | tail
    str = "%x" % val
    return str.decode('hex').decode('gb2312')

  @staticmethod
  def English():
      return choice(_STR)

class ImageChar():
  def __init__(self, fontColor = (0, 0, 0),
                     size = (100, 30),
                     fontPath = './impact.ttf',
                     bgColor = (255, 255, 255),
                     fontSize = 24):
    self.size = size
    self.fontPath = fontPath
    self.bgColor = bgColor
    self.fontSize = fontSize
    self.fontColor = fontColor
    self.font = ImageFont.truetype(self.fontPath, self.fontSize)
    self.image = Image.new('RGB', size, bgColor)
    self.code = ''

  def rotate(self):
    self.image.rotate(randint(0, 30), expand=0)  

  def drawText(self, pos, txt, fill):
    draw = ImageDraw.Draw(self.image)
    draw.text(pos, txt, font=self.font, fill=fill)
    del draw  

  def randRGB(self):
    return (randint(0, 255),
           randint(0, 255),
           randint(0, 255))  

  def randPoint(self):
    (width, height) = self.size
    return (randint(0, width), randint(0, height))  

  def randLine(self, num):
    draw = ImageDraw.Draw(self.image)
    for i in range(0, num):
      draw.line([self.randPoint(), self.randPoint()], self.randRGB())
    del draw  

  def randChinese(self, num):
    gap = 3
    start = 0
    for i in range(0, num):
      char = RandomChar().GB2312()
      self.code += char
      x = start + self.fontSize * i + randint(0, gap) + gap * i
      self.drawText((x, randint(-5, 5)), char, self.randRGB())
      self.rotate()
    self.randLine(10)

  def randEnglish(self, num):
    gap = 3
    start = 0
    for i in range(0, num):
      char = RandomChar().English()
      self.code += char
      x = start + self.fontSize * i + randint(0, gap) + gap * i
      self.drawText((x, randint(-5, 5)), char, self.randRGB())
      self.rotate()
    self.randLine(10)

  def save(self, path):
    self.image.save(path)

def captcha(ext='png', fontPath='./impact.ttf'):
    ic = ImageChar(fontColor=(100,211, 90), fontPath=fontPath)
    ic.randEnglish(4)
    out = StringIO()
    ic.image.save(out, ext)
    return ic.code.lower(), out

def captchacn(ext='png', fontPath='./impact.ttf'):
    ic = ImageChar(fontColor=(100,211, 90), fontPath=fontPath)
    ic.randChinese(4)
    out = StringIO()
    ic.image.save(out, ext)
    return ic.code.lower(), out

if __name__=='__main__':
    # ic = ImageChar(fontColor=(100,211, 90))
    # ic.randChinese(2)
    # ic.save("./1.png")

    # ic = ImageChar(fontColor=(100,211, 90))
    # ic.randEnglish(4)
    # ic.save("./1.png")

    with open('./1.png', 'wb') as f:
        ic = captcha()
        print ic[0]
        f.write(ic[1].getvalue())

    with open('./2.png', 'wb') as f:
        ic = captchacn()#must use chinese font.ttf file like msyh.ttf
        print ic[0]
        f.write(ic[1].getvalue())
