import pygame
from pygame.locals import *
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

def load_texture(image_path):
    texture_surface = pygame.image.load(image_path).convert_alpha()
    texture_data = pygame.image.tostring(texture_surface, "RGBA", 1)
    width, height = texture_surface.get_rect().size

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    return texture_id

class Earth:
    def __init__(self, texture_path):
        self.texture = load_texture(texture_path)
        self.angle = 0.0

    def draw(self):
        glPushMatrix()
        glTranslatef(10 * math.cos(math.radians(self.angle)), 0, 10 * math.sin(math.radians(self.angle)))
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, 2, 32, 32)
        gluDeleteQuadric(quadric)
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()

    def update_angle(self, delta):
        self.angle += delta

class Moon:
    def __init__(self, texture_path):
        self.texture = load_texture(texture_path)
        self.angle = 0.0

    def draw(self, earth_x, earth_z):
        glPushMatrix()
        glTranslatef(earth_x + 5 * math.cos(math.radians(self.angle)), 0, earth_z + 5 * math.sin(math.radians(self.angle)))
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, 1, 32, 32)
        gluDeleteQuadric(quadric)
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()

    def update_angle(self, delta):
        self.angle += delta

class Sun:
    def __init__(self, texture_path):
        self.texture = load_texture(texture_path)

    def draw(self):
        glPushMatrix()
        glTranslatef(0, 0, 0)
        glMaterialfv(GL_FRONT, GL_EMISSION, [1.0, 1.0, 0.0, 1.0])
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, 3, 32, 32)
        gluDeleteQuadric(quadric)
        glDisable(GL_TEXTURE_2D)
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])
        glPopMatrix()

def setup_lighting(light_position):
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.1, 0.1, 0.1, 1.0])

class Background:
    def __init__(self, texture_path):
        self.texture = load_texture(texture_path)

    def draw(self, display_width, display_height):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, display_width, 0, display_height, -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(0, 0)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(display_width, 0)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(display_width, display_height)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(0, display_height)
        glEnd()
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

def moon_simulation():
    pygame.init()
    display = (1600, 800)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    zoom = -28
    angle_x, angle_y = 0.0, 0.0
    last_mouse_pos = (0, 0)
    dragging = False
    phase_control = None
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glEnable(GL_DEPTH_TEST)
    background = Background('images/background.png')
    moon = Moon('images/moon.png')
    earth = Earth('images/earth.png')
    sun = Sun('images/sun.png')

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    zoom += 0.5
                elif event.button == 5:
                    zoom -= 0.5
                elif event.button == 1:
                    last_mouse_pos = pygame.mouse.get_pos()
                    dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    phase_control = 0
                elif event.key == pygame.K_2:
                    phase_control = 90
                elif event.key == pygame.K_3:
                    phase_control = 180
                elif event.key == pygame.K_4:
                    phase_control = 270
                elif event.key == pygame.K_5:
                    phase_control = None

        if dragging:
            current_mouse_pos = pygame.mouse.get_pos()
            dx, dy = current_mouse_pos[0] - last_mouse_pos[0], current_mouse_pos[1] - last_mouse_pos[1]
            angle_x += dy * 0.1
            angle_y += dx * 0.1
            last_mouse_pos = current_mouse_pos

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        background.draw(display[0], display[1])
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
        glTranslatef(0.0, 0.0, zoom)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glRotatef(angle_x, 1, 0, 0)
        glRotatef(angle_y, 0, 1, 0)
        light_position = [0.0, 0.0, 0.0, 1.0]
        setup_lighting(light_position)
        sun.draw()
        earth.update_angle(0.1)
        earth_x = 10 * math.cos(math.radians(earth.angle))
        earth_z = 10 * math.sin(math.radians(earth.angle))
        earth.draw()
        if phase_control is None:
            moon.update_angle(0.3)
        else:
            moon.angle = phase_control
        moon.draw(earth_x, earth_z)
        pygame.display.flip()
        pygame.time.wait(10)

moon_simulation()
