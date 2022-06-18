import pyxel

class Item:
    def __init__(self):
        # 기본 이미지 설정
        self.item = pyxel.rndi(2,5)
        self.img_num = self.item
        self.img_x = 0
        self.img_y = 0
        
        self.w = 32
        self.h = 32
        
        
        
        self.x = pyxel.rndi(0,39)
        self.y = pyxel.rndi(0,19)
        pass
    
    def get_life(self):
        return 1
    
    