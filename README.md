# **Avoid poop game**
<p>
Avoid poop game using pyxel.
</p>
<br>

## **Edit Program**
<p>
Use PyxelEditor
</p>
<br>

## **Condition**
Python 에서 pyxel import 해서 게임 만들기
1. **초기 설정 및 캐릭터, 똥, life 등 생성과 움직임 제어**
   - [x] 똥피하기 게임, 매 2초마다 캐릭터 있던자리에 똥 한개씩 설치, 
   - [x] 똥을 관통해서 지나갈수 없다. 
   - [x]  똥에 닿으면 life count 1개 준다.

2. **Own ability (Space bar)**
   - [ ] 100초 마다 능력을 사용
   - [ ] 스페이스 바를 누르면 능력 사용
   - [ ] 맵에 있는 똥 삭제 후 점수 증가 (전체 or 한개)

3. **Own ability2 (Mouse)**
   - [ ] 능력이 충전되는 바 가 있어야함
   - [ ] 마우스로 충전이 완료된 바 를 누르면 능력 사용 가능

4. **3가지의 랜덤 특수 아이템(30초 마다 랜덤한 장소에 생성)**
   - [ ] Life count 1 증가
   - [ ] 특정 시간동안 무적+똥에 닿으면 똥 삭제
   - [ ] 투명(무적)

5. **방해물**
   - [ ] 랜덤하게 등장하는 새
   - [ ] 랜덤한 방향으로 맵을 지나감
   - [ ] 처음엔 천천히 지나가지만 점점 빨리 지나가도록
   - [ ] 새와 캐릭터가 부딛히면 life count 1 감소
