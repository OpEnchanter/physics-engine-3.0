import pygame
import time
import multiprocessing as mp
import tkinter as tk
from tkinter import ttk
import math, os, json

pygame.init()

def physics_engine(reset_event, Kg, scale, elasticity, roughness, spawn_event, reset_objs_event, static, timescale, detail_view, savefile,loadnew,spr_stiff,spr_len):
    win = pygame.display.set_mode([750,750], pygame.RESIZABLE)
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

    class RigidBody:
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
            self.is_selected_secondary = False
            self.grabbing = False
            self.roughness = roughness
            self.static = False
            self.airRes = 0.999

        def frame(self, timer, objs, col):

            if self.static:
                self.color = (0,153,255)
            else:
                self.color = (0,0,0)
            if self.is_selected:
                pygame.draw.rect(self.win, (94, 255, 140), (self.position[0] - self.scale / 2 - 2, self.position[1] - self.scale / 2 - 2, self.scale+4, self.scale+4))
            if self.is_selected_secondary:
                pygame.draw.rect(self.win, (255, 184, 43), (self.position[0] - self.scale / 2 - 2, self.position[1] - self.scale / 2 - 2, self.scale+4, self.scale+4))
            pygame.draw.rect(self.win, self.color, (self.position[0] - self.scale / 2, self.position[1] - self.scale / 2, self.scale, self.scale))

            if (detail_view.value):
                pygame.draw.line(self.win, (0,0,255), self.position, [self.position[0] + (self.velocity[0]/10), self.position[1] + (self.velocity[1]/10)], 5)
                #pygame.draw.circle(self.win, (0,0,255), [self.position[0] + (self.velocity[0]/10), self.position[1] + (self.velocity[1]/10)], 5)

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

            if self.velocity[1] < self.terminal_vel and not self.grabbing:
                self.velocity[1] += self.g * timer.deltatime

            if (not self.static):
                self.position[0] += self.velocity[0] * timer.deltatime * timescale.value
                self.position[1] += self.velocity[1] * timer.deltatime * timescale.value
            
            self.velocity[0] *= self.airRes
            self.velocity[1] *= self.airRes

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

            if not col:
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
                            self.velocity[1] *= -self.elasticity
                            self.position[1] = obj.position[1] - obj.scale/2 - self.scale/2
                            self.velocity[0] -= self.velocity[0]*self.roughness
                            if (abs(self.velocity[1]) < 15):
                                self.velocity[1] = 0
                        if yBottomCollision:
                            transferredEnergy = self.scale/obj.scale * self.velocity[1] * (1-self.elasticity)
                            obj.velocity[1] += transferredEnergy
                            self.velocity[1] *= -self.elasticity
                            self.position[1] = obj.position[1] + obj.scale/2 + self.scale/2
                            self.velocity[0] -= self.velocity[0]*self.roughness
                            if (abs(self.velocity[1]) < 50):
                                self.velocity[1] = 0
                    if yCenterCollision:
                        if xLeftCollsion:
                            transferredEnergy = self.scale/obj.scale * self.velocity[0] * (1-self.elasticity)
                            obj.velocity[0] += transferredEnergy
                            self.velocity[0] *= -self.elasticity

                            self.position[0] = obj.position[0] + obj.scale/2 + self.scale/2
                        if xRightCollision:
                            transferredEnergy = self.scale/obj.scale * self.velocity[0] * (1-self.elasticity)
                            obj.velocity[0] += transferredEnergy
                            self.velocity[0] *= -self.elasticity

                            self.position[0] = obj.position[0] - obj.scale/2 - self.scale/2

            # Mouse grabbing
            if pygame.mouse.get_pressed()[0]:
                mousex, mousey = pygame.mouse.get_pos()

                other_grabbing = any(obj.grabbing for obj in objs if obj is not self)

                if self.position[0] - self.scale/2 < mousex < self.position[0] + self.scale/2 and self.position[1] - self.scale/2 < mousey < self.position[1] + self.scale/2 and not (other_grabbing or self.lastFrameMouseDown):
                    self.grabbing = True

                if self.grabbing:
                    dragdiv = 1000
                    xvel = (mousex - self.position[0]) * math.sqrt(math.pow(mousex - self.position[0], 2) + math.pow(mousey - self.position[1], 2))
                    yvel = (mousey - self.position[1]) * math.sqrt(math.pow(mousex - self.position[0], 2) + math.pow(mousey - self.position[1], 2))
                    self.velocity[0] += xvel/self.scale / dragdiv
                    self.velocity[1] += yvel/self.scale / dragdiv
                    self.airRes = 0.999 - 0.999/(math.sqrt(math.pow(mousex - self.position[0], 2) + math.pow(mousey - self.position[1], 2))*10)

                self.lastFrameMouseDown = True
            elif pygame.mouse.get_pressed()[2]:
                mousex, mousey = pygame.mouse.get_pos()
                if (keys[pygame.K_LSHIFT]):
                    if self.position[0] - self.scale/2 < mousex < self.position[0] + self.scale/2 and self.position[1] - self.scale/2 < mousey < self.position[1] + self.scale/2:
                        self.is_selected_secondary = True
                    else:
                        self.is_selected_secondary = False
                else:
                    if self.position[0] - self.scale/2 < mousex < self.position[0] + self.scale/2 and self.position[1] - self.scale/2 < mousey < self.position[1] + self.scale/2:
                        self.is_selected = True
                    else:
                        self.is_selected = False
            else:
                mousex, mousey = pygame.mouse.get_pos()
                self.grabbing = False
                self.airRes = 0.999

                self.lastFrameMouseDown = False

    # Spring system
    class spring():
        def __init__(self, obj1, obj2, length, stiffness):
            self.obj1 = obj1
            self.obj2 = obj2
            self.length = length
            self.stiffness = stiffness
        def frame(self, timer):
            # Retrieve locations of both objects
            p1 = self.obj1.position
            p2 = self.obj2.position

            # Get distance between points
            xdist = p2[0] - p1[0]
            ydist = p2[1] - p1[1]

            # Create vector pointing from one point to another
            magnitude = math.sqrt(math.pow(xdist, 2) + math.pow(ydist,2))
            vector = [0, 0]

            if magnitude != 0:
                vector = [xdist/magnitude, ydist/magnitude]

            # These are defining our target
            tx = p1[0]+(vector[0]*self.length)
            ty = p1[1]+(vector[1]*self.length)

            txdist = tx-p2[0]
            tydist = ty-p2[1]

            tdist = math.sqrt(math.pow(txdist, 2) + math.pow(tydist, 2))

            tmagnitude = math.sqrt(math.pow(xdist, 2) + math.pow(ydist,2))
            tvector = [0, 0]
            if magnitude != 0:
                tvector = [txdist/tmagnitude, tydist/tmagnitude]

            v1 = tdist * tvector[0]
            v2 = tdist * tvector[1]

            self.obj2.velocity[0] += v1 / (self.obj2.scale/10) * self.stiffness
            self.obj2.velocity[1] += v2 / (self.obj2.scale/10) * self.stiffness

            pygame.draw.line(win, (0,0,0), p1, p2, 7)

            if (detail_view.value):
                pygame.draw.circle(win, (255,0,0), [tx, ty], 5)

    scales = []
    positions = []
    roughnesses = []
    elasticities = []
    scene_objects = []
    scene_springs = []

    no_collisions = []

    def readSave(filePath):
        with open(filePath, "r") as file:
            # Load the JSON data from the file
            data = json.load(file)

            scne_rb = data["rigidbodies"]

            for rb in scne_rb:
                scales.append(data["rigidbodies"][rb]["scale"])
                positions.append([data["rigidbodies"][rb]["x"], data["rigidbodies"][rb]["y"]])
                roughnesses.append(data["rigidbodies"][rb]["roughness"])
                elasticities.append(data["rigidbodies"][rb]["elasticity"])
                scene_objects.append(RigidBody(win, scales[len(scene_objects)], 1, Kg.value, elasticities[len(scene_objects)], positions[len(scene_objects)], roughnesses[len(scene_objects)]))
                static = data["rigidbodies"][rb]["static"]
                if static.lower() == "true":
                    scene_objects[len(scene_objects)-1].static = True
                elif static.lower() == "false":
                    scene_objects[len(scene_objects)-1].static = False

                collidable = data["rigidbodies"][rb]["collidable"]
                if collidable.lower() == "true":
                    collidable = True
                elif collidable.lower() == "false":
                    collidable = False
                if (not collidable):
                    no_collisions.append(scene_objects[len(scene_objects)-1])

            scne_sp = data["springs"]

            for sp in scne_sp:
                scene_springs.append(spring(scene_objects[data["springs"][sp]["obj1"]], scene_objects[data["springs"][sp]["obj2"]], data["springs"][sp]["length"], data["springs"][sp]["stiffness"]))

    timer = Timer()
    running = True

    decoded_default_scene = savefile.value.decode()
    readSave(decoded_default_scene)

    last_frame_scale_slider = 0
    last_frame_elasticity_slider = 0
    last_frame_roughness_slider = 0

    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)  # You can specify a font file path instead of None for a custom font
    lastfpsupd = 0
    lastframetime = 0
    fpslist= []

    fps = 0

    lastFrameKeys = pygame.key.get_pressed()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        win.fill((255, 255, 255)) # Reset window to white
        clock.tick(6000)
        if time.time()-lastfpsupd > 0.1 and time.time() != lastframetime:
            fps = clock.get_fps()
            lastfpsupd = time.time()
            fpslist.append(fps)
        lastframetime = time.time()

        total = 0
        for fps in fpslist:
            total += fps
        avgfps = total/len(fpslist)

        if (len(fpslist)) > 50:
            fpslist.pop(0)

        text = font.render("FPS:"+str(int(round(fps, 2))), True, (0, 0, 0))  # (text, antialiasing, color)
        text_rect = text.get_rect(center=(55, 15))  # Center the text on the screen
        win.blit(text, text_rect)

        text = font.render("AVG:"+str(int(avgfps)), True, (0, 0, 0))  # (text, antialiasing, color)
        text_rect = text.get_rect(center=(55, 35))  # Center the text on the screen
        win.blit(text, text_rect)

        text = font.render("Objects:"+str(int(len(scene_objects))), True, (0, 0, 0))  # (text, antialiasing, color)
        text_rect = text.get_rect(center=(55, 55))  # Center the text on the screen
        win.blit(text, text_rect)

        text = font.render("Springs:"+str(int(len(scene_springs))), True, (0, 0, 0))  # (text, antialiasing, color)
        text_rect = text.get_rect(center=(55, 75))  # Center the text on the screen
        win.blit(text, text_rect)

        # Frame update handling
        for obj in scene_objects:
            other_objs = [other_obj for other_obj in scene_objects if other_obj != obj]
            for no_col in no_collisions:
                if (no_col != obj):
                    other_objs.remove(no_col)
            collisions = obj in no_collisions
            obj.frame(timer, other_objs, collisions)
        for spring_x in scene_springs:
            spring_x.frame(timer)

        pygame.display.flip()
        timer.frame()


        # Input Handling

        # Spring Add Handling
        keys = pygame.key.get_pressed()
        if keys[pygame.K_s] and not lastFrameKeys[pygame.K_s]: # Create a new spring in runtime
            obj1 = [obj for obj in scene_objects if obj.is_selected]
            obj2 = [obj for obj in scene_objects if obj.is_selected_secondary]

            if len(obj1) > 0 and len(obj2) > 0:
                scene_springs.append(spring(obj1[0], obj2[0], spr_len.value+(obj1[0].scale/2), spr_stiff.value))
                scene_springs.append(spring(obj2[0], obj1[0], spr_len.value+(obj2[0].scale/2), spr_stiff.value))
            else:
                print("Error: No two objects selected")
        if keys[pygame.K_e] and not lastFrameKeys[pygame.K_e]:
            print("Spawning Object")
            mousex, mousey = pygame.mouse.get_pos()
            anyObjGrabbed = any(obj.is_selected for obj in scene_objects)
            if (anyObjGrabbed):
                scales.append(50)
                positions.append([0,0])
                roughnesses.append(0.1)
                elasticities.append(0.7)
            else:
                scales.append(scale.value)
                positions.append([mousex-win.get_size()[0]/2,mousey-win.get_size()[1]/2])
                roughnesses.append(roughness.value)
                elasticities.append(elasticity.value)
            
            scene_objects.append(RigidBody(win, scales[len(scene_objects)], 1, Kg.value, elasticities[len(scene_objects)], positions[len(scene_objects)], roughnesses[len(scene_objects)]))
        if keys[pygame.K_q] and not lastFrameKeys[pygame.K_q]:
            for obj in scene_objects:
                if obj.is_selected:
                    if  obj.static:
                        obj.static = False
                        obj.velocity = [0,0]
                    else:
                        obj.static = True
        if keys[pygame.K_BACKSPACE] and not lastFrameKeys[pygame.K_BACKSPACE]:
            for obj in scene_objects:
                springs = [spring_obj for spring_obj in scene_springs if spring_obj.obj1 == obj or spring_obj.obj2 == obj]
                if obj.is_selected:
                    for spring_obj in springs:
                        if (spring_obj in scene_springs):
                            scene_springs.remove(spring_obj)
                    scene_objects.remove(obj)
            
        lastFrameKeys = keys

        # Scene reset handling
        if reset_event.value == True:
            print("Resetting Scene")
            for obj in scene_objects:
                scene_objects[scene_objects.index(obj)] = RigidBody(win, scales[scene_objects.index(obj)], 1, Kg.value, elasticities[scene_objects.index(obj)], positions[scene_objects.index(obj)], roughnesses[scene_objects.index(obj)])
            reset_event.value = False
        
        if loadnew.value == True:
            print("Loading Scene From File")
            # Load logic here

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
            
            scene_objects.append(RigidBody(win, scales[len(scene_objects)], 1, Kg.value, elasticities[len(scene_objects)], positions[len(scene_objects)], roughnesses[len(scene_objects)]))
            spawn_event.value = False

        if reset_objs_event.value == True:
            print("De-Spawning All Objects")
            scales = []
            positions = []
            roughnesses = []
            elasticities = []
            scene_objects = []
            scene_springs = []
            no_collisions = []
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
        
        if loadnew.value == True:
            print("Loading New Scene...")
            scales = []
            positions = []
            roughnesses = []
            elasticities = []
            scene_objects = []
            scene_springs = []
            no_collisions = []
            decoded_scene = savefile.value.decode()
            readSave(decoded_scene)
            loadnew.value = False


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

