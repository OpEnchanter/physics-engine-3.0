import pygame
import time
import multiprocessing as mp
import tkinter as tk
import math

pygame.init()

def physics_engine(reset_event, Kg, scale):
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
        def __init__(self, window, scale, density, g, elasticity, pos):
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
            self.color = (0,0,255)
            self.is_selected = False
            self.grabbing = False

        def frame(self, timer, objs):
            pygame.draw.rect(self.win, self.color, (self.position[0] - self.scale / 2, self.position[1] - self.scale / 2, self.scale, self.scale))

            # Frame Physics
            if self.velocity[1] < self.terminal_vel:
                self.velocity[1] += self.g * timer.deltatime

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
            if self.position[1] < 0 + self.scale / 2:
                self.position[1] = 1 + self.scale / 2
                self.velocity[1] *= -1 * self.elasticity

            
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

                yCenterCollision = self.position[1] > otherLowerBound and self.position[1] < otherUpperBound


                xLeftCollsion = thisLeftBound > otherLeftBound and thisLeftBound < otherRightBound
                xRightCollision = thisRightBound > otherLeftBound and thisRightBound < otherRightBound

                xCenterCollision = self.position[0] > otherLeftBound and self.position[0] < otherRightBound

                if xCenterCollision or xLeftCollsion or xRightCollision:
                    if yTopCollision:
                        self.velocity[1] *= -1 * self.elasticity
                        self.position[1] = obj.position[1] - obj.scale/2 - self.scale/2
                    if yBottomCollision:
                        self.velocity[1] *= -1 * self.elasticity
                        self.position[1] = obj.position[1] + obj.scale/2 + self.scale/2
                if yCenterCollision:
                    if xLeftCollsion:
                        self.velocity[0] *= -1 * self.elasticity
                        self.position[0] = obj.position[0] + obj.scale/2 + self.scale/2
                    if xRightCollision:
                        self.velocity[0] *= -1 * self.elasticity
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
                    self.color = (255,0,0)
                    self.is_selected = True
                else:
                    self.color=(0,0,255)
                    self.is_selected = False
            else:
                mousex, mousey = pygame.mouse.get_pos()
                self.grabbing = False

                self.lastFrameMouseDown = False

    scales = [25, 25]
    positions = [[0,0], [100,0]]
    scene_objects = []
    scene_objects.append(GameObject(win, scales[0], 1, Kg.value, 0.7, positions[0]))
    scene_objects.append(GameObject(win, scales[1], 1, Kg.value, 0.7, positions[1]))
    timer = Timer()
    running = True

    last_frame_scale_slider = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        win.fill((255, 255, 255))
        for obj in scene_objects:
            other_objs = [other_obj for other_obj in scene_objects if other_obj != obj]
            obj.frame(timer, other_objs)
        pygame.display.flip()
        timer.frame()

        # Scene reset handling
        if reset_event.value == True:
            print("Resetting Scene")
            for obj in scene_objects:
                scene_objects[scene_objects.index(obj)] = GameObject(win, scales[scene_objects.index(obj)], 1, Kg.value, 0.7, positions[scene_objects.index(obj)])
            reset_event.value = False

        if (scale.value != last_frame_scale_slider):
            for obj in scene_objects:
                if obj.is_selected:
                    scales[scene_objects.index(obj)] = scale.value

        last_frame_scale_slider = scale.value

        #time.sleep(0.1)

    pygame.quit()

def settings_ui(reset_event,Kg,scale):
    def reset():
        reset_event.value = True

    def on_g_change(value):
        Kg.value = float(value)

    def on_scale_change(value):
        scale.value = float(value)

    win = tk.Tk()
    win.title("Physics Engine Settings")
    win.geometry("250x500")

    gravity_label = tk.Label(text="World Gravity:")
    gravity_label.pack()

    gravity_slider = tk.Scale(win, from_=50, to=981, orient="horizontal", command=on_g_change)
    gravity_slider.pack()

    scale_label = tk.Label(text="Object Scale:")
    scale_label.pack()

    scale_slider = tk.Scale(win, from_=25, to=200, orient="horizontal", command=on_scale_change)
    scale_slider.pack()

    resetButton = tk.Button(text="Reset", command=reset)
    resetButton.pack()

    win.mainloop()

if __name__ == "__main__":
    reset_event = mp.Value('b', False)
    Kg = mp.Value('f', 98.1)
    scale = mp.Value('f', 100)
    engine_process = mp.Process(target=physics_engine, args=(reset_event,Kg,scale,))
    ui_process = mp.Process(target=settings_ui, args=(reset_event,Kg,scale,))
    engine_process.start()
    ui_process.start()
