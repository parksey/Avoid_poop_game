import pyxel

class Item:
    def __init__(self):
        # 기본 이미지 설정
        self.img_x = 0
        self.img_y = 0
        
        self.w = 32
        self.h = 32
        
        # 0: Undying, 1: Ghost, 2: Heart
        self.item_type = pyxel.rndi(0,2)
        self.img_num = 1
        
        # 랜덤 위치 생성
        self.x = pyxel.rndi(0,39) * self.w
        self.y = pyxel.rndi(0,15) * self.h
        pass
    
    def draw(self):
        if self.item_type == 0:
            self.draw_undying()
        elif self.item_type == 1:
            self.draw_ghost()
        else:
            self.draw_heart()
    
    def draw_undying(self):
        pyxel.blt(self.x, self.y + self.h, 
                  self.img_num, self.img_x, self.img_y, 
                  self.w, self.h)
    
    def draw_ghost(self):
        pyxel.blt(self.x, self.y + self.h, 
                  self.img_num, self.img_x+32, self.img_y, 
                  self.w, self.h)

    def draw_heart(self):
        pyxel.blt(self.x, self.y + self.h, 
                  self.img_num, self.img_x+64, self.img_y, 
                  self.w, self.h)
        
    def draw_status(x, y, target):
        if target == "ghost":
            pyxel.blt(x, y + 32, 
                  1, 32, 0, 
                  32, 32)
        elif target == "undying":
            pyxel.blt(x, y + 32, 
                  1, 0, 0, 
                  32, 32)