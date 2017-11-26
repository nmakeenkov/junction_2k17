from copy import deepcopy
from collections import Counter
import json


from IPython.display import clear_output
from matplotlib import pyplot as plt
from scipy.stats import norm
import numpy as np
from shapely.geometry import LineString


names = ["Alex", "John", "Mary"]
for i in range(50):
    names += ["guy_"+str(i)]
for i in range(50):
    names += ["girl_"+str(i)]


room_names = {
    '-1': 'Hall'
}
for i in range(100):
    room_names[str(i)] = "office_"+str(i)


printable = False

BIG_USERS = [1,7]


colors = [
	'#000','#5F9EA0','#D2691E','#F08080', 
	'#008000', '#DC143C','#00FFFF','#00008B',
	'#008B8B','#B8860B','#A9A9A9','#A9A9A9',
	'#006400','#BDB76B','#8B008B','#556B2F',
	'#FF8C00','#9932CC','#8B0000','#E9967A'
]

class Door(object):
    # vertical
    
    def __init__(self, ptstart, ptend, left_rn, right_rn):
        self.ptstart = ptstart
        self.ptend = ptend
        self.left_rn = left_rn
        self.right_rn = right_rn
        
        
    def check_trace(self, prev, new):
        line1 = LineString([prev, new])
        line2 = LineString([self.ptstart, self.ptend])

       
        res = line1.intersection(line2)
        if res: 
            if prev[0] < self.ptstart[0]:
                return self.right_rn
            else:
                return self.left_rn
        else:
            return None


class Room(object):
    def __init__(self, area_w, area_h, left_upper, right_bottom, my_num):
        self.area_w=area_w
        self.area_h=area_h
        self.left_upper=left_upper
        self.right_bottom=right_bottom
        
        self.my_num=my_num

        self.walls = {}
        self.walls['left'] = lambda x,y: x > left_upper[0]
        self.walls['right'] = lambda x,y: x < right_bottom[0]
        self.walls['upper'] = lambda x,y: y < left_upper[1]
        self.walls['bottom'] = lambda x,y: y > right_bottom[1]

    def is_inside_room(self, x, y):
        inside = True
        for wall,checker in self.walls.items():
            inside = inside and checker(x,y)
        return inside

    
class Area(object):
    def __init__(self, w, h, people_number, speed=1.):
        self.w=w
        self.h=h
        self.people_number=people_number
        self.speed=speed
        self.X_crowd = np.random.randint(0, w, size=people_number)*1.
        self.Y_crowd = np.random.randint(0, h, size=people_number)*1.
        self.X_crowd_directions = np.zeros(people_number)
        self.Y_crowd_directions = np.zeros(people_number)
        self.rooms = []
        
    
    def init_rooms(self, rooms):
        self.rooms = rooms
        self.crowd_rooms = [
            self.get_room_number(x,y) 
            for x,y in zip(self.X_crowd, self.Y_crowd)
        ]
    
    def init_doors(self, doors):
        self.doors = doors
        
    def get_room_number(self,x,y):
        for room in self.rooms:
            ans = room.is_inside_room(x,y)
            if ans:
                return room.my_num
        return -1



    def make_iteration(self):
        prev_X = self.X_crowd.copy()
        prev_Y = self.Y_crowd.copy()
        
        addit = norm.rvs(0., self.speed, size=self.people_number)
        self.X_crowd_directions = 0.9*self.X_crowd_directions + 0.1*addit
        self.X_crowd += self.X_crowd_directions
        
        addit = norm.rvs(0., self.speed, size=self.people_number)
        self.Y_crowd_directions = 0.9*self.Y_crowd_directions + 0.1*addit
        self.Y_crowd += self.Y_crowd_directions

        self.X_crowd = [max([self.w*0.05,min([self.w*0.95,x])]) for x in self.X_crowd]
        self.Y_crowd = [max([self.h*0.05,min([self.h*0.95,y])]) for y in self.Y_crowd]
        
                
        new_X, new_Y = [],[]
        for p, coords in enumerate(zip(self.X_crowd, self.Y_crowd)):
            x,y = coords
            rn = self.get_room_number(x,y)
            from copy import deepcopy
            prev_room_number = deepcopy(self.crowd_rooms[p])
            if not rn == prev_room_number:
                any_res = False
                for door in self.doors:
                    res = door.check_trace([prev_X[p], prev_Y[p]], [x,y])
                    if res is None:
                        pass
                    else:
                        any_res = True
                        self.crowd_rooms[p] = res
                if not any_res:
                    x = prev_X[p]
                    y = prev_Y[p]
                if not (0 < x < self.w) or not (0 < y < self.h):
                    x = prev_X[p]
                    y = prev_Y[p]
            new_X += [x]
            new_Y += [y]
        self.X_crowd = np.array(new_X, dtype='float64')
        self.Y_crowd = np.array(new_Y, dtype='float64')
        if printable and not np.allclose(prev_room_number, self.crowd_rooms):
            print 'crowd_rooms:', self.crowd_rooms
            print 'rooms counts:', json.dumps(
                {room_names[str(k)]: v for k,v in Counter(self.crowd_rooms).items()},
                indent=4,
            )
            print 'people:', json.dumps(
                dict(zip(names,[room_names[str(k)] for k in self.crowd_rooms])),
                indent=4,
            )
            print '\n'
            

        