def settings_ui(reset_event,Kg,scale,elasticity,roughness,spawn_event,reset_objs_event,static,timescale, detail_view,savefile,loadnew,spr_stiff,spr_len):
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

    def on_timescale_change(value):
        timescale.value = float(value)

    def set_static():
        static.value = True

    def detail_view_update():
        if (not detail_view.value):
            detail_view.value = True
        else:
            detail_view.value = False

    # JSON scene loading system
    def load_save():
        loadwin = tk.Tk()
        loadwin.title("Load Scene")
        loadwin.geometry("500x125")
        selected_file = tk.StringVar()
        dropdown_menu = ttk.OptionMenu(loadwin, selected_file)
        def populate_dropdown():
            # Get the list of files in the specified directory
            directory = "saves"
            files = os.listdir(directory)
            
            # Populate the dropdown menu with filenames
            for file in files:
                dropdown_menu['menu'].add_command(label=file, command=tk._setit(selected_file, file))

        def on_select(*args):
            selected_file_label.config(text="Selected File: " + selected_file.get())

        def set_file():
            savefile.value = f'saves/{selected_file.get()}'.encode()
            loadnew.value = True

        # Populate the dropdown menu
        populate_dropdown()

        # Create the dropdown menu
        
        dropdown_menu.pack(padx=10, pady=10)

        # Display the selected file
        selected_file_label = tk.Label(loadwin, text="")
        selected_file_label.pack(pady=10)

        loadButton = tk.Button(loadwin, text="Load Scene", command=set_file)
        loadButton.pack()

        # Bind the selection event
        selected_file.trace_add("write", on_select)

        # Run the Tkinter event loop
        loadwin.mainloop()

    # Object Settings window

    def object_settings():
        objwin = tk.Tk()
        objwin.title("Object Settings")

        objwin.geometry("500x125")

        scale_label = tk.Label(objwin, text="Object Scale:")
        scale_label.grid(row=0,column=0, padx=10)

        scale_slider = tk.Scale(objwin, from_=5, to=200, orient="horizontal", command=on_scale_change)
        scale_slider.grid(row=1,column=0, padx=10, pady=10)

        elasticity_label = tk.Label(objwin, text="Object Elasticity:")
        elasticity_label.grid(row=0,column=1, padx=10)

        elasticity_slider = tk.Scale(objwin, from_=0, to=2, orient="horizontal", command=on_elasticity_change, resolution=0.1)
        elasticity_slider.grid(row=1,column=1, padx=10, pady=10)

        roughness_label = tk.Label(objwin, text="Object Roughness:")
        roughness_label.grid(row=0,column=2, padx=10)

        roughness_slider = tk.Scale(objwin, from_=0, to=1, orient="horizontal", command=on_roughness_change, resolution=0.1)
        roughness_slider.grid(row=1,column=2, padx=10, pady=10)

        staticButton = tk.Button(objwin, text="Toggle Frozen", command=set_static)
        staticButton.grid(row=2, column=0, padx=10, pady=10)

        spawnButton = tk.Button(objwin, text="Spawn Object", command=spawn)
        spawnButton.grid(row=2, column=1, padx=10, pady=10)

        delButton = tk.Button(objwin, text="Remove All Objects", command=removeall)
        delButton.grid(row=2, column=2, padx=10, pady=10)

        scale_slider.set(scale.value)
        elasticity_slider.set(elasticity.value)
        roughness_slider.set(roughness.value)


        objwin.mainloop()

    def spring_settings():

        def change_stiff(val):
            spr_stiff.value = float(val)

        def change_len(val):
            spr_len.value = float(val)

        springwin = tk.Tk()
        springwin.title("Spring Settings")

        springwin.geometry("500x125")

        spring_len_label = tk.Label(springwin, text="Length:")
        spring_len_label.grid(row=0,column=0, padx=10)

        spring_len_slider = tk.Scale(springwin, from_=20, to=100, orient="horizontal", command=change_len, resolution=1)
        spring_len_slider.grid(row=1,column=0, padx=10, pady=10)

        spring_stiffness_label = tk.Label(springwin, text="Stiffness:")
        spring_stiffness_label.grid(row=0,column=1, padx=10)

        spring_stiffness_slider = tk.Scale(springwin, from_=0, to=10, orient="horizontal", command=change_stiff, resolution=0.1)
        spring_stiffness_slider.grid(row=1,column=1, padx=10, pady=10)

        spring_len_slider.set(spr_len.value)
        spring_stiffness_slider.set(spr_stiff.value)
        
        springwin.mainloop()

    win = tk.Tk()
    win.title("Physics Engine Settings")
    win.geometry("500x175")

    # World Settings

    gravity_label = tk.Label(text="World Gravity:")
    gravity_label.grid(row=0,column=0, padx=10)

    gravity_slider = tk.Scale(win, from_=0, to=981, orient="horizontal", command=on_g_change)
    gravity_slider.grid(row=1,column=0, padx=10, pady=10)

    timescale_label = tk.Label(text="Timescale:")
    timescale_label.grid(row=0,column=1, padx=10)

    timescale_slider = tk.Scale(win, from_=0, to=10, orient="horizontal", command=on_timescale_change, resolution=0.1)
    timescale_slider.grid(row=1,column=1, padx=10, pady=10)

    resetButton = tk.Button(text="Reset", command=reset)
    resetButton.grid(row=2, column=0, padx=10, pady=10)

    detailButton = tk.Button(text="Toggle Detail View", command=detail_view_update)
    detailButton.grid(row=2, column=1, padx=10, pady=10)

    loadButton = tk.Button(text="Load Scene", command=load_save)
    loadButton.grid(row=2, column=2, padx=10, pady=10)

    loadButton = tk.Button(text="Object Settings", command=object_settings)
    loadButton.grid(row=2, column=3, padx=10, pady=10)

    loadButton = tk.Button(text="Spring Settings", command=spring_settings)
    loadButton.grid(row=3, column=0, padx=10, pady=10)

    gravity_slider.set(Kg.value)
    timescale_slider.set(timescale.value)


    win.mainloop()

