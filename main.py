import pyxel
import random
from pathlib import Path
import time
import enum

from character.poop import Poop
from character.human import Human
from item import Item
from direction import Direction

class App:
    # 화면 가로 세로
    WIDHT = 1280
    HEIGHT = 672
    
    # 박스 크기
    BOX_X = 32
    BOX_Y = 32
    
    # 아이템 및 똥 시간 주기
    POOP_TIME = 2
    COOL_TIME = 0.5
    SB_AB_TIME = 20 # 100초지만 20초마다 확인
    ITEM_TIME = 30
    INTERRUPT_TIME = 15
    
    UNDYING_TIME = 10 # 불사 : 10초
    GHOST_TIME = 10 # 투명 : 10초
    
    # 똥 제거 점수
    REMOVE_SCORE = 100
    
    
    def __init__(self, ROOT):
        # 초기화
        pyxel.init(App.WIDHT, App.HEIGHT, title="똥피하기", fps=60)
        pyxel.mouse(True)
        self.root = str(ROOT)
        
        # 객체 생성
        self.poop_list = []
        self.poop_cool_list = []
        
        rand_x, rand_y = self.get_rand_pos()
        self.human = Human(rand_x, rand_y)
        
        self.gauge_box_x = 256*3 - 100
        self.gauge_box_y = 520 + App.BOX_Y
        
        # 이미지
        pyxel.image(0).load(0, 0, f"{self.root}\\assets\\character.png")
        pyxel.image(1).load(0, 0, f"{self.root}\\assets\\items.png")
    
        # map
        pyxel.image(2).load(0,0,f"{self.root}\\assets\\map.png")
        
        # 시작 화면
        self.user_name=[]
        
        self.is_press_enter = False
        self.is_start= False
        self.is_game_over = False
        
        self.alphabet_dict ={
            "a": [0,0],
            "b": [0,1],
            "c": [0,2],
            "d": [0,3],
            "e": [0,4],
            "f": [0,5],
            "g": [0,6],
            "h": [0,7],
            "i": [0,8],
            "j": [0,9],
            "k": [0,10],
            "l": [0,11],
            "m": [0,12],
            "n": [1,0],
            "o": [1,1],
            "p": [1,2],
            "q": [1,3],
            "r": [1,4],
            "s": [1,5],
            "t": [1,6],
            "u": [1,7],
            "v": [1,8],
            "w": [1,9],
            "x": [1,10],
            "y": [1,11],
            "z": [1,12],
        }
        
        # max height
        self.max_height = App.HEIGHT - 128
        
        # 시작 타임
        self.start_time = time.time()
        
        # For once draw
        self.is_two_time = False
        self.is_ab_time = False
        self.is_cool_time = False 
        self.is_item_time = False
        
        # 능력 게이지
        self.sb_gauge = 0
        self.AB_FULL_GAUGE = 5 # 0~5  : 0, 20, 40, 60, 80, 100

        # Item list
        self.item_list = []

        # use item
        self.is_ghost = False
        self.ghost_start_time = 0
        
        self.is_undying = False
        self.undying_start_time = 0
        
        # Score
        self.total_score = 0
        
        pyxel.run(self.update, self.draw)

    def get_rand_pos(self):
        return pyxel.rndi(0, 39) * App.BOX_X, pyxel.rndi(0, 15) * App.BOX_Y

    def update(self):
        # 종료 조건
        if pyxel.btn(pyxel.KEY_ESCAPE):
            pyxel.quit()
            
        if self.human.life_count == 0:
            self.is_game_over = True
        
        if not self.is_start or self.is_game_over:
            return
        
        now = time.time()
        self.move_player()
        
        # 기본 동작 제어 시간
        action_dt = int(now - self.start_time)
        
        # Item 제어 시간
        ghost_dt = 0
        undying_dt = 0
        # Ghost
        if self.is_ghost:
            ghost_dt = int(now - self.ghost_start_time)
        
        # Undying
        if self.is_undying:
            undying_dt = int(now - self.undying_start_time)
        
        if ghost_dt == App.GHOST_TIME:
            self.is_ghost = False
        if undying_dt == App.UNDYING_TIME:
            self.is_undying = False
        
        ## POOP 관련
        # 똥 추가
        if not self.is_two_time and action_dt % App.POOP_TIME == 0: # 2초일 때 한 번 동작
            if action_dt != 0:
                # Score 올림
                self.total_score += 2
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

        # Ability
        if not self.is_ab_time and action_dt % App.SB_AB_TIME == 0: # 20초일 때 한 번 동작
            if action_dt != 0 and self.sb_gauge < self.AB_FULL_GAUGE: # 100초 이전
                self.sb_gauge+=1
            self.is_ab_time = True
        elif action_dt % App.SB_AB_TIME != 0:
            self.is_ab_time = False 
            
        # Use Ability
        if self.sb_gauge == self.AB_FULL_GAUGE:
            if pyxel.btn(pyxel.KEY_SPACE):
                self.use_ability()
                self.sb_gauge = 0
            elif pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                if self.is_hit_box("gauge", (self.gauge_box_x, self.gauge_box_y), (pyxel.mouse_x, pyxel.mouse_y)):
                    self.use_ability()
                    self.sb_gauge = 0
                
        # Random Item
        if not self.is_item_time and action_dt % App.ITEM_TIME == 0: # 30초일 때 한 번 동작
            if action_dt != 0:
                self.drop_item()
            self.is_item_time = True
        elif action_dt % App.ITEM_TIME != 0:
            self.is_item_time = False     
        
    
    def drop_item(self): 
        self.item_list.append(Item())
        
        
       
    def use_ability(self):
        # Update score
        self.total_score += 5000
        
        # Delete all obst
        # Poop
        self.poop_list.clear()
        self.poop_cool_list.clear()
    
    def check_collisions(self, x, y):
        center_x,center_y = self.calc_pos(x,y)
        # 똥 리스트에서 해당 똥 있는지 확인
        for i in range(len(self.poop_list) - len(self.poop_cool_list)):
            # if center_x == self.poop_list[i].x and center_y == self.poop_list[i].y: # 중심 좌표로 판별

            if self.is_hit_box("poop", (self.poop_list[i].x, self.poop_list[i].y), (x,y)): # 거리에 따른 히트박스 판별
                # 유령 : 통과
                # 불사 : 제거 계속
                
                if self.is_undying:
                    self.total_score += App.REMOVE_SCORE
                    self.poop_list.remove(self.poop_list[i])
                    break
                if self.is_ghost:
                    break
                
                self.poop_list.remove(self.poop_list[i])
                self.human.life_count -= 1
                return True
            
        # 아이템 확인
        for item in self.item_list:
            if self.is_hit_box("item", (item.x, item.y), (x,y)): # 거리에 따른 히트박스 판별
                if item.item_type == 2: # heart
                    if self.human.life_count != self.human.max_life:
                        self.human.life_count += 1
                elif item.item_type == 1: # ghost
                    self.is_ghost = True
                    self.ghost_start_time = time.time()
                elif item.item_type == 0:
                    self.is_undying = True
                    self.undying_start_time = time.time()
                self.item_list.remove(item)
                return False
            
        return False

    
    def is_hit_box(self, target, target_pos, curr_pos):
        if target == "gauge":
            tolerance = 10
            max_x = target_pos[0] + self.BOX_X
            max_y = target_pos[1] + self.BOX_Y
            if curr_pos[0] >= target_pos[0] - tolerance and curr_pos[0] <= max_x + tolerance \
                and curr_pos[1] >= target_pos[1] - tolerance and curr_pos[1] <= max_y + tolerance:
                    return True
            
        elif target == "poop":
            tolerance = 0.9
            dx = target_pos[0] - curr_pos[0]
            dy = target_pos[1] - curr_pos[1]
            r = App.BOX_X//2
            if dx*dx + dy*dy < r*r * tolerance:
                    return True
                
        elif target == "item":
            tolerance = 1
            dx = target_pos[0] - curr_pos[0]
            dy = target_pos[1] - curr_pos[1]
            r = App.BOX_X//2
            if dx*dx + dy*dy < r*r * tolerance:
                    return True
        
        return False

    
    def move_player(self):
        prev_x = self.human.x
        prev_y = self.human.y
        
        # 뒤로 밀려나는것
        back_x = 0
        back_y = 0

        # Calc next step
        if pyxel.btn(pyxel.KEY_UP):
            prev_y = prev_y - Human.MOVE_DIST
            prev_y = prev_y if prev_y >= 0 else 0
            back_y = +20
        elif pyxel.btn(pyxel.KEY_DOWN):
            prev_y = prev_y + Human.MOVE_DIST
            prev_y = prev_y if prev_y < self.max_height - self.human.h - App.BOX_Y else self.max_height - self.human.h - App.BOX_Y
            back_y = -20
        elif pyxel.btn(pyxel.KEY_LEFT):
            prev_x = prev_x - Human.MOVE_DIST
            prev_x = prev_x if prev_x >= 0 else 0
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
              
        
    def ability_bar_draw(self):
        # Draw guage
        for i in range(self.sb_gauge+1):
            pyxel.blt(self.gauge_box_x, self.gauge_box_y, 
                    1, i*32, 32, 
                    32, 32)
        
        # Draw ability Skill
        if self.sb_gauge ==self.AB_FULL_GAUGE:
            pyxel.blt(256*3, 520 + App.BOX_Y, 
                    1, 128, 0, 
                    32, 32)
        else:
            pyxel.blt(256*3, 520 + App.BOX_Y, 
                    1, 160, 0, 
                    32, 32)

    def draw_score(self):
        x = 256
        y = 520
        
        # SCORE
        pyxel.blt(0, 0, 
                    1, 160, 64, 
                    47, 32)
        # Number
        x = 48
        num_string = str(self.total_score)
        for num in num_string:
            pyxel.blt(x, 0, 
                    1, 16 * int(num), 64, 
                    16, 32)
            x += 16
        
    def show_press_menu(self):
        # “Press “Enter” to start the game”
        start_x = 400
        start_y = 300
               
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["p"][1] * 16, 96 + self.alphabet_dict["p"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["r"][1] * 16, 96 + self.alphabet_dict["r"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["e"][1] * 16, 96 + self.alphabet_dict["e"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["s"][1] * 16, 96 + self.alphabet_dict["s"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["s"][1] * 16, 96 + self.alphabet_dict["s"][0] * 16, 16, 16)
        start_x+=32
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["e"][1] * 16, 96 + self.alphabet_dict["e"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["n"][1] * 16, 96 + self.alphabet_dict["n"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["t"][1] * 16, 96 + self.alphabet_dict["t"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["e"][1] * 16, 96 + self.alphabet_dict["e"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["r"][1] * 16, 96 + self.alphabet_dict["r"][0] * 16, 16, 16)
        start_x+=32
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["t"][1] * 16, 96 + self.alphabet_dict["t"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["o"][1] * 16, 96 + self.alphabet_dict["o"][0] * 16, 16, 16)
        start_x+=32
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["s"][1] * 16, 96 + self.alphabet_dict["s"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["t"][1] * 16, 96 + self.alphabet_dict["t"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["a"][1] * 16, 96 + self.alphabet_dict["a"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["r"][1] * 16, 96 + self.alphabet_dict["r"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["t"][1] * 16, 96 + self.alphabet_dict["t"][0] * 16, 16, 16)
        start_x+=32
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["t"][1] * 16, 96 + self.alphabet_dict["t"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["h"][1] * 16, 96 + self.alphabet_dict["h"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["e"][1] * 16, 96 + self.alphabet_dict["e"][0] * 16, 16, 16)
        start_x+=32
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["g"][1] * 16, 96 + self.alphabet_dict["g"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["a"][1] * 16, 96 + self.alphabet_dict["a"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["m"][1] * 16, 96 + self.alphabet_dict["m"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["e"][1] * 16, 96 + self.alphabet_dict["e"][0] * 16, 16, 16)
        start_x+=16
        
        if pyxel.btn(pyxel.KEY_RETURN):
            self.is_press_enter = True
            time.sleep(0.1)
        
    def get_user_name(self):
        start_x = 400
        start_y = 300
               
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["w"][1] * 16, 96 + self.alphabet_dict["w"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["h"][1] * 16, 96 + self.alphabet_dict["h"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["a"][1] * 16, 96 + self.alphabet_dict["a"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["t"][1] * 16, 96 + self.alphabet_dict["t"][0] * 16, 16, 16)
        start_x+=32
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["i"][1] * 16, 96 + self.alphabet_dict["i"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["s"][1] * 16, 96 + self.alphabet_dict["s"][0] * 16, 16, 16)
        start_x+=32
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["y"][1] * 16, 96 + self.alphabet_dict["y"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["o"][1] * 16, 96 + self.alphabet_dict["o"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["u"][1] * 16, 96 + self.alphabet_dict["u"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["r"][1] * 16, 96 + self.alphabet_dict["r"][0] * 16, 16, 16)
        start_x+=32
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["n"][1] * 16, 96 + self.alphabet_dict["n"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["a"][1] * 16, 96 + self.alphabet_dict["a"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["m"][1] * 16, 96 + self.alphabet_dict["m"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["e"][1] * 16, 96 + self.alphabet_dict["e"][0] * 16, 16, 16)
        start_x+=48
        
        
            
        for key in self.alphabet_dict:
            if pyxel.btn(ord(key)):
                self.user_name.append(key)
                time.sleep(0.18)
                break
            if pyxel.btn(pyxel.KEY_SPACE):
                self.user_name.append(" ")
                time.sleep(0.18)
                break
                
        for c in self.user_name:
            if c == " ":
                start_x+=16
            else:
                pyxel.blt(start_x, start_y, 1, self.alphabet_dict[c][1] * 16, 96 + self.alphabet_dict[c][0] * 16, 16, 16)
            start_x+=16
            
            
        if pyxel.btn(pyxel.KEY_RETURN):
            self.is_start = True
          
    def end_game(self):
        start_x = 400
        start_y = 300
        
        # Game Over
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["g"][1] * 16, 96 + self.alphabet_dict["g"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["a"][1] * 16, 96 + self.alphabet_dict["a"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["m"][1] * 16, 96 + self.alphabet_dict["m"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["e"][1] * 16, 96 + self.alphabet_dict["e"][0] * 16, 16, 16)
        start_x+=32
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["o"][1] * 16, 96 + self.alphabet_dict["o"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["v"][1] * 16, 96 + self.alphabet_dict["v"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["e"][1] * 16, 96 + self.alphabet_dict["e"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["r"][1] * 16, 96 + self.alphabet_dict["r"][0] * 16, 16, 16)
        
        # name scored (score)
        start_x = 350
        start_y = 400
        for c in self.user_name:
            if c == " ":
                start_x+=16
            else:
                pyxel.blt(start_x, start_y, 1, self.alphabet_dict[c][1] * 16, 96 + self.alphabet_dict[c][0] * 16, 16, 16)
            start_x+=16
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["s"][1] * 16, 96 + self.alphabet_dict["s"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["c"][1] * 16, 96 + self.alphabet_dict["c"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["o"][1] * 16, 96 + self.alphabet_dict["o"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["r"][1] * 16, 96 + self.alphabet_dict["r"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["e"][1] * 16, 96 + self.alphabet_dict["e"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["d"][1] * 16, 96 + self.alphabet_dict["d"][0] * 16, 16, 16)
        start_x+=48
        
        # Number
        num_string = str(self.total_score)
        for num in num_string:
            pyxel.blt(start_x, start_y, 1, 16 * int(num), 64, 16, 32)
            start_x += 16
        
        start_x = 400
        start_y = 500    
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["p"][1] * 16, 96 + self.alphabet_dict["p"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["r"][1] * 16, 96 + self.alphabet_dict["r"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["e"][1] * 16, 96 + self.alphabet_dict["e"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["s"][1] * 16, 96 + self.alphabet_dict["s"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["s"][1] * 16, 96 + self.alphabet_dict["s"][0] * 16, 16, 16)
        start_x+=32
        
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["e"][1] * 16, 96 + self.alphabet_dict["e"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["n"][1] * 16, 96 + self.alphabet_dict["n"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["t"][1] * 16, 96 + self.alphabet_dict["t"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["e"][1] * 16, 96 + self.alphabet_dict["e"][0] * 16, 16, 16)
        start_x+=16
        pyxel.blt(start_x, start_y, 1, self.alphabet_dict["r"][1] * 16, 96 + self.alphabet_dict["r"][0] * 16, 16, 16)
        start_x+=16
        
        if pyxel.btn(pyxel.KEY_RETURN):
            self.is_game_over = False
            self.is_start = False
            self.is_press_enter = False
            self.user_name.clear()
            time.sleep(0.1)
    
    def draw(self):
        pyxel.cls(0)
         # level 0
        # Score text
        self.draw_score()
        
        # level 0
        # MAP
        for i in range(4):
            for j in range(5):
                pyxel.blt(256*j,128*i + App.BOX_Y, 
                  2, 0, 0, 
                  256, 128)
        # status
        for i in range(5):
            pyxel.blt(256*i, 512 +  App.BOX_Y, 
                  2, 0, 128, 
                  256, 128)
           
        if not self.is_press_enter:
            self.show_press_menu()
        elif not self.is_start: 
            self.get_user_name()
        elif self.is_game_over:
            self.end_game()
        else:
            # level 1
            # life
            self.human.life_draw()
        
            # level 1
            # gauge
            self.ability_bar_draw()
            
            # level 1
            # draw item
            if self.is_ghost:
                Item.draw_status(256*3 + 40, 520, "ghost")
            if self.is_undying:
                Item.draw_status(256*3 + 72, 520, "undying")
            
            # level1
            # Draw poop
            for p in self.poop_list:
                p.draw()
            self.human.draw()
            
            # level2
            # Draw item
            for item in self.item_list:
                item.draw()
        
        
        
        
   
if __name__ =="__main__":    
    FILE = Path(__file__).resolve()
    ROOT = FILE.parents[0]  # root directory
    App(ROOT)