import pyxel
import random
from pathlib import Path
import time
import enum

from character.poop import Poop
from character.human import Human
from item import Item
from bird import Bird
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
    ITEM_TIME = 5
    BIRD_TIME = 5
    
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
        self.is_bird_time = False
        
        # 능력 게이지
        self.sb_gauge = 0
        self.AB_FULL_GAUGE = 5 # 0~5  : 0, 20, 40, 60, 80, 100

        # Item list
        self.item_list = []

        # use item
        self.is_ghost = False
        self.ghost_start_time = 0
        self.ghost_dt = 0
        
        self.is_undying = False
        self.undying_start_time = 0
        self.undying_dt = 0
        
        # Score
        self.total_score = 0
        
        # obstacle : bird
        # 한 번에 나타나는 새 마리 수
        self.bird_level = 0
        self.bird_num = [1, 1, 2, 4, 4]
        self.bird_speed = [5, 10, 20, 40, 5]
        
        self.bird_list = []
        
        # 새 끝나는 범위 허용 오차
        self.bird_tolerance = 10
        
        # bird dt
        self.bird_last_time = time.time()
        self.bird_dt = 0
        self.bird_move_list= []
        
        pyxel.run(self.update, self.draw)

    def game_init(self):
        # 객체 생성
        self.poop_list.clear()
        self.poop_cool_list.clear()
        
        rand_x, rand_y = self.get_rand_pos()
        self.human = Human(rand_x, rand_y)
        
        # 시작 화면
        self.user_name.clear()
        
        self.is_press_enter = False
        self.is_start= False
        self.is_game_over = False
        
        # 시작 타임
        self.start_time = time.time()
        
        # For once draw
        self.is_two_time = False
        self.is_ab_time = False
        self.is_cool_time = False 
        self.is_item_time = False
        self.is_bird_time = False
        
        # 능력 게이지
        self.sb_gauge = 0
        self.AB_FULL_GAUGE = 5 # 0~5  : 0, 20, 40, 60, 80, 100

        # Item list
        self.item_list.clear()

        # use item
        self.is_ghost = False
        self.ghost_start_time = 0
        self.ghost_dt = 0
        
        self.is_undying = False
        self.undying_start_time = 0
        self.undying_dt = 0
        
        # Score
        self.total_score = 0
        
        # obstacle : bird
        # 한 번에 나타나는 새 마리 수
        self.bird_level = 0
        self.bird_list.clear()
        
        # bird dt
        self.bird_last_time = time.time()
        self.bird_dt = 0
        self.bird_move_list.clear()

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
        
        self.bird_dt = now - self.bird_last_time
        self.bird_last_time = now
        for i in range(len(self.bird_move_list)):
            self.bird_move_list[i] += self.bird_dt

        i = 0 
        while i < len(self.bird_list):  
        # for i in range(len(self.bird_list)): 
            if self.bird_move_list[i] > 1 / self.bird_list[i].speed:
                if self.bird_list[i].level == 4:
                    self.bird_list[i].special_move(self.human.x, self.human.y)
                else:
                    x = self.bird_list[i].x 
                    y = self.bird_list[i].y
                    if self.bird_list[i].rand_direction == Direction.UP.value:
                        y -= Bird.MOVE_DIST
                    elif self.bird_list[i].rand_direction == Direction.DOWN.value:
                        y += Bird.MOVE_DIST
                    elif self.bird_list[i].rand_direction == Direction.RIGHT.value:
                        x += Bird.MOVE_DIST
                    elif self.bird_list[i].rand_direction == Direction.LEFT.value:
                        x -= Bird.MOVE_DIST
                        
                    self.bird_list[i].x = x
                    self.bird_list[i].y = y
                # 삭제
                if (self.bird_list[i].x > App.WIDHT +self.bird_tolerance or self.bird_list[i].x < -self.bird_tolerance) or\
                    (self.bird_list[i].y > 480 + self.bird_tolerance or self.bird_list[i].y < -self.bird_tolerance):
                        del self.bird_list[i]
                        del self.bird_move_list[i]
                        continue
                self.bird_move_list[i] = 0
            i += 1
        
        # 기본 동작 제어 시간
        action_dt = int(now - self.start_time)
        
        # Item 제어 시간
        # Ghost
        if self.is_ghost:
            self.ghost_dt = int(now - self.ghost_start_time)
        
        # Undying
        if self.is_undying:
            self.undying_dt = int(now - self.undying_start_time)
        
        if self.ghost_dt == App.GHOST_TIME:
            self.is_ghost = False
        if self.undying_dt == App.UNDYING_TIME:
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
            
        # 새 추가    
        if not self.is_bird_time and action_dt % App.BIRD_TIME == 0: # 10초일 때 한 번 동작
            # Level check
            if self.total_score < 10:
                self.bird_level = 0
            elif self.total_score < 50:
                self.bird_level = 1
            elif self.total_score < 100:
                self.bird_level = 2
            elif self.total_score < 300:
                self.bird_level = 3
            else:
                self.bird_level = 4
            
            if action_dt != 0:
                # Score 올림
                self.drop_bird()
            self.is_bird_time = True
        elif action_dt % App.BIRD_TIME != 0:
            self.is_bird_time = False 
         
     
    def drop_bird(self):
        for i in range(self.bird_num[self.bird_level]):
            self.bird_list.append(Bird(self.bird_level, self.bird_speed[self.bird_level]))
            self.bird_move_list.append(0)
            
        
    
    def drop_item(self): 
        self.item_list.append(Item())
        
        
       
    def use_ability(self):
        # Update score
        self.total_score += 5000
        
        # Delete all obst
        # Poop
        self.poop_list.clear()
        self.poop_cool_list.clear()
        
        # Bird
        self.bird_list.clear()
        self.bird_move_list.clear()
        
    
    def check_collisions(self, x, y):
        center_x,center_y = self.calc_pos(x,y)
        # 똥 리스트에서 해당 똥 있는지 확인
        for i in range(len(self.poop_list) - len(self.poop_cool_list)):
            # if center_x == self.poop_list[i].x and center_y == self.poop_list[i].y: # 중심 좌표로 판별

            if self.is_hit_box("obstacle", (self.poop_list[i].x, self.poop_list[i].y), (x,y)): # 거리에 따른 히트박스 판별
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
            
        # 새 확인
        for i in range(len(self.bird_list)):
            if self.is_hit_box("obstacle", (self.bird_list[i].x, self.bird_list[i].y), (x,y)):
                if self.is_undying:
                    self.total_score += App.REMOVE_SCORE
                    self.bird_list.remove(self.bird_list[i])
                    break
                if self.is_ghost:
                    break
                
                self.bird_list.remove(self.bird_list[i])
                del self.bird_move_list[i]
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
            
        elif target == "obstacle":
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
        x, y = self.calc_pos(self.human.x+16, self.human.y+16)
        is_exist = False
        for poop in self.poop_list:
            if poop.x == x and poop.y == y:
                is_exist = True
                break
        if not is_exist:
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
            time.sleep(0.2)
        
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
            time.sleep(0.2)
            self.start_time = time.time()
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
            self.game_init()
            time.sleep(0.2)
    
    def draw_item(self):
        x = 256*3 + 40
        y = 520
        if self.is_ghost:
            ghost_x = x
            Item.draw_status(ghost_x, y, "ghost")
            ghost_x +=32
            # Number
            num_string = str(self.GHOST_TIME - self.ghost_dt)
            for num in num_string:
                pyxel.blt(ghost_x, y+32, 1, 16 * int(num), 64, 16, 32)
                ghost_x += 16
        if self.is_undying:
            undying_x = x
            Item.draw_status(undying_x, y+32, "undying")
            undying_x += 32
            # Number
            num_string = str(self.UNDYING_TIME-self.undying_dt)
            for num in num_string:
                pyxel.blt(undying_x, y+64, 1, 16 * int(num), 64, 16, 32)
                undying_x += 16
    
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
            self.draw_item()
            
            # level1
            # Draw poop
            for p in self.poop_list:
                p.draw()
            self.human.draw()
            
            # level2
            # Draw item
            for item in self.item_list:
                item.draw()
                
            # level 3
            # Draw bird
            for bird in self.bird_list:
                bird.draw()
        
        
        
        
   
if __name__ =="__main__":    
    FILE = Path(__file__).resolve()
    ROOT = FILE.parents[0]  # root directory
    App(ROOT)