if __name__ == "__main__":
    default_scene = "saves/springs.json"

    # Encode the default scene string to bytes
    encoded_default_scene = default_scene.encode()

    # Create a shared array to store the encoded string
    savefile = mp.Array('c', encoded_default_scene)

    reset_event = mp.Value('b', False)
    detail_view = mp.Value('b', False)
    spawn_event = mp.Value('b', False)
    loadnew = mp.Value('b', False)
    timescale = mp.Value('f', 1)
    spr_stiff = mp.Value('f', 0.1)
    spr_len = mp.Value('f', 60)
    static = mp.Value('b', False)
    reset_objs_event = mp.Value('b', False)
    Kg = mp.Value('f', 981)
    scale = mp.Value('f', 100)
    elasticity = mp.Value('f', 0.7)
    roughness = mp.Value('f', 0.2)
    engine_process = mp.Process(target=physics_engine, args=(reset_event,Kg,scale,elasticity,roughness,spawn_event,reset_objs_event,static,timescale,detail_view,savefile,loadnew,spr_stiff,spr_len))
    ui_process = mp.Process(target=settings_ui, args=(reset_event,Kg,scale,elasticity,roughness,spawn_event,reset_objs_event,static,timescale,detail_view,savefile,loadnew,spr_stiff,spr_len))
    engine_process.start()
    ui_process.start()