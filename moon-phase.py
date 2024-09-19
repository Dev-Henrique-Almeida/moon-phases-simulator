import pygame
from pygame.locals import *
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math

# Função para carregar textura globalmente
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

# Classe para gerenciar dados da lua (Estrutura de Dados)
class Moon:
    def __init__(self, texture_path):
        self.texture = load_texture(texture_path)
        self.angle = 0.0  # Ângulo para rotacionar a luz (simulação de fases da lua)

    # Desenhar a esfera texturizada (lua) com base na posição da luz
    def draw(self, light_position):
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        
        # Aplicar iluminação e posição da luz
        glEnable(GL_LIGHTING)
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)

        # Desenhar a lua como uma esfera
        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, 1, 32, 32)
        gluDeleteQuadric(quadric)
        
        glDisable(GL_TEXTURE_2D)

    # Atualizar o ângulo da fase da lua
    def update_angle(self, delta):
        self.angle += delta

# Classe para gerenciar o Sol
class Sun:
    def __init__(self, texture_path):
        self.texture = load_texture(texture_path)
        self.angle = 0.0  # Ângulo de rotação do sol ao redor da lua

    # Desenhar o Sol
    def draw(self):
        glPushMatrix()
        glTranslatef(10 * math.cos(math.radians(self.angle)), 0, 10 * math.sin(math.radians(self.angle)))  # Posicionar o Sol mais distante
        
        # Adicionar luz emissiva para simular o brilho do Sol
        glMaterialfv(GL_FRONT, GL_EMISSION, [1.0, 1.0, 0.0, 1.0])  # Emitir luz amarela

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)

        quadric = gluNewQuadric()
        gluQuadricTexture(quadric, GL_TRUE)
        gluSphere(quadric, 3, 32, 32)  # Desenhar o Sol como uma esfera grande (3x o tamanho da Lua)
        gluDeleteQuadric(quadric)

        glDisable(GL_TEXTURE_2D)

        # Desabilitar luz emissiva após desenhar o Sol
        glMaterialfv(GL_FRONT, GL_EMISSION, [0.0, 0.0, 0.0, 1.0])

        glPopMatrix()

    # Atualizar o ângulo do Sol para a órbita
    def update_angle(self, delta):
        self.angle += delta

# Configurar iluminação
def setup_lighting(light_position):
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])  # Luz branca brilhante para a luz solar
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])  # Reflexão especular
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.1, 0.1, 0.1, 1.0])  # Luz ambiente baixa

# Classe para gerenciar o fundo
class Background:
    def __init__(self, texture_path):
        self.texture = load_texture(texture_path)

    # Desenhar o fundo para sempre preencher a tela
    def draw(self, display_width, display_height):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, display_width, 0, display_height, -1, 1)  # Configurar projeção ortográfica

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # Desabilitar iluminação e teste de profundidade para garantir que o fundo seja desenhado atrás de tudo
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)

        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)

        # Desenhar o quad do fundo para preencher a tela
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(0, 0)  # Inferior esquerdo
        glTexCoord2f(1.0, 0.0)
        glVertex2f(display_width, 0)  # Inferior direito
        glTexCoord2f(1.0, 1.0)
        glVertex2f(display_width, display_height)  # Superior direito
        glTexCoord2f(0.0, 1.0)
        glVertex2f(0, display_height)  # Superior esquerdo
        glEnd()

        glDisable(GL_TEXTURE_2D)

        # Reabilitar iluminação e teste de profundidade para outros objetos
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)

        glMatrixMode(GL_PROJECTION)
        glPopMatrix()

        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

# Simulação 3D principal das fases da lua
def moon_simulation():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    zoom = -8  # Nível de zoom inicial
    angle_x, angle_y = 0.0, 0.0  # Ângulos de rotação
    last_mouse_pos = (0, 0)  # Última posição do mouse
    dragging = False  # Para verificar se o mouse está sendo arrastado
    
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glEnable(GL_DEPTH_TEST)
    
    background = Background('background.png')  # Inicializar o fundo
    moon = Moon('moon.png')  # Inicializar o objeto Lua
    sun = Sun('sun.png')  # Inicializar o objeto Sol com textura

    phase_control = 0.5  # Controle para as fases da lua
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Rolagem para cima
                    zoom += 0.5
                elif event.button == 5:  # Rolagem para baixo
                    zoom -= 0.5
                elif event.button == 1:  # Botão esquerdo do mouse
                    last_mouse_pos = pygame.mouse.get_pos()
                    dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Botão esquerdo do mouse
                    dragging = False

            # Verificar se uma tecla foi pressionada
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    phase_control = 0  # Lua Nova
                elif event.key == pygame.K_2:
                    phase_control = 90  # Quarto Crescente
                elif event.key == pygame.K_3:
                    phase_control = 180  # Lua Cheia
                elif event.key == pygame.K_4:
                    phase_control = 270  # Quarto Minguante

        if dragging:
            current_mouse_pos = pygame.mouse.get_pos()
            dx, dy = current_mouse_pos[0] - last_mouse_pos[0], current_mouse_pos[1] - last_mouse_pos[1]
            angle_x += dy * 0.1
            angle_y += dx * 0.1
            last_mouse_pos = current_mouse_pos

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Desenhar o fundo (tela cheia em projeção ortográfica)
        background.draw(display[0], display[1])

        # Atualizar a matriz de projeção para o zoom
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)  # Redefinir matriz de projeção
        glTranslatef(0.0, 0.0, zoom)  # Aplicar zoom

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Aplicar rotação da câmera
        glRotatef(angle_x, 1, 0, 0)  # Rotacionar em torno do eixo x
        glRotatef(angle_y, 0, 1, 0)  # Rotacionar em torno do eixo y

        # Configurar iluminação a partir da posição do Sol, ajustada com phase_control
        light_position = [5 * math.cos(math.radians(phase_control)), 0.0, 5 * math.sin(math.radians(phase_control)), 1.0]
        setup_lighting(light_position)

        # Desenhar o Sol
        sun.draw()

        # Desenhar a lua com a posição da luz
        glPushMatrix()
        moon.draw(light_position)  # Agora passamos light_position corretamente
        glPopMatrix()

        pygame.display.flip()
        pygame.time.wait(10)



if __name__ == "__main__":
    moon_simulation()