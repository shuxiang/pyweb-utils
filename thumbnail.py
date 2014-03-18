#! /usr/bin/env python
#coding=utf-8
"""
    Thumbnail
"""
import Image, ImageEnhance

def reduce_opacity(im, opacity):
    """Returns an image with reduced opacity."""
    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im

class Thumbnail(object):
    """
        t = Thumbnail(path)
        t.thumb(size=(100,100),outfile='file/to/name.xx',bg=False,watermark=None)
    """
    def __init__(self, path):
        self.path = path
        try:
            self.img = Image.open(self.path)
        except IOError:
            self.img = None
            print "%s not images" % path

    def thumb(self, size=(100,100), outfile=None, bg=False, watermark=None):
        """
            outfile: 'file/to/outfile.xxx'  
            crop: True|False
            watermark: 'file/to/watermark.xxx'
        """
        if not self.img:
            print 'must be have a image to process'
            return

        if not outfile:
            outfile = self.path

        #原图复制
        part = self.img
        part.thumbnail(size, Image.ANTIALIAS) # 按比例缩略
        
        size = size if bg else part.size # 如果没有白底则正常缩放
        w,h = size
        
        layer = Image.new('RGBA',size,(255,255,255)) # 白色底图

        # 计算粘贴的位置
        pw,ph = part.size
        left = (h-ph)/2
        upper = (w-pw)/2
        layer.paste(part,(upper,left)) # 粘贴原图

        # 如果有watermark参数则加水印, 只在width>=400 height>=300的图加水印
        if watermark and w > 400 and h > 300:
            logo = Image.open(watermark)
            logo = reduce_opacity(logo, 0.3)
            # 粘贴到右下角
            lw,lh = logo.size
            position = (w-lw,h-lh)
            if layer.mode != 'RGBA':
                layer = layer.convert('RGBA')
            mark = Image.new('RGBA', layer.size, (0,0,0,0))
            mark.paste(logo, position)
            layer = Image.composite(mark, layer, mark)

        layer.save(outfile, quality=100) # 保存
        return outfile

if __name__=='__main__':
    t = Thumbnail('1.jpg')
    t.thumb(size=(400,400),outfile='1_s1.jpg')
    t.thumb(size=(200,100),outfile='1_s2.jpg')
    t.thumb(size=(400,400),outfile='1_s3.jpg',watermark='logo.png')