w,h=1300,800
area = Area(
    w=w,
    h=h,
    people_number=25,
    speed=5
)


rooms = [
    Room(
        area_w=w, 
        area_h=h,
        left_upper=(0,h),
        right_bottom=(w*.1,0),
        my_num=1,
    ),
    Room(
        area_w=w, 
        area_h=h,
        left_upper=(w*.1,h),
        right_bottom=(w*.2,0),
        my_num=2,
    ),
    Room(
        area_w=w,
        area_h=h,
        left_upper=(w*.2,h),
        right_bottom=(w*.5,0),
        my_num=3,
    ),
    Room(
        area_w=w,
        area_h=h,
        left_upper=(w*.5,h),
        right_bottom=(w*.62,0),
        my_num=4,
    ),
    Room(
        area_w=w,
        area_h=h,
        left_upper=(w*.62,h),
        right_bottom=(w*.7,0),
        my_num=5,
    ),
    Room(
        area_w=w,
        area_h=h,
        left_upper=(w*.7,h),
        right_bottom=(w,0),
        my_num=6,
    ),
]

doors = [
    Door(
        ptstart=(w*.1,h*.2),
        ptend=(w*.1,h*.4),
        left_rn=1,
        right_rn=2
    ),
    Door(
        ptstart=(w*.2,h*.6),
        ptend=(w*.2,h*.8),
        left_rn=2,
        right_rn=3
    ),
    Door(
        ptstart=(w*.2,h*.1),
        ptend=(w*.2,h*.2),
        left_rn=2,
        right_rn=3
    ),
    Door(
        ptstart=(w*.5,h*.1),
        ptend=(w*.5,h*.35),
        left_rn=3,
        right_rn=4
    ),
    Door(
        ptstart=(w*.62,h*.1),
        ptend=(w*.62,h*.6),
        left_rn=4,
        right_rn=5
    ),
    Door(
        ptstart=(w*.62,h*.8),
        ptend=(w*.62,h*.9),
        left_rn=4,
        right_rn=5
    ),
    Door(
        ptstart=(w*.7,h*.8),
        ptend=(w*.7,h*.9),
        left_rn=5,
        right_rn=6
    ),
]

area.init_rooms(rooms)
area.init_doors(doors)



import pantograph
import math


class Rotary(pantograph.PantographHandler):
    def setup(self):
        pass

    def update(self):

        self.clear_rect(0, 0, self.width, self.height)
        self.draw_rect(0, 0, w, h, color = "#111")
        for room in area.rooms:
            lu = room.left_upper
            x1,y1 = lu
            rb = room.right_bottom
            x2,y2=rb
            self.draw_rect(x1,0,abs(x1-x2),abs(y1-y2), color = "#800000")

        for door in area.doors:
            self.fill_rect(
                door.ptstart[0], door.ptstart[1],
                10, abs(door.ptstart[1]-door.ptend[1]),
                color="#66CDAA"
            )
        i=0
        for x,y in zip(area.X_crowd, area.Y_crowd):
            rad = 6
            if i in BIG_USERS:
                img_src = '/img/'+str(i)+'.png'
                self.draw("image", src=img_src, x=x, y=y, width=60, height=60)
                rad = 0.5
                #self.draw_line(x+50,y+100,w,h)
            else:
                self.fill_circle(x,y,rad,color=colors[area.crowd_rooms[i]+1])
            #else:
                #self.fill_rect(x,y,8,8,color=colors[area.crowd_rooms[i]+1])
            i+=1

        area.make_iteration()
        
                

if __name__ == '__main__':
    #app = pantograph.PantographApplication([
    #    ("Pantograph", "/", Rotary)
    #])
    app = pantograph.SimplePantographApplication(Rotary)
    app.run()



