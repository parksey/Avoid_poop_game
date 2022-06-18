import pyxel
from pathlib import Path

class Poop:
    FILE = Path(__file__).resolve()
    ROOT = FILE.parents[1]  # root directory
    
    def __init__(self, x, y):
        # 기본 이미지 설정
        self.img_num = 0
        self.img_x = 32
        self.img_y = 0
        
        self.x = x
        self.y = y
        self.w = 32
        self.h = 32
        
        
    def draw(self):
        
        pyxel.blt(self.x, self.y + self.h, 
                  self.img_num, self.img_x, self.img_y, 
                  self.w, self.h)
        