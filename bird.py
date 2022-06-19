import pyxel
from direction import Direction

class Bird:
    MOVE_DIST = 2
    CORSS_MOVE_DIST = 2
    
    def __init__(self, level=0, speed=1):
        # 기본 이미지 설정
        self.img_num = 1
        self.img_x = 0
        self.img_y = 128
        self.w = 32
        self.h = 32
        
        self.x = 0
        self.y = 0
        
        self.level = level
        self.speed = speed
        
        self.rand_direction = pyxel.rndi(0,3)
        if self.rand_direction == Direction.UP.value:
            self.x = pyxel.rndi(0,39) * self.w
            self.y = 480
        elif self.rand_direction == Direction.DOWN.value:
            self.x = pyxel.rndi(0,39) * self.w
        elif self.rand_direction == Direction.RIGHT.value:
            self.y = pyxel.rndi(0,15) * self.h
        elif self.rand_direction == Direction.LEFT.value:
            self.y = pyxel.rndi(0,15) * self.h
            self.x = 1280
            
    def special_move(self, x, y):
        # human pos = x, y
        # 플레이어 기준
        if x > self.x and y > self.y: # 새가 좌측 위 = 우측 아래로 가야함
            self.x += Bird.CORSS_MOVE_DIST
            self.y += Bird.CORSS_MOVE_DIST
        elif x > self.x and y < self.y: # 새가 좌측 아래 = 우측 위로 가야함
            self.x += Bird.CORSS_MOVE_DIST
            self.y -= Bird.CORSS_MOVE_DIST
        elif x < self.x and y > self.y: # 새가 우측 위 = 좌측 아래로 가야함
            self.x -= Bird.CORSS_MOVE_DIST
            self.y += Bird.CORSS_MOVE_DIST
        elif x < self.x and y < self.y: # 새가 우측 아래 = 좌측 위로 가야함
            self.x -= Bird.CORSS_MOVE_DIST
            self.y -= Bird.CORSS_MOVE_DIST
        elif y == self.y:
            self.x += Bird.CORSS_MOVE_DIST if x > self.x else -Bird.CORSS_MOVE_DIST
        elif x == self.x:
            self.y += Bird.CORSS_MOVE_DIST if y > self.y else -Bird.CORSS_MOVE_DIST
            
        
        
            
    def draw(self):
        pyxel.blt(self.x, self.y + self.h, 
                  self.img_num, 32 * self.rand_direction, self.img_y, 
                  self.w, self.h)
        

        
    
        