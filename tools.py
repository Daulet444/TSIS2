# tools.py
import pygame
import math
from collections import deque

class DrawingTools:
    def __init__(self, canvas):
        self.canvas = canvas
        self.current_tool = None
        self.start_pos = None
        self.current_color = None
        self.brush_size = None
        
    def start_drawing(self, pos, tool, color, brush_size):
        self.current_tool = tool
        self.start_pos = pos
        self.current_color = color
        self.brush_size = brush_size
        
    def finish_drawing(self, end_pos):
        if self.start_pos and self.current_tool:
            if self.current_tool == "line":
                self.draw_line(self.start_pos, end_pos)
            elif self.current_tool == "rectangle":
                self.draw_rectangle(self.start_pos, end_pos)
            elif self.current_tool == "circle":
                self.draw_circle(self.start_pos, end_pos)
            elif self.current_tool == "square":
                self.draw_square(self.start_pos, end_pos)
            elif self.current_tool == "right_triangle":
                self.draw_right_triangle(self.start_pos, end_pos)
            elif self.current_tool == "equilateral_triangle":
                self.draw_equilateral_triangle(self.start_pos, end_pos)
            elif self.current_tool == "rhombus":
                self.draw_rhombus(self.start_pos, end_pos)
                
    def draw_pencil(self, current_pos, last_pos):
        if last_pos:
            pygame.draw.line(self.canvas, self.current_color, last_pos, current_pos, self.brush_size)
        else:
            pygame.draw.circle(self.canvas, self.current_color, current_pos, self.brush_size // 2)
            
    def draw_line(self, start, end):
        pygame.draw.line(self.canvas, self.current_color, start, end, self.brush_size)
        
    def draw_rectangle(self, start, end):
        rect = pygame.Rect(start, (end[0] - start[0], end[1] - start[1]))
        pygame.draw.rect(self.canvas, self.current_color, rect, self.brush_size)
        
    def draw_circle(self, center, point):
        radius = int(math.hypot(point[0] - center[0], point[1] - center[1]))
        pygame.draw.circle(self.canvas, self.current_color, center, radius, self.brush_size)
        
    def draw_square(self, start, end):
        size = max(abs(end[0] - start[0]), abs(end[1] - start[1]))
        rect = pygame.Rect(start[0] - size//2, start[1] - size//2, size, size)
        pygame.draw.rect(self.canvas, self.current_color, rect, self.brush_size)
        
    def draw_right_triangle(self, start, end):
        points = [start, (end[0], start[1]), (start[0], end[1])]
        pygame.draw.polygon(self.canvas, self.current_color, points, self.brush_size)
        
    def draw_equilateral_triangle(self, start, end):
        height = end[1] - start[1]
        half_width = height * math.tan(math.radians(30))
        points = [start,
                 (start[0] - half_width, start[1] + height),
                 (start[0] + half_width, start[1] + height)]
        pygame.draw.polygon(self.canvas, self.current_color, points, self.brush_size)
        
    def draw_rhombus(self, start, end):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        points = [start,
                 (start[0] + dx//2, start[1] - abs(dy)//2),
                 (start[0] + dx, start[1]),
                 (start[0] + dx//2, start[1] + abs(dy)//2)]
        pygame.draw.polygon(self.canvas, self.current_color, points, self.brush_size)
        
    def draw_eraser(self, pos):
        pygame.draw.circle(self.canvas, (255, 255, 255), pos, self.brush_size // 2)

class FloodFill:
    def __init__(self, canvas):
        self.canvas = canvas
        
    def flood_fill(self, pos, new_color):
        """Flood fill algorithm using queue (BFS)"""
        try:
            # Get the color at the clicked position
            target_color = self.canvas.get_at(pos)[:3]  # Get RGB only, ignore alpha
            
            # If target color is the same as new color, don't do anything
            if target_color == new_color:
                return
                
            # Use a queue for BFS
            queue = deque()
            queue.append(pos)
            
            # Keep track of visited positions to avoid infinite loops
            visited = set()
            visited.add(pos)
            
            # Get canvas dimensions
            width, height = self.canvas.get_size()
            
            while queue:
                x, y = queue.popleft()
                
                # Set the new color
                self.canvas.set_at((x, y), new_color)
                
                # Check neighboring pixels (4-directional)
                neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
                
                for nx, ny in neighbors:
                    if 0 <= nx < width and 0 <= ny < height:
                        if (nx, ny) not in visited:
                            # Check if the neighbor has the target color
                            neighbor_color = self.canvas.get_at((nx, ny))[:3]
                            if neighbor_color == target_color:
                                visited.add((nx, ny))
                                queue.append((nx, ny))
                                
        except Exception as e:
            print(f"Flood fill error: {e}")

class TextTool:
    def __init__(self, canvas):
        self.canvas = canvas
        self.active = False
        self.position = None
        self.text = ""
        self.font = pygame.font.Font(None, 36)
        self.preview_surface = None
        
    def activate(self, pos):
        if not self.active:
            self.active = True
            self.position = pos
            self.text = ""
            self.preview_surface = self.canvas.copy()
            
    def add_char(self, char):
        if char and char.isprintable():
            self.text += char
            
    def backspace(self):
        self.text = self.text[:-1]
        
    def confirm(self):
        if self.position and self.text:
            text_surface = self.font.render(self.text, True, (0, 0, 0))
            self.canvas.blit(text_surface, self.position)
            return True
        return False
        
    def cancel(self):
        self.active = False
        self.position = None
        self.text = ""
        self.preview_surface = None
        
    def draw_preview(self, screen):
        if self.active and self.position:
            # Draw cursor
            cursor_pos = (self.position[0] + self.font.size(self.text)[0], self.position[1])
            pygame.draw.line(screen, (0, 0, 0), cursor_pos, 
                           (cursor_pos[0], cursor_pos[1] + self.font.get_height()), 2)
            
            # Draw text preview
            text_surface = self.font.render(self.text + "|", True, (0, 0, 0))
            screen.blit(text_surface, self.position)

class ToolManager:
    def __init__(self, canvas):
        self.canvas = canvas
        self.drawing_tools = DrawingTools(canvas)
        self.flood_fill = FloodFill(canvas)
        self.text_tool = TextTool(canvas)