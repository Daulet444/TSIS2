# paint.py
import pygame
import sys
import math
from datetime import datetime
from tools import ToolManager, DrawingTools, FloodFill, TextTool

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
CANVAS_WIDTH = 900
CANVAS_HEIGHT = 600
TOOLBAR_WIDTH = 300
COLOR_BOX_SIZE = 30
BRUSH_SIZES = {pygame.K_1: 2, pygame.K_2: 5, pygame.K_3: 10}
BRUSH_SIZE_BUTTONS = {1: 2, 2: 5, 3: 10}

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (150, 150, 150)
LIGHT_GRAY = (220, 220, 220)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

COLORS = [BLACK, WHITE, RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, ORANGE, PURPLE]

class Button:
    def __init__(self, x, y, width, height, text, color, action=None, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.action = action
        self.text_color = text_color
        self.hovered = False
        
    def draw(self, screen, font):
        color = self.color if not self.hovered else tuple(min(255, c + 30) for c in self.color)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.action:
                return self.action()
        return None

class PaintApp:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Advanced Paint Application")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Create canvas surface
        self.canvas = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
        self.canvas.fill(WHITE)
        
        # Initialize tools
        self.tool_manager = ToolManager(self.canvas)
        self.drawing_tools = DrawingTools(self.canvas)
        self.flood_fill = FloodFill(self.canvas)
        self.text_tool = TextTool(self.canvas)
        
        self.current_tool = "pencil"
        self.current_color = BLACK
        self.brush_size = 5  # medium by default
        
        # Drawing state
        self.drawing = False
        self.start_pos = None
        self.last_pos = None
        self.preview_surface = None
        
        # UI Elements
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 32)
        self.buttons = []
        self.tool_buttons = {}
        self.color_rects = []
        self.brush_buttons = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        # Tool buttons
        tools = [
            ("✏️ Pencil", "pencil", 10, 10),
            ("📏 Line", "line", 10, 50),
            ("📦 Rectangle", "rectangle", 10, 90),
            ("⬤ Circle", "circle", 10, 130),
            ("⬛ Square", "square", 10, 170),
            ("📐 Triangle", "right_triangle", 10, 210),
            ("🔺 Eq Triangle", "equilateral_triangle", 10, 250),
            ("🔶 Rhombus", "rhombus", 10, 290),
            ("🪣 Fill", "fill", 10, 330),
            ("📝 Text", "text", 10, 370),
            ("🧽 Eraser", "eraser", 10, 410),
        ]
        
        for text, tool, x, y in tools:
            btn = Button(x, y, 120, 30, text, LIGHT_GRAY, lambda t=tool: self.set_tool(t))
            self.tool_buttons[tool] = btn
            self.buttons.append(btn)
        
        # Brush size buttons
        brush_sizes = [(1, 2, "Small"), (2, 5, "Medium"), (3, 10, "Large")]
        for key, size, label in brush_sizes:
            btn = Button(10, 460 + (key-1)*35, 120, 30, f"{label} ({size}px)", LIGHT_GRAY, 
                        lambda s=size: self.set_brush_size(s))
            self.brush_buttons[size] = btn
            self.buttons.append(btn)
        
        # Save button
        save_btn = Button(10, 570, 120, 40, "💾 Save (Ctrl+S)", GREEN, self.save_canvas)
        self.buttons.append(save_btn)
        
        # Clear button
        clear_btn = Button(150, 570, 120, 40, "🗑️ Clear", RED, self.clear_canvas)
        self.buttons.append(clear_btn)
        
        # Color selection
        for i, color in enumerate(COLORS):
            rect = pygame.Rect(CANVAS_WIDTH + 10 + (i % 2) * 35, 
                             460 + (i // 2) * 35, 30, 30)
            self.color_rects.append((rect, color))
        
        # Current color display
        self.current_color_rect = pygame.Rect(CANVAS_WIDTH + 10, 10, 60, 60)
        
        # Brush size indicator
        self.brush_indicator_rect = pygame.Rect(CANVAS_WIDTH + 80, 10, 60, 60)
        
    def set_tool(self, tool):
        self.current_tool = tool
        if tool == "text":
            self.text_tool.active = False
        
    def set_brush_size(self, size):
        self.brush_size = size
        
    def save_canvas(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"canvas_{timestamp}.png"
        pygame.image.save(self.canvas, filename)
        print(f"Canvas saved as {filename}")
        
    def clear_canvas(self):
        self.canvas.fill(WHITE)
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            # Keyboard shortcuts
            elif event.type == pygame.KEYDOWN:
                if event.mod & pygame.KMOD_CTRL and event.key == pygame.K_s:
                    self.save_canvas()
                elif event.key in BRUSH_SIZES:
                    self.set_brush_size(BRUSH_SIZES[event.key])
                elif event.key == pygame.K_ESCAPE and self.current_tool == "text":
                    self.text_tool.cancel()
                elif event.key == pygame.K_RETURN and self.current_tool == "text":
                    if self.text_tool.confirm():
                        self.text_tool.active = False
                elif self.current_tool == "text" and self.text_tool.active:
                    if event.key == pygame.K_BACKSPACE:
                        self.text_tool.backspace()
                    else:
                        self.text_tool.add_char(event.unicode)
                        
            # Mouse events
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                
                # Check if click is on canvas
                if pos[0] < CANVAS_WIDTH and pos[1] < CANVAS_HEIGHT:
                    if self.current_tool == "fill":
                        self.flood_fill.flood_fill(pos, self.current_color)
                    elif self.current_tool == "text":
                        self.text_tool.activate(pos)
                    elif self.current_tool == "eraser":
                        self.drawing = True
                        self.start_pos = pos
                        self.last_pos = pos
                        self.drawing_tools.start_drawing(pos, self.current_tool, self.current_color, self.brush_size)
                    else:
                        self.drawing = True
                        self.start_pos = pos
                        self.last_pos = pos
                        self.drawing_tools.start_drawing(pos, self.current_tool, self.current_color, self.brush_size)
                else:
                    # Check UI buttons
                    for button in self.buttons:
                        button.handle_event(event)
                    
                    # Check color selection
                    for rect, color in self.color_rects:
                        if rect.collidepoint(pos):
                            self.current_color = color
                            
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.drawing:
                    end_pos = pygame.mouse.get_pos()
                    if end_pos[0] < CANVAS_WIDTH and end_pos[1] < CANVAS_HEIGHT:
                        self.drawing_tools.finish_drawing(end_pos)
                    self.drawing = False
                    self.start_pos = None
                    self.last_pos = None
                    
            elif event.type == pygame.MOUSEMOTION:
                if self.drawing:
                    current_pos = pygame.mouse.get_pos()
                    if current_pos[0] < CANVAS_WIDTH and current_pos[1] < CANVAS_HEIGHT:
                        if self.current_tool == "pencil":
                            self.drawing_tools.draw_pencil(current_pos, self.last_pos)
                        elif self.current_tool == "eraser":
                            self.drawing_tools.draw_pencil(current_pos, self.last_pos)
                        elif self.current_tool in ["line", "rectangle", "circle", "square", 
                                                   "right_triangle", "equilateral_triangle", "rhombus"]:
                            self.preview_shape(current_pos)
                        self.last_pos = current_pos
                        
    def preview_shape(self, current_pos):
        # Create a preview surface
        preview = self.canvas.copy()
        if self.start_pos:
            if self.current_tool == "line":
                pygame.draw.line(preview, self.current_color, self.start_pos, current_pos, self.brush_size)
            elif self.current_tool == "rectangle":
                rect = pygame.Rect(self.start_pos, (current_pos[0] - self.start_pos[0], 
                                                   current_pos[1] - self.start_pos[1]))
                pygame.draw.rect(preview, self.current_color, rect, self.brush_size)
            elif self.current_tool == "circle":
                radius = int(math.hypot(current_pos[0] - self.start_pos[0], 
                                       current_pos[1] - self.start_pos[1]))
                pygame.draw.circle(preview, self.current_color, self.start_pos, radius, self.brush_size)
            elif self.current_tool == "square":
                size = max(abs(current_pos[0] - self.start_pos[0]), 
                          abs(current_pos[1] - self.start_pos[1]))
                rect = pygame.Rect(self.start_pos[0] - size//2, self.start_pos[1] - size//2, size, size)
                pygame.draw.rect(preview, self.current_color, rect, self.brush_size)
            elif self.current_tool == "right_triangle":
                points = [self.start_pos, 
                         (current_pos[0], self.start_pos[1]),
                         (self.start_pos[0], current_pos[1])]
                pygame.draw.polygon(preview, self.current_color, points, self.brush_size)
            elif self.current_tool == "equilateral_triangle":
                height = current_pos[1] - self.start_pos[1]
                half_width = height * math.tan(math.radians(30))
                points = [self.start_pos,
                         (self.start_pos[0] - half_width, self.start_pos[1] + height),
                         (self.start_pos[0] + half_width, self.start_pos[1] + height)]
                pygame.draw.polygon(preview, self.current_color, points, self.brush_size)
            elif self.current_tool == "rhombus":
                dx = current_pos[0] - self.start_pos[0]
                dy = current_pos[1] - self.start_pos[1]
                points = [self.start_pos,
                         (self.start_pos[0] + dx//2, self.start_pos[1] - abs(dy)//2),
                         (self.start_pos[0] + dx, self.start_pos[1]),
                         (self.start_pos[0] + dx//2, self.start_pos[1] + abs(dy)//2)]
                pygame.draw.polygon(preview, self.current_color, points, self.brush_size)
        
        self.screen.blit(preview, (0, 0))
        self.draw_ui()
        pygame.display.flip()
        
    def draw_ui(self):
        # Draw toolbar background
        pygame.draw.rect(self.screen, GRAY, (CANVAS_WIDTH, 0, TOOLBAR_WIDTH, SCREEN_HEIGHT))
        pygame.draw.line(self.screen, BLACK, (CANVAS_WIDTH, 0), (CANVAS_WIDTH, SCREEN_HEIGHT), 3)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen, self.font)
        
        # Draw color palette
        for rect, color in self.color_rects:
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)
        
        # Draw current color
        pygame.draw.rect(self.screen, self.current_color, self.current_color_rect)
        pygame.draw.rect(self.screen, BLACK, self.current_color_rect, 3)
        color_text = self.font.render("Current", True, BLACK)
        self.screen.blit(color_text, (CANVAS_WIDTH + 10, 75))
        
        # Draw brush size indicator
        pygame.draw.circle(self.screen, self.current_color, 
                          (CANVAS_WIDTH + 110, 40), self.brush_size)
        pygame.draw.circle(self.screen, BLACK, 
                          (CANVAS_WIDTH + 110, 40), self.brush_size, 1)
        size_text = self.font.render(f"Size: {self.brush_size}px", True, BLACK)
        self.screen.blit(size_text, (CANVAS_WIDTH + 80, 75))
        
        # Draw current tool
        tool_text = self.font.render(f"Tool: {self.current_tool}", True, BLACK)
        self.screen.blit(tool_text, (CANVAS_WIDTH + 10, 130))
        
        # Draw text input indicator if text tool is active
        if self.current_tool == "text" and self.text_tool.active:
            self.text_tool.draw_preview(self.screen)
            
    def run(self):
        while self.running:
            self.handle_events()
            
            # Draw canvas
            self.screen.blit(self.canvas, (0, 0))
            
            # Draw UI
            self.draw_ui()
            
            # Draw shape preview
            if self.drawing and self.start_pos and self.current_tool in ["line", "rectangle", "circle", 
                                                                        "square", "right_triangle", 
                                                                        "equilateral_triangle", "rhombus"]:
                self.preview_shape(pygame.mouse.get_pos())
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = PaintApp()
    app.run()