# Pygame Physics Engine 3.0

**About the Project:**

This is the third of the pygamed based physics engines I have made which now includes many new features, including a new object grabbing system, more in-depth collisions, and more interactivity.

**Usage:**

- When run, the python script will show two windows one of which is a settings window using the tkinter library, and the other is the physics engine viewport where you can see the output of the physics engine, this window is using the pygame library and is run asynchronously with the settings window.
- **Keybinds**
    - *Left Mouse Button (LMB)*: When hovering an object, pressing LMB allows you to grab the object and move it around the scene unless the object is frozen.
    - *Right Mouse Button (RMB)*: When hovering an object and pressing RMB you will select the object and then can change it's properties which will then by applied on the next scene reset.
    - *F*: When holding the F key objects will have a force applied on them away from the mouse cursor's position
    - *S*: Connects two objects (Selected Object and Secondary Selected Object) with a spring
    - *LeftShift*: When holding the LeftShift key you are able to use RMB to Secondary Select an object, to deselect hold LeftShift and either click on another object or somewhere else in the viewport with RMB
- **Settings UI**
    - *World Gravity Slider*: This slider is used to adjust the simulation-wide gravity variable which can make objects fall faster, slower, or not at all.
    - *Object Scale Slider*: Adjusts an object's scale when an object is selected or, if no object is selected will adjust the scale of the next object that is spawned
    - *Object Elasticity Slider*: Adjusts an object's elasticity when an object is selected or, if no object is selected will adjust the elasticity of the next object that is spawned. An object's elasticity can affect how energy is transferred between objects in the case of a collision.
    - *Object Roughness Slider*: Adjusts an object's roughness when an object is selected or, if no object is selected will adjust the roughness of the next object that is spawned. An objects roughness controlls its friction, which will cause it to lose momentum while sliding over the ground, ceiling, or other objects.
    - *Toggle Frozen Button*: Toggles the frozen state of the selected object. When an object is frozen it will turn blue, and not be affected by any action that adds velocity to it, such as moving the object with the cursor, or a collision with another object.
    - *Spawn Object button*: Spawns a new object in the center of the screen with values specefied in the settings menu, or preset values if another object is selected.
    - *Remove All Objects Button*: Removes all objects currently present in the scene.
    - *Reset Button*: Resets all objects to their default positions, while not deleting the objects.


**Objects:**
- *RigidBody*: This is an object that has physics applied to it, such as gravity and collision with other physics objects.
- *Spring*: This is an object that takes in two objects, and moves the second object, toward the first.