import pyxel
import random
from pathlib import Path
import time

from character.poop import Poop
from character.human import Human
from direction import Direction



class App:
    # 화면 가로 세로
    WIDHT = 1280
    HEIGHT = 640
    
    # 박스 크기
    BOX_X = 32
    BOX_Y = 32
    
    # 아이템 및 똥 시간 주기
    POOP_TIME = 2
    ITEM_TIME = 30
    INTERRUPT_TIME = 15
    COOL_TIME = 0.5
    
    def __init__(self, ROOT):
        # 초기화
        pyxel.init(App.WIDHT, App.HEIGHT, title="똥피하기", fps=60)
        self.root = str(ROOT)
        
        # 객체 생성
        self.poop_list = []
        self.poop_cool_list = []
        self.human = Human(20,100)
        
        
        # 이미지
        pyxel.image(0).load(0, 0, f"{self.root}\\assets\\character.png")
        pyxel.image(1).load(0, 0, f"{self.root}\\assets\\items.png")
        # pyxel.image(2).load(0, 0, f"{self.root}\\assets\\item.png") # undying, darksight, hear
    
        # map
        pyxel.image(2).load(0,0,f"{self.root}\\assets\\map.png")
        
        # max height
        self.max_height = App.HEIGHT - 128
        
        # 시작 타임
        self.start_time = time.time()
        
        # For once draw
        self.is_two_time = False
        self.is_ab_time = False
        self.is_cool_time = False 
        
        pyxel.run(self.update, self.draw)

    def update(self):
        # 종료 조건
        if pyxel.btn(pyxel.KEY_ESCAPE) or self.human.life_count == 0:
            pyxel.quit()
        
        now = time.time()
        self.move_player()
        
        action_dt = int(now - self.start_time)
        
        ## POOP 관련
        # 똥 추가
        if not self.is_two_time and action_dt % App.POOP_TIME == 0: # 2초일 때 한 번 동작
            if action_dt != 0:
                print("?")
                self.drop_poop()
            self.is_two_time = True
        elif action_dt % App.POOP_TIME != 0:
            self.is_two_time = False 
            
        f_dt = round(now-self.start_time,1) # ex) 1.5
        # 쿨 제거
        if not self.is_cool_time and f_dt % App.COOL_TIME == 0: # 0.3초일 때 한 번 동작
            if self.poop_cool_list:
                del self.poop_cool_list[0]
            self.is_cool_time = True
        elif f_dt % App.COOL_TIME != 0:
            self.is_cool_time = False 

    
    def check_collisions(self, x, y):
        center_x,center_y = self.calc_pos(x,y)
        
        # 똥 리스트에서 해당 똥 있는지 확인
        for i in range(len(self.poop_list) - len(self.poop_cool_list)):
            if center_x == self.poop_list[i].x and center_y == self.poop_list[i].y:
                self.poop_list.remove(self.poop_list[i])
                self.human.life_count -= 1
                return True
        return False

    
    def is_hit_box(self):
        pass
    
    def move_player(self):
        prev_x = self.human.x
        prev_y = self.human.y
        
        # 뒤로 밀려나는것
        back_x = 0
        back_y = 0
        
        # Calc next step
        if pyxel.btn(pyxel.KEY_UP):
            prev_y = prev_y - Human.MOVE_DIST
            prev_y = prev_y if prev_y >= self.human.h//2 else 0
            back_y = +20
        elif pyxel.btn(pyxel.KEY_DOWN):
            prev_y = prev_y + Human.MOVE_DIST
            prev_y = prev_y if prev_y < self.max_height - self.human.h else self.max_height - self.human.h
            back_y = -20
        elif pyxel.btn(pyxel.KEY_LEFT):
            prev_x = prev_x - Human.MOVE_DIST
            prev_x = prev_x if prev_x >= self.human.w//2 else 0
            back_x = +20
        elif pyxel.btn(pyxel.KEY_RIGHT):
            prev_x = prev_x + Human.MOVE_DIST
            prev_x = prev_x if prev_x < App.WIDHT - self.human.w else App.WIDHT - self.human.w
            back_x = -20
            
        is_collision = self.check_collisions(prev_x, prev_y)

        if is_collision:
            self.human.x = prev_x + back_x
            self.human.y = prev_y + back_y
        else:
            self.human.x = prev_x
            self.human.y = prev_y 
    
    # 각 칸의 중심 좌표 계산
    def calc_pos(self, x, y):
        x = x // App.BOX_X
        y = y // App.BOX_Y
        x = x * App.BOX_X
        y = y * App.BOX_Y
        return x, y
    
    def drop_poop(self): 
        # 각 칸에 똥싸게 하기 위함, 좌표 // 32
        x, y = self.calc_pos(self.human.x, self.human.y)
        self.poop_list.append(Poop(x,y))
        # 쿨 타임 : 똥을 싸는 즉시 밟는 것을 막기 위함
        self.poop_cool_list.append(self.poop_list[0])
              
        

    def draw(self):
        pyxel.cls(0)
        # level 0
        # MAP
        for i in range(4):
            for j in range(5):
                pyxel.blt(256*j,128*i, 
                  2, 0, 0, 
                  256, 128)
        # status
        for i in range(5):
            pyxel.blt(256*i, 512, 
                  2, 0, 128, 
                  256, 128)
        
        # level 1
        # life
        self.human.life_draw()
    

        # Draw poop
        for p in self.poop_list:
            p.draw()
        self.human.draw()
            
        
        
        
        
   
if __name__ =="__main__":    
    FILE = Path(__file__).resolve()
    ROOT = FILE.parents[0]  # root directory
    App(ROOT)