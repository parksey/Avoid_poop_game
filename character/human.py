import pyxel
from pathlib import Path

from direction import Direction

class Human:
    FILE = Path(__file__).resolve()
    ROOT = FILE.parents[1]  # root directory
    
    MOVE_DIST = 2
    FULL_LIFE = 5
    
    def __init__(self, x, y):
        # 기본 이미지 설정
        self.img_num = 0
        self.img_x = 0
        self.img_y = 0
        
        self.x = x
        self.y = y
        self.w = 32
        self.h = 32
        
        # 게임 내 설정
        # 목숨
        self.life_count = 5
        
        
        
        
        
    def draw(self):
        pyxel.blt(self.x, self.y, 
                  self.img_num, self.img_x, self.img_y, 
                  self.w, self.h)
        
    def life_draw(self):
        # full = 64
        # empty = 96
        # Full heart
        x = 256*4
        for i in range(self.life_count):
            x += 32
            pyxel.blt(x, 520, 
                  1, 64, 0, 
                  self.w, self.h)
        
        # Empty heart
        for i in range(Human.FULL_LIFE-self.life_count):
            x += 32
            pyxel.blt(x, 520, 
                  1, 96, 0, 
                  self.w, self.h)
        
    
        