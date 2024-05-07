import pygame
import time
import multiprocessing as mp
import tkinter as tk
import math, random

pygame.init()

def physics_engine(reset_event, Kg, scale, elasticity, roughness, spawn_event, reset_objs_event, static):
    win = pygame.display.set_mode([500, 500])
    pygame.display.set_caption("Physics Engine Viewport")

    class Timer:
        def __init__(self):
            self.elapsed = 0
            self.deltatime = 0
            self.frames = 0
            self.last_frame_time = time.time()
            self.start = time.time()

        def frame(self):
            self.elapsed = time.time() - self.start
            self.deltatime = time.time() - self.last_frame_time
            self.last_frame_time = time.time()
            self.frames += 1

    class GameObject:
        def __init__(self, window, scale, density, g, elasticity, pos, roughness):
            self.win = window
            self.g = g
            self.scale = scale
            self.density = density
            self.mass = (scale * scale) * density
            self.position = [win.get_size()[0] / 2 + pos[0], win.get_size()[0] / 2 + pos[1]]
            self.velocity = [0, 0]
            self.terminal_vel = 1000
            self.elasticity = elasticity
            self.lastFrameMouseDown = False
            self.color = (0,0,0)
            self.is_selected = False
            self.grabbing = False
            self.roughness = roughness
            self.static = False

        def frame(self, timer, objs):

            if self.static:
                self.color = (0,153,255)
            else:
                self.color = (0,0,0)
            if self.is_selected:
                pygame.draw.rect(self.win, (94, 255, 140), (self.position[0] - self.scale / 2 - 2, self.position[1] - self.scale / 2 - 2, self.scale+4, self.scale+4))

            pygame.draw.rect(self.win, self.color, (self.position[0] - self.scale / 2, self.position[1] - self.scale / 2, self.scale, self.scale))

            # Frame Physics

            keys = pygame.key.get_pressed()
            if keys[pygame.K_f]:
                mouseX, mouseY = pygame.mouse.get_pos()  # Obtain the mouse position first
                dist = math.sqrt(math.pow(mouseX - self.position[0], 2) + math.pow(mouseY - self.position[1], 2))

                mouseWind = [self.position[0] - mouseX, self.position[1] - mouseY]

                # Scale mouseWind based on distance
                if dist != 0:  # Avoid division by zero
                    mouseWind[0] /= 100 * (dist/100)
                    mouseWind[1] /= 100 * (dist/100)
                self.velocity[1] += mouseWind[1]
                self.velocity[0] += mouseWind[0]

            if self.velocity[1] < self.terminal_vel:
                self.velocity[1] += self.g * timer.deltatime

            if (not self.static):
                self.position[0] += self.velocity[0] * timer.deltatime
                self.position[1] += self.velocity[1] * timer.deltatime

            # Frame Collisions
            if self.position[0] > self.win.get_size()[0] - self.scale / 2:
                self.position[0] = self.win.get_size()[0] - self.scale / 2
                self.velocity[0] *= -1 * self.elasticity
            if self.position[0] < 0 + self.scale / 2:
                self.position[0] = 0 + self.scale / 2
                self.velocity[0] *= -1 * self.elasticity

            if self.position[1] > self.win.get_size()[1] - self.scale / 2:
                self.position[1] = self.win.get_size()[1] - self.scale / 2
                self.velocity[1] *= -1 * self.elasticity
                self.velocity[0] -= self.velocity[0]*(self.roughness/10)
                if (abs(self.velocity[1]) < 5):
                    self.velocity[1] = 0
            if self.position[1] < 0 + self.scale / 2:
                self.position[1] = 1 + self.scale / 2
                self.velocity[1] *= -1 * self.elasticity
                self.velocity[0] -= self.velocity[0]*(self.roughness/10)
                if (abs(self.velocity[1]) < 5):
                    self.velocity[1] = 0

            
            for obj in objs:
                thisUpperBound = self.position[1] + self.scale/2
                thisLowerBound = self.position[1] - self.scale/2
                thisRightBound = self.position[0] + self.scale/2
                thisLeftBound = self.position[0] - self.scale/2

                otherUpperBound = obj.position[1] + obj.scale/2
                otherLowerBound = obj.position[1] - obj.scale/2
                otherRightBound = obj.position[0] + obj.scale/2
                otherLeftBound = obj.position[0] - obj.scale/2


                yTopCollision = thisUpperBound > otherLowerBound and thisUpperBound < otherUpperBound
                yBottomCollision = thisLowerBound > otherLowerBound and thisLowerBound < otherUpperBound

                yCenterCollision = self.position[1] > otherLowerBound-self.scale/2+1 and self.position[1] < otherUpperBound+self.scale/2-1


                xLeftCollsion = thisLeftBound > otherLeftBound and thisLeftBound < otherRightBound
                xRightCollision = thisRightBound > otherLeftBound and thisRightBound < otherRightBound

                xCenterCollision = self.position[0] > otherLeftBound - self.scale/2+1 and self.position[0] < otherRightBound + self.scale/2-1

                if xCenterCollision:
                    if yTopCollision:
                        transferredEnergy = self.scale/obj.scale * self.velocity[1] * (1-self.elasticity)
                        obj.velocity[1] += transferredEnergy
                        self.velocity[1] = -1 * self.scale/obj.scale * self.velocity[1] * self.elasticity
                        self.position[1] = obj.position[1] - obj.scale/2 - self.scale/2
                        self.velocity[0] -= self.velocity[0]*self.roughness
                        if (abs(self.velocity[1]) < 15):
                            self.velocity[1] = 0
                    if yBottomCollision:
                        transferredEnergy = self.scale/obj.scale * self.velocity[1] * (1-self.elasticity)
                        obj.velocity[1] += transferredEnergy
                        self.velocity[1] = -1 * self.scale/obj.scale * self.velocity[1] * self.elasticity
                        self.position[1] = obj.position[1] + obj.scale/2 + self.scale/2
                        self.velocity[0] -= self.velocity[0]*self.roughness
                        if (abs(self.velocity[1]) < 15):
                            self.velocity[1] = 0
                if yCenterCollision:
                    if xLeftCollsion:
                        transferredEnergy = self.scale/obj.scale * self.velocity[0] * (1-self.elasticity)
                        obj.velocity[0] += transferredEnergy
                        self.velocity[0] = -self.scale/obj.scale * self.velocity[0] * self.elasticity
                        self.position[0] = obj.position[0] + obj.scale/2 + self.scale/2
                    if xRightCollision:
                        transferredEnergy = self.scale/obj.scale * self.velocity[0] * (1-self.elasticity)
                        obj.velocity[0] += transferredEnergy
                        self.velocity[0] = -self.scale/obj.scale * self.velocity[0] * self.elasticity
                        self.position[0] = obj.position[0] - obj.scale/2 - self.scale/2

            # Mouse grabbing
            if pygame.mouse.get_pressed()[0]:
                mousex, mousey = pygame.mouse.get_pos()

                other_grabbing = any(obj.grabbing for obj in objs if obj is not self)

                if self.position[0] - self.scale/2 < mousex < self.position[0] + self.scale/2 and self.position[1] - self.scale/2 < mousey < self.position[1] + self.scale/2 and not (other_grabbing or self.lastFrameMouseDown):
                    self.grabbing = True

                if self.grabbing:
                    xvel = (mousex - self.position[0]) * math.sqrt(math.pow(mousex - self.position[0], 2) + math.pow(mousey - self.position[1], 2)) / 50
                    yvel = (mousey - self.position[1]) * math.sqrt(math.pow(mousex - self.position[0], 2) + math.pow(mousey - self.position[1], 2)) / 50
                    self.velocity = [xvel, yvel]

                self.lastFrameMouseDown = True
            elif pygame.mouse.get_pressed()[2]:
                mousex, mousey = pygame.mouse.get_pos()
                if self.position[0] - self.scale/2 < mousex < self.position[0] + self.scale/2 and self.position[1] - self.scale/2 < mousey < self.position[1] + self.scale/2:
                    self.is_selected = True
                else:
                    self.is_selected = False
            else:
                mousex, mousey = pygame.mouse.get_pos()
                self.grabbing = False

                self.lastFrameMouseDown = False


    # This class is only for storing data related to each segment in the rope
    class ropeSegment:
        def __init__(self, pos):
            self.position = pos
            self.velocity = [0,0]

    # This class is used to store data for rope start point
    class ropeStart:
        def __init__(self, pos):
            self.position = pos


    # This class runs physics for all segments of rope
    class rope:
        def __init__(self, ropeSegments, segmentLength, window, g):
            self.segments = ropeSegments
            self.segLen = segmentLength
            self.segments = []
            self.window = window
            self.g = g

            self.termvel = 1

            winX, winY = self.window.get_size()

            self.segments.append(ropeStart([winX/2, winY/2]))

            for i in range(ropeSegments):
                self.segments.append(ropeSegment([winX/2, winY/2 + self.segLen * i]))
        def frame(self, timer):
            winX, winY = self.window.get_size()
            for i in range(len(self.segments)-1):
                segment = self.segments[i+1]
                pos1 = (self.segments[i+1].position[0], self.segments[i+1].position[1])
                pos2 = (self.segments[(i+2) % len(self.segments)].position[0], self.segments[(i+2) % len(self.segments)].position[1])
                pygame.draw.line(self.window, (0,0,0), pos1, pos2, 5)

                mouseX, mouseY = pygame.mouse.get_pos()
                mouseWind = [segment.position[0] - mouseX, segment.position[1] - mouseY]

                mouseWind[0] /= 1000 / random.randint(1,5)
                mouseWind[1] /= 1000 / random.randint(1,5)

                segment.velocity[0] += mouseWind[0]
                segment.velocity[1] += mouseWind[1]


                if segment.velocity[1] < self.termvel:
                    segment.velocity[1] += self.g
                segment.position[1] += segment.velocity[1]
                segment.position[0] += segment.velocity[0]

                distToLastSeg = math.sqrt(math.pow(segment.position[0] - self.segments[i-1].position[0],2) + math.pow(segment.position[1] - self.segments[i-1].position[1],2))

                if (distToLastSeg > self.segLen):
                    vector = [segment.position[0] - self.segments[i].position[0], segment.position[1] - self.segments[i].position[1]]
                    magnitude = math.sqrt(math.pow(vector[0],2) + math.pow(vector[1],2))
                    if magnitude == 0:
                        magnitude = 1
                    vector = [vector[0]/magnitude, vector[1]/magnitude]

                    target = vector*self.segLen

                    target[0] += winX/2
                    target[1] += winY/2

                    xvel = (target[0] - segment.position[0]) * math.sqrt(math.pow(target[0] - segment.position[0], 2) + math.pow(target[1] - segment.position[1], 2)) / 5000
                    yvel = (target[1] - segment.position[1]) * math.sqrt(math.pow(target[1] - segment.position[0], 2) + math.pow(target[1] - segment.position[1], 2)) / 5000
                    segment.velocity = [xvel, yvel]
                else:
                    segment.velocity = [0,0]

                
                 


    scales = [25, 25]
    positions = [[0,0], [100,0]]
    roughnesses = [0.1, 0.1]
    elasticities = [0.7, 0.7]
    scene_objects = []
    scene_objects.append(GameObject(win, scales[0], 1, Kg.value, elasticities[0], positions[0], roughnesses[0]))
    scene_objects.append(GameObject(win, scales[1], 1, Kg.value, elasticities[1], positions[1], roughnesses[1]))
    timer = Timer()
    running = True

    last_frame_scale_slider = 0
    last_frame_elasticity_slider = 0
    last_frame_roughness_slider = 0


    #rope = rope(10, 10, win, 5)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        win.fill((255, 255, 255))
        for obj in scene_objects:
            other_objs = [other_obj for other_obj in scene_objects if other_obj != obj]
            obj.frame(timer, other_objs)

        #rope.frame(timer)
        pygame.display.flip()
        timer.frame()

        # Scene reset handling
        if reset_event.value == True:
            print("Resetting Scene")
            for obj in scene_objects:
                scene_objects[scene_objects.index(obj)] = GameObject(win, scales[scene_objects.index(obj)], 1, Kg.value, elasticities[scene_objects.index(obj)], positions[scene_objects.index(obj)], roughnesses[scene_objects.index(obj)])
            reset_event.value = False

        if spawn_event.value == True:
            print("Spawning Object")
            anyObjGrabbed = any(obj.is_selected for obj in scene_objects)
            if (anyObjGrabbed):
                scales.append(50)
                positions.append([0,0])
                roughnesses.append(0.1)
                elasticities.append(0.7)
            else:
                scales.append(scale.value)
                positions.append([0,0])
                roughnesses.append(roughness.value)
                elasticities.append(elasticity.value)
            
            scene_objects.append(GameObject(win, scales[len(scene_objects)], 1, Kg.value, elasticities[len(scene_objects)], positions[len(scene_objects)], roughnesses[len(scene_objects)]))
            spawn_event.value = False

        if reset_objs_event.value == True:
            print("De-Spawning All Objects")
            scales = []
            positions = []
            roughnesses = []
            elasticities = []
            scene_objects = []
            reset_objs_event.value = False

        if static.value == True:
            for obj in scene_objects:
                if obj.is_selected:
                    if  obj.static:
                        obj.static = False
                        obj.velocity = [0,0]
                    else:
                        obj.static = True
            static.value = False

        if (scale.value != last_frame_scale_slider):
            for obj in scene_objects:
                if obj.is_selected:
                    scales[scene_objects.index(obj)] = scale.value
        if (elasticity.value != last_frame_elasticity_slider):
            for obj in scene_objects:
                if obj.is_selected:
                    elasticities[scene_objects.index(obj)] = elasticity.value
        if (roughness.value != last_frame_roughness_slider):
            for obj in scene_objects:
                if obj.is_selected:
                    roughnesses[scene_objects.index(obj)] = roughness.value

        last_frame_scale_slider = scale.value
        last_frame_elasticity_slider = elasticity.value
        last_frame_roughness_slider = roughness.value

        #time.sleep(0.1)

    pygame.quit()

def settings_ui(reset_event,Kg,scale,elasticity,roughness,spawn_event,reset_objs_event,static):
    def reset():
        reset_event.value = True
    
    def spawn():
        spawn_event.value = True

    def removeall():
        reset_objs_event.value = True

    def on_g_change(value):
        Kg.value = float(value)

    def on_scale_change(value):
        scale.value = float(value)

    def on_elasticity_change(value):
        elasticity.value = float(value)

    def on_roughness_change(value):
        roughness.value = float(value)

    def set_static():
        static.value = True

    win = tk.Tk()
    win.title("Physics Engine Settings")
    win.geometry("250x500")

    gravity_label = tk.Label(text="World Gravity:")
    gravity_label.pack()

    gravity_slider = tk.Scale(win, from_=0, to=981, orient="horizontal", command=on_g_change)
    gravity_slider.pack()

    scale_label = tk.Label(text="Object Scale:")
    scale_label.pack()

    scale_slider = tk.Scale(win, from_=5, to=200, orient="horizontal", command=on_scale_change)
    scale_slider.pack()

    elasticity_label = tk.Label(text="Object Elasticity:")
    elasticity_label.pack()

    elasticity_slider = tk.Scale(win, from_=0, to=2, orient="horizontal", command=on_elasticity_change, resolution=0.1)
    elasticity_slider.pack()

    roughness_label = tk.Label(text="Object Roughness:")
    roughness_label.pack()

    roughness_slider = tk.Scale(win, from_=0, to=1, orient="horizontal", command=on_roughness_change, resolution=0.1)
    roughness_slider.pack()

    staticButton = tk.Button(text="Toggle Frozen", command=set_static)
    staticButton.pack()

    spawnButton = tk.Button(text="Spawn Object", command=spawn)
    spawnButton.pack()

    delButton = tk.Button(text="Remove All Objects", command=removeall)
    delButton.pack()

    resetButton = tk.Button(text="Reset", command=reset)
    resetButton.pack()

    win.mainloop()

if __name__ == "__main__":
    reset_event = mp.Value('b', False)
    spawn_event = mp.Value('b', False)
    static = mp.Value('b', False)
    reset_objs_event = mp.Value('b', False)
    Kg = mp.Value('f', 98.1)
    scale = mp.Value('f', 100)
    elasticity = mp.Value('f', 0.7)
    roughness = mp.Value('f', 0.2)
    engine_process = mp.Process(target=physics_engine, args=(reset_event,Kg,scale,elasticity,roughness,spawn_event,reset_objs_event,static))
    ui_process = mp.Process(target=settings_ui, args=(reset_event,Kg,scale,elasticity,roughness,spawn_event,reset_objs_event,static))
    engine_process.start()
    ui_process.start()
