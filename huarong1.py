#coding=utf-8
from __future__ import division, unicode_literals, print_function
import colorsys
import cairo

class Block(object):
    def __init__(self, name, height, width):
        self.height = height
        self.width = width
        self.name = name
        self.x = 0
        self.y = 0
    
    def draw(self, cr):
        m = hash(self.name)
        r,g,b = colorsys.hsv_to_rgb((m & 0xff)/0xff, 0.5, 1)
        cr.set_source_rgb(r,g,b)
        
        cr.rectangle(self.x + 0.05, self.y + 0.05, self.width-.1, self.height-.1 )
        cr.fill_preserve()
        
        cr.set_source_rgb(0,0,0)
        cr.stroke()
        
        xbearing, ybearing, width, height, xadvance, yadvance = cr.text_extents(self.name)
        cr.move_to(self.x + self.width/2.- xbearing - width/2., self.y + self.height/2. - ybearing - height/2., ) 
        cr.set_source_rgb(0,0,0)
        cr.show_text(self.name)
        cr.stroke()

def test_drawbox():
    ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, 500, 600)    
    cr = cairo.Context(ims)
    cr.select_font_face(u"微软雅黑", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    cr.set_font_size(0.2)
    cr.set_line_width(0.01)
    cr.scale(100, 100)
    cr.translate (-.5, -.5)

    c = Block("曹操", 2, 2)
    c.x = 1
    c.y = 1
    c.draw(cr)
    ims.write_to_png("box.png")

if __name__ == "__main__":
    test_drawbox()


    