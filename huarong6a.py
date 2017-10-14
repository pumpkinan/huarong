#coding=utf-8
from __future__ import division, unicode_literals, print_function
import colorsys
import cairo

range = xrange
class Block(object):
    def __init__(self, name, height, width):
        self.height = height
        self.width = width
        self.name = name
        self.x = 0
        self.y = 0

    def copy(self):
        b = Block(self.name, self.height, self.width)
        b.x = self.x
        b.y = self.y
        return b
    
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

UP, DOWN, LEFT, RIGHT = (0, -1), (0, +1), (-1, 0), (+1, 0)

class HuarongStatus(object):
    def __init__(self, block_param):
        self.blocks = {}
        for n, w, h in block_param:
            self.blocks[n]=Block(n, height=h, width=w)
        self.pattern = None

    def set_pos(self, pos):
        for n, x, y in pos:
            self.blocks[n].x = x
            self.blocks[n].y = y
        self.updatePattern()

    def copy(self):
        c = HuarongStatus(PARAM)
        for n in PARAM:
            n0 = n[0]
            c.blocks[n0].x = self.blocks[n0].x
            c.blocks[n0].y = self.blocks[n0].y
        return c

    def draw(self,cr):
        cr.set_source_rgb(1,1,1)
        cr.rectangle(0.9, 0.9, 4.2, 5.2)
        cr.fill_preserve()
        cr.set_source_rgb(0,0,0)
        cr.stroke()
        for b in self.blocks.itervalues():
            b.draw(cr)
        

    def updatePattern(self):
        c = [[0 for i in range(7)] for j in range(6)]
        for i in range(6):
            c[i][0]=c[i][-1]=9
        for j in range(7):
            c[0][j]=c[-1][j]=9
        for b in self.blocks.itervalues():
            for x in range(b.x, b.x+b.width):
                for y in range(b.y, b.y+b.height):
                    c[x][y]=b.width*2 + b.height
        self.pattern = c
    
    def getPatternId(self):
        p = self.pattern
        s = [str(p[x][y]) for y in range(1,6) for x in range(1,5) ]
        return "".join(s)

    def getPatternMirrorId(self):
        p = self.pattern
        s = [str(p[5-x][y]) for y in range(1,6) for x in range(1,5) ]
        return "".join(s)

    def canMoveUp(self, n):
        b = self.blocks[n]
        cells = [ self.pattern[b.x + k][b.y-1] for k in range(b.width)]
        return sum(cells)==0
    
    def canMoveDown(self, n):
        b = self.blocks[n]
        cells = [ self.pattern[b.x + k][b.y+b.height] for k in range(b.width)]
        return sum(cells)==0

    def canMoveLeft(self, n):
        b = self.blocks[n]
        cells = [ self.pattern[b.x-1][b.y+k] for k in range(b.height)]
        return sum(cells)==0

    def canMoveRight(self, n):
        b = self.blocks[n]
        cells = [ self.pattern[b.x+b.width][b.y+k] for k in range(b.height)]
        return sum(cells)==0   

    def move(self, n, direction):
        dx, dy = direction
        self.blocks[n].x += dx
        self.blocks[n].y += dy
        self.updatePattern()

    def getNextStatus(self, n):
        nss = []
        for method, direction in [ ("canMoveDown", DOWN), 
                                    ("canMoveUp", UP),
                                    ("canMoveLeft", LEFT),
                                    ("canMoveRight", RIGHT)]:
            if getattr(self, method)(n):
                ns = self.copy()
                ns.move(n, direction)
                nss.append(ns)
        return nss
        
    def getAllNextStatus(self):
        all_nss = []
        for n, b in self.blocks.iteritems():
            nss = self.getNextStatus(n)
            if b.width==1 or b.height==1:
                another_step = []
                for s in nss:
                    another_step.extend( s.getNextStatus(n) )
                nss.extend(another_step)
            all_nss.extend(nss)
        return all_nss
    
    def is_done(self):
        cc = self.blocks["曹操"]
        return (cc.x==2) and (cc.y==4)
    
    def to_str(self):
        s = "\n"
        for y in range(1,6):
            for x in range(1,5):
                s+=str(self.pattern[x][y])
            s+="\n"
        return s

def showSolution(s, last_step_dict, pattern_status_dict):
    solution = []
    while True:
        solution.append(s)
        p = s.getPatternId()
        last_p = last_step_dict[p]
        if last_p==None:
            break
        else:
            s = pattern_status_dict[last_p]
    print( "Len=", len(solution) )
    
    WIDTH, HEIGHT = 180*9, 210*12
    ims = cairo.PDFSurface("solution.pdf", WIDTH, HEIGHT )    
    cr = cairo.Context(ims)
    cr.set_source_rgb(1, 1, 1)
    cr.rectangle(0, 0, WIDTH, HEIGHT)
    cr.fill()

    cr.select_font_face("微软雅黑", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    cr.set_font_size(0.4)
    cr.set_line_width(0.002)
    cr.scale(30, 30) # about 150*180
    cr.save()

    solution = solution[::-1]
    for i, s in enumerate(solution):
        ypos = .5 + 7 * int(i//8)
        xpos = .5 + 6 * (i % 8)
        cr.restore()
        cr.save()
        cr.translate ( xpos, ypos )
        cr.set_source_rgb(0, 0, 0)
        cr.move_to(2, 0.5)
        cr.show_text("Step: %d" % i)
        s.draw(cr)

    ims.show_page()

def getSolution(init_status):
    patterns_processed = set() 
    patterns_processed.add(init_status.getPatternId())
    patterns_processed.add(init_status.getPatternMirrorId())
    status_unprocessed = [ init_status ]
    status_processed = []
    last_step_dict = { init_status.getPatternId(): None}
    pattern_status_dict = {}
    while status_unprocessed:
        if len(status_processed)%1000==0:
            print("Visited: %d; Unvisited %d"%(len(status_processed), len(status_unprocessed)) )
        s = status_unprocessed.pop(0)
        pattern_status_dict[s.getPatternId()] = s
        status_processed.append(s)
        #print("pop S:", s.to_str())
        if s.is_done(): # solved?
            break
        nss = s.getAllNextStatus()
        #print("next Status:", len(nss))
        for k in nss:
            if (k.getPatternId() in patterns_processed) or (
                    k.getPatternMirrorId() in patterns_processed): ## visited
                pass
            else:
                status_unprocessed.append(k)
                patterns_processed.add(k.getPatternId())
                patterns_processed.add(k.getPatternMirrorId())
                last_step_dict[k.getPatternId()] = s.getPatternId()
    else:
        print("No Solution")
        return 
    
    # now s is last step of my solution
    showSolution(s, last_step_dict, pattern_status_dict)
    print("Done")

def test_solve():
    h = HuarongStatus(PARAM)
    h.set_pos(INIT_POS)
    getSolution(h)

if __name__ == "__main__":
    import cProfile
    cProfile.run("test_solve()", "result")
   
    import pstats
    #创建Stats对象
    p = pstats.Stats("result")
     
    #按照在一个函数中累积的运行时间进行排序
    #print_stats(3):只打印前3行函数的信息,参数还可为小数,表示前百分之几的函数信息
    p.strip_dirs().sort_stats("cumulative").print_stats(30)


    