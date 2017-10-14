#coding=utf-8
from __future__ import division, unicode_literals, print_function
import colorsys
import cairo
import copy

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

PARAM = [ 
    ("曹操",2,2),
    ("赵云",1,2),
    ("黄忠",1,2),
    ("马超",1,2),
    ("张飞",1,2),
    ("关羽",2,1),
    ("甲1",1,1),
    ("乙2",1,1),
    ("丙3",1,1),
    ("丁4",1,1)
]
    
INIT_POS = [
    ("曹操",2,1),
    ("赵云",1,1),
    ("黄忠",1,3),
    ("马超",4,1),
    ("张飞",4,3),
    ("关羽",2,3),
    ("甲1",1,5),
    ("乙2",2,4),
    ("丙3",3,4),
    ("丁4",4,5)
]

class HuarongStatus(object):
    def __init__(self, block_param):
        self.blocks = {}
        for n, w, h in block_param:
            self.blocks[n]=Block(n, height=h, width=w)

    def set_pos(self, pos):
        for n, x, y in pos:
            self.blocks[n].x = x
            self.blocks[n].y = y
    
    def draw(self,cr):
        for b in self.blocks.itervalues():
            b.draw(cr)

    def getPattern(self):
        c = [[0 for i in range(7)] for j in range(6)]
        for i in range(6):
            c[i][0]=c[i][-1]=9
        for j in range(7):
            c[0][j]=c[-1][j]=9
        for b in self.blocks.itervalues():
            for x in range(b.x, b.x+b.width):
                for y in range(b.y, b.y+b.height):
                    c[x][y]=b.width*2 + b.height
        return c

    def canMoveUp(self, n, pattern):
        b = self.blocks[n]
        cells = [ pattern[b.x + k][b.y-1] for k in range(b.width)]
        return sum(cells)==0
    
    def canMoveDown(self, n, pattern):
        b = self.blocks[n]
        print(b.height, b.width, b.x, b.y)
        cells = [ pattern[b.x + k][b.y+b.height] for k in range(b.width)]
        return sum(cells)==0

    def canMoveLeft(self, n, pattern):
        b = self.blocks[n]
        cells = [ pattern[b.x-1][b.y+k] for k in range(b.height)]
        return sum(cells)==0

    def canMoveRight(self, n, pattern):
        b = self.blocks[n]
        cells = [ pattern[b.x+b.width][b.y+k] for k in range(b.height)]
        return sum(cells)==0  

    def getNewStatus(self, n, move):
        ns = copy.deepcopy(self)
        if move=="UP":
            ns.blocks[n].y -= 1
        elif move=="DOWN":
            ns.blocks[n].y += 1
        elif move=="LEFT":
            ns.blocks[n].x -= 1
        elif move=="RIGHT":
            ns.blocks[n].x += 1
        else:
            assert "Error in parameter move"
        return ns
        
def prepare_cr():
    ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, 500, 600)    
    cr = cairo.Context(ims)
    cr.select_font_face("微软雅黑", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    cr.set_font_size(0.2)
    cr.set_line_width(0.01)
    cr.scale(100, 100)
    cr.translate (-.5, -.5)
    return cr, ims

def test_drawbox():
    cr, ims = prepare_cr()
    c = Block("曹操", 2, 2)
    c.x = 1
    c.y = 1
    c.draw(cr)
    ims.write_to_png("box.png")

def test_draw_status():
    cr, ims = prepare_cr()

    h = HuarongStatus(PARAM)
    h.set_pos(INIT_POS)
    
    h.draw(cr)
    ims.write_to_png("status.png")

def test_move_status():
    h = HuarongStatus(PARAM)
    h.set_pos(INIT_POS)
    c = h.getPattern()
    print(h.canMoveUp("曹操", c))
    print(h.canMoveDown("乙2", c))

def test_move_get_status():
    h = HuarongStatus(PARAM)
    h.set_pos(INIT_POS)
    ns = h.getNewStatus("甲1", "RIGHT")
    cr, ims = prepare_cr()

    p = ns.getPattern()
    print(p)
    assert ns.canMoveDown("黄忠", p)

    ns.draw(cr)
    ims.write_to_png("status_new.png")

if __name__ == "__main__":
    test_move_get_status()


    