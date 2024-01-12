import os, sys, win32api, win32con, re

import pygame as pg
import requests as req

from math import *
from io import BytesIO

class Origin:
    TOP_LEFT = (0, 0)
    TOP_CENTER = (1, 0)
    TOP_RIGHT = (2, 0)
    MIDDLE_LEFT = (0, 1)
    MIDDLE_CENTER = (1, 1)
    MIDDLE_RIGHT = (2, 1)
    BOTTOM_LEFT = (0, 2)
    BOTTOM_CENTER = (1, 2)
    BOTTOM_RIGHT = (2, 2)

class Color:

#region Colors
    auto = (0, 0, 0, 0)

    black = (0, 0, 0)
    white = (255, 255, 255)
    gray = (75, 75, 75)

    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    magenta = (255, 0, 255)
    yellow = (255, 255, 0)
    cyan = (0, 255, 255)

    orange = (255, 100, 25)
    dk_orange = (150, 60, 15)
    lt_orange = (255, 170, 115)

    pink = (255, 185, 255)
    dk_pink = (175, 120, 175)
    lt_pink = (255, 220, 255)

    dk_gray = (25, 25, 25)
    dk_red = (75, 0, 0)
    dk_green = (0, 75, 0)
    dk_blue = (0, 0, 75)

    lt_orange = (230, 166, 115)
    lt_cyan = (185, 255, 255)
    lt_gray = (125, 125, 125)
    purple = (128, 0, 128)


    lt_purple = (180, 120, 180)
    dk_purple = (80, 0, 80)

    brown = (139, 69, 19)
    lt_brown = (205, 133, 63)
    dk_brown = (101, 67, 33)

    olive = (128, 128, 0)
    lt_olive = (194, 190, 110)
    dk_olive = (64, 64, 0)

    teal = (0, 128, 128)
    lt_teal = (120, 190, 200)
    dk_teal = (0, 80, 80)

    maroon = (128, 0, 0)
    lt_maroon = (200, 120, 120)
    dk_maroon = (80, 0, 0)

    navy = (0, 0, 128)
    lt_navy = (120, 120, 200)
    dk_navy = (0, 0, 80)

    lavender = (230, 230, 250)
    lt_lavender = (240, 240, 255)
    dk_lavender = (220, 220, 240)

    gold = (255, 215, 0)
    lt_gold = (255, 235, 110)
    dk_gold = (205, 173, 0)

    coral = (255, 127, 80)
    lt_coral = (255, 165, 130)
    dk_coral = (205, 102, 77)

    indigo = (75, 0, 130)
    lt_indigo = (120, 60, 200)
    dk_indigo = (25, 0, 100)
#endregion

    def Mix(color1, color2):
        return ((color1[0] + color2[0])/2, (color1[1] + color2[1])/2, (color1[2] + color2[2])/2)
    
    def Add(color1, color2):
        color = [(color1[0] + color2[0]), (color1[1] + color2[1]), (color1[2] + color2[2])]
        for i, x in enumerate(color):
            if x > 255: color[i] = 255
            elif x <0: color[i] = 0
        return (color[0], color[1], color[2])

    def Desaturate(color, percent:float=.5):
        gray = sum(color) / 3
        color = [color[0] * (1-percent) + gray * percent, color[1] * (1-percent) + gray * percent, color[2] * (1-percent) + gray * percent]
        for i, x in enumerate(color):
            if x > 255: color[i] = 255
            elif x <0: color[i] = 0
        return (color[0], color[1], color[2])
    
    def Lighten(color, percent: float = 0.5):
        color = [int(color[0] + 255 * percent), int(color[1] + 255 * percent), int(color[2] + 255 * percent)]
        for i, x in enumerate(color):
            if x > 255: color[i] = 255
            elif x <0: color[i] = 0
        return (color[0], color[1], color[2])

class DigObj:
    def __init__(self, color:Color=Color.gray, alt_colors:list[Color]=[Color.lt_gray, Color.dk_gray], scale:float=1.0, coords:tuple[int, int]=(10, 10),
                 origin:Origin=(-1, -1), origin_adjust:Origin=(0, 0), text:str="Object", size:tuple[int, int]=(0, 0)) -> None:
        #public
        self.size = size
        self.coords = coords
        self.text = text
        self.origin = origin
        self.origin_adjust = origin_adjust
        self.scale = scale
        #private
        self._engine = None
        #hidden
        self.__display_color = color
        self.__origin_color = color
        self.__alt_colors = alt_colors
        self.__bounds = (self.coords[0], self.coords[1], self.coords[0]+self.size[0], self.coords[1]+self.size[1])
        self.__hover = False
        
    def _update_bounds(self):
        self.__bounds = (self.coords[0], self.coords[1], self.coords[0]+self.size[0], self.coords[1]+self.size[1])
        
    def SetSize(self, size:tuple[int, int]):
        self.size = size
        self.__bounds = (self.coords[0], self.coords[1], int(self.coords[0]+(self.size[0] * self.scale)), int(self.coords[1]+(self.size[1] * self.scale)))

class ReqImage:
    def __init__(self, url, coords=(10, 10), origin:Origin=(-1, -1), origin_adjust=(0, 0), scale:float=1) -> None:
        self._image_got = False
        self.url = url
        self.image = None
        self.coords = coords
        self.origin = origin
        self.origin_adjust = origin_adjust
        self.scale = scale
        self.size = (0, 0)

    def _get_image(self):
        try:
            response = req.get(self.url)
            response.raise_for_status()
            image_data = response.content
            image_stream = BytesIO(image_data)
            self.image = pg.image.load(image_stream)
            self.size = (self.image.get_width(), self.image.get_height())
            self.image = pg.transform.smoothscale(self.image, (int(self.size[0] * self.scale), int(self.size[1] * self.scale)))
            self.size = (self.image.get_width(), self.image.get_height())
            self._image_got = True
        except req.exceptions.RequestException as e:
            print(f"Error downloading image: {e}")
            self.image = None

class Image(DigObj):
    def __init__(self, path="", coords=(10, 10), origin=(-1, -1), origin_adjust=(0, 0), scale=1.0, size=(0, 0)):
        super().__init__(coords=coords, origin=origin, origin_adjust=origin_adjust, scale=scale, size=size)
        self.path = path
        self.image = None
        if path != "":
            self._load_image()

    def _load_image(self):
        try:
            self.image = pg.image.load(self.path)
            if self.size == (0, 0):
                self.size = (self.image.get_width(), self.image.get_height())
            self.image = pg.transform.smoothscale(self.image, (int(self.size[0] * self.scale), int(self.size[1] * self.scale)))
        except pg.error as e:
            print(f"Error loading image: {e}")
            self.image = None
        self._update_bounds()
        
class Text(DigObj):
    def __init__(self, text="Text", coords=(10, 10), origin=(-1, -1), origin_adjust=(0, 0), scale=1.0, color=Color.white, outline=False, center=False):
        super().__init__(coords=coords, origin=origin, origin_adjust=origin_adjust, scale=scale)
        pg.font.init()
        self.text = text
        self.font = pg.font.SysFont("Arial", int(28 * scale))  # Set the desired font and size
        self.color = color
        self.image = None
        self.size = None
        self.text_mode = 1
        self.outline=outline
        self.outline_image = None
        self.origin_adjust = origin_adjust
        self.center=center
        if center:
            self._render_text()
            text_rect = self.image.get_rect()
            self.coords = (self.coords[0]-(text_rect.width/2), self.coords[1]-(text_rect.height/2))

    def _render_text(self):
        self.outline_image = self.font.render(self.text, True, Color.black)
        self.image = self.font.render(self.text, True, self.color)
        self.size = self.image.get_size()
        self._update_bounds()
    
class DisplayBox(DigObj):
    def __init__(self, color: Color = Color.gray, alt_colors: list[Color] = [Color.lt_gray, Color.dk_gray], scale: float = 1, coords: tuple[int, int] = (10, 10), origin: Origin = (-1, -1), origin_adjust: Origin = (0, 0), text: Text=Text("Text"), size: tuple[int, int] = (50, 50),
                 display_image:Image=Image(), wrap:bool=False, text_origin:Origin=(0, 1), text_mode=1) -> None:
        super().__init__(color, alt_colors, scale, coords, origin, origin_adjust, size)
        self.image = display_image
        self.textObj = text
        self.text_origin = text_origin
        self.wrap = wrap
        self.image.coords = coords
        self.textObj.coords = coords
        self.textObj.text_mode = text_mode
        if text_mode != 1:
            self.textObj.text_mode = 0
        self.textObj._render_text()
        text_rect = self.textObj.image.get_rect()
        # self.size = (self.image.size[0] + text_rect.width, self.image.size[1] + text_rect.height)
        max_x = max(self.image.coords[0] + self.image.size[0], self.textObj.coords[0] + text_rect.width)
        max_y = max(self.image.coords[1] + self.image.size[1], self.textObj.coords[1] + text_rect.height)
        self.size = (max_x - coords[0], max_y - coords[1])
        self.size_adjusted = False

    def _adjust_size(self):
        self.textObj._render_text()
        text_rect = self.textObj.image.get_rect()
        max_x = max(self.image.coords[0] + self.image.size[0], self.textObj.coords[0] + text_rect.width)
        max_y = max(self.image.coords[1] + self.image.size[1], self.textObj.coords[1] + text_rect.height)
        self.size = (max_x - self.coords[0], max_y - self.coords[1])

    def _update_coordinates(self):
            self.image.coords = self.coords
            self.textObj.coords = self.coords

class Button:
    def __init__(self, toggle_mode=False, color:Color=Color.gray, toggle_color:Color=Color.green,scale:float=1.0, coords:tuple[int, int]=(10, 10), 
                 origin:Origin=(-1, -1), origin_adjust:Origin=(0, 0), text:str="Button") -> None:
        self.size = (150, 35)
        #hidden
        self.__display_color = color
        self.__origin_color = color
        self.__origin_toggle_color = toggle_color
        self.__bounds = (coords[0], coords[1], int(coords[0]+(self.size[0] * scale)), int(coords[1]+(self.size[1] * scale)))
        self.__hover = False
        self.__mouse_set = False
        #private
        self._toggle_mode = toggle_mode
        self._engine = None
        self._scale = scale
        self._text_scale = scale - .25
        #public
        self.text = text
        self.coords = coords
        self.origin = origin
        self.origin_adjust = origin_adjust

    def SetSize(self, size:tuple[int, int]):
        self.size = size
        self.__bounds = (self.coords[0], self.coords[1], int(self.coords[0]+(self.size[0] * self.scale)), int(self.coords[1]+(self.size[1] * self.scale)))
    
    def Manage(self):
        mouse_pos = Engine.GetMouse()
        if mouse_pos[0] >= self.__bounds[0]-1 and mouse_pos[0] <= self.__bounds[2]+1 and mouse_pos[1] >= self.__bounds[1]-1 and mouse_pos[1] <= self.__bounds[3]+1:
            self.__hover = True
        else:
            self.__hover = False
            
    def _update_bounds(self):
        self.__bounds = (self.coords[0], self.coords[1], self.coords[0]+self.size[0], self.coords[1]+self.size[1])
    
    def GetColor(self):
        return self.__display_color

class Cell:
    def __init__(self, interact:bool=False, color=Color.gray, hover_color=Color.Lighten(Color.gray, .3), toggle_colors:list[Color]=[Color.Desaturate(Color.red), 
                Color.Desaturate(Color.blue), Color.Desaturate(Color.green)],origin=(-1, -1), origin_adjust:tuple[int, int]=(0, 0), coords:tuple[int, int]=(10, 10), 
                toggle_modes:int=1, size:tuple[int, int]=(50, 50)) -> None:
        #hidden
        self.__display_color = color
        self.__origin_color = color
        self.__origin_hover_color = hover_color
        self.__origin_toggle_colors = toggle_colors
        self.__bounds = (coords[0], coords[1], coords[0]+size[0], coords[1]+size[1])
        self.__hover = False
        self.__click = False
        self.__toggled = [False, False, False]
        self.__hover_clicked = False
        #private
        self._engine = None
        self._interact = interact
        self._toggle_modes = toggle_modes
        #public
        self.size = size
        self.coords = coords
        self.origin = origin
        self.origin_adjust = origin_adjust
        #modifiers
        if toggle_modes <= 0:
            self._interact = False
            self._toggle_modes = 0
        elif toggle_modes > 3:
            self._interact = True
            toggle_modes = 3
    
    def _update_bounds(self):
        self.__bounds = (self.coords[0], self.coords[1], self.coords[0]+self.size[0], self.coords[1]+self.size[1])
        
    def IsToggled(self):
        if self.__toggled:
            return True
        else:
            return False

    def IsClicked(self):
        if self.__click:
            return True
        else:
            return False
    
    def GetColor(self):
        return self.__display_color

    def SetColors(self, color=None, hover_color=None, toggle_colors:list[Color]=None):
        if not color == None:
            self.__origin_color = color
        if not hover_color == None:
            self.__origin_hover_color = hover_color
        if not toggle_colors == None:
            self.__origin_toggle_colors = toggle_colors
    
    def Manage(self):
        for click in ["left_release", "middle_release", "right_release"]:
            if self.__hover_clicked and self._engine.clicks[click]:
                self.__hover_clicked = False
        self.__click = False
        mouse_pos = Engine.GetMouse()
        # MOUSE DETECTION
        if mouse_pos[0] >= self.__bounds[0]+1 and mouse_pos[0] <= self.__bounds[2]-1 and mouse_pos[1] >= self.__bounds[1]+1 and mouse_pos[1] <= self.__bounds[3]-1:
            self.__hover = True
            self.__display_color = self.__origin_hover_color
            for button_name, toggled_index in {"left_click": 0, "right_click": 1, "middle_click": 2, "left_hold":0, "right_hold":1, "middle_hold":2}.items():
                if self._engine.clicks[button_name] and not self.__hover_clicked:
                    self.__hover_clicked = True
                    self.__click = True
                    self.__toggled[toggled_index] = not self.__toggled[toggled_index]
                    for i in range(len(self.__toggled)):
                        if i != toggled_index:
                            self.__toggled[i] = False
        else:
            self.__hover = False
            self.__display_color = self.__origin_color
        
        #TOGGLED
        for i, togglemode in enumerate(self.__toggled):
            if togglemode:
                self.__display_color = self.__origin_toggle_colors[i]
                if self.__hover:
                    self.__display_color = Color.Lighten(self.__origin_toggle_colors[i], .3)

class Engine:
    def __init__(self, caption:str="Dig Game Engine", resolution:tuple[int, int]=(600, 400), resize=False, background:Color=Color.dk_gray, system_memory=False, frameless=False, always_front=False) -> None:
        pg.init()
        self.flags = 0
        if resize:
            self.flags |= pg.RESIZABLE
        if system_memory:
            self.flags |= pg.SWSURFACE
        if frameless:
            self.flags |= pg.NOFRAME
        self.__display = pg.display.set_mode(resolution, self.flags, vsync=1)
        pg.display.set_caption(caption)
        self.__clock = pg.time.Clock()
        self._mouse_position = None
        self._core_resolution = resolution
        self.maxFPS = 60
        self.resolution = resolution
        self.background_color = background
        self.quit = False
        self.fonts = []
        self.clicks = {
            "left_click": False,
            "right_click": False,
            "middle_click": False,
            "left_hold": False,
            "middle_hold": False,
            "right_hold": False,
            "left_release": False,
            "right_release": False,
            "middle_release": False,
            "scroll_up": False,
            "scroll_down": False
        }
        if always_front:
            hwnd = pg.display.get_wm_info()['window']
            import win32con
            import win32gui
            win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        # self.__set_Icon()
        win32api.LoadCursor(0, win32con.IDC_HAND)
    
    def Manage(self) -> None:
        self.__GetEvents()
        self._mouse_position = pg.mouse.get_pos()
        self.__clock.tick(self.maxFPS)
        self.__display.fill(self.background_color)

    def Update(self):
        pg.display.flip()
        pg.display.update()
        if self.quit:
            pg.quit()
        self.__SetAllFalse(dct=self.clicks)

    def AddButton(self, btn:Cell):
        if btn._engine != self:
            btn._engine = self
        if btn.origin != (-1, -1):
            self.SetOrigin(btn)
            btn._update_bounds()
        pg.draw.rect(self.__display, btn.GetColor(),(btn.coords, btn.size))
        pg.draw.rect(self.__display, Color.Desaturate(Color.Lighten(btn.GetColor(), .3), .3),(btn.coords, btn.size), 3)
        pg.font.init()
        font = pg.font.SysFont("Arial", int(28 * btn._text_scale))
        text = font.render(btn.text, True, Color.white)
        text_rect = text.get_rect()
        text_rect.center = (btn.coords[0]+btn.size[0]/2, btn.coords[1]+btn.size[1]/2)
        pg.display.get_surface().blit(text, (text_rect))
        btn.Manage()

    def AddCell(self, cell: Cell):
        if cell._engine != self:
            cell._engine = self
        if cell.origin != (-1, -1):
            self.SetOrigin(cell)
            cell._update_bounds()
        pg.draw.rect(self.__display, cell.GetColor(),(cell.coords, cell.size), 2)
        if cell._interact:
            cell.Manage()

    def MakeRect(self, coords:tuple[int, int], size:tuple[int, int], color:Color=Color.auto, border=False, border_thickness=1):
        if color == Color.auto:
            color = self.background_color
        if border:
            pg.draw.rect(self.__display, color, (coords, size), border_thickness)
        else:
            pg.draw.rect(self.__display, color, (coords, size))

    def MakeStar(self, coords, size, color):
        points = []
        angle = 18
        for _ in range(5):
            x = coords[0] + size * pg.math.Vector2(1, 0).rotate(angle)
            y = coords[1] + size * pg.math.Vector2(0, -1).rotate(angle)
            points.append((x, y))
            angle += 72
        pg.draw.polygon(self.__display, color, points)

    def AddImage(self, image):
        if isinstance(image, ReqImage):
            if image._image_got == False:
                image._get_image()
            if image.origin != (-1, -1):
                self.SetOrigin(image)
            if image.image:
                self.__display.blit(image.image, image.coords)
        elif isinstance(image, Image):
            if image.origin != (-1, -1):
                self.SetOrigin(image)
            if image.image:
                self.__display.blit(image.image, image.coords)
    
    def AddText(self, textObj):
        textObj._render_text()
        if textObj.center:
            textObj._render_text()
            text_rect = textObj.image.get_rect()
            textObj.coords = (textObj.coords[0]-(text_rect.width/2), textObj.coords[1]-(text_rect.height/2))
        if textObj.outline:
            pg.display.get_surface().blit(textObj.outline_image, (textObj.coords[0] - 2, textObj.coords[1] - 2))
            pg.display.get_surface().blit(textObj.outline_image, (textObj.coords[0], textObj.coords[1] - 2))
            pg.display.get_surface().blit(textObj.outline_image, (textObj.coords[0] + 2, textObj.coords[1] - 2))
            pg.display.get_surface().blit(textObj.outline_image, (textObj.coords[0] - 2, textObj.coords[1]))
            pg.display.get_surface().blit(textObj.outline_image, (textObj.coords[0] + 2, textObj.coords[1]))
            pg.display.get_surface().blit(textObj.outline_image, (textObj.coords[0] - 2, textObj.coords[1] + 2))
            pg.display.get_surface().blit(textObj.outline_image, (textObj.coords[0], textObj.coords[1] + 2))
            pg.display.get_surface().blit(textObj.outline_image, (textObj.coords[0] + 2, textObj.coords[1] + 2))
        pg.display.get_surface().blit(textObj.image, textObj.coords)

    def AddDisplay(self, display):
        self.AddImage(display.image)
        display.textObj.coords = self.SetTextOrigin(display.image, display.textObj, display.text_origin)
        self.AddText(display.textObj)
        # self.WrapDraw([display.image])
        if not display.size_adjusted:
            display.size_adjusted = True
            display._adjust_size()
        display._update_coordinates()
        
    def WrapDraw(self, objects, gap=(0, 0), color=Color.white, thickness=2):
        min_x = min(obj.coords[0] for obj in objects)
        min_y = min(obj.coords[1] for obj in objects)
        max_x = max(obj.coords[0] + obj.size[0] for obj in objects)
        max_y = max(obj.coords[1] + obj.size[1] for obj in objects)

        rect_coords = (
            min_x - gap[0],  # Left-most x coordinate
            min_y - gap[1],  # Top-most y coordinate
            max_x - min_x + gap[0] * 2,  # Width
            max_y - min_y + gap[1] * 2  # Height
        )
        pg.draw.rect(self.__display, color, rect_coords, thickness)

    def GetMouse():
        return pg.mouse.get_pos()

    def SetTextOrigin(self, obj, textObj, origin):
        new_coords = (0, 0)
        textObj._render_text()
        text_rect = textObj.image.get_rect()
        match origin[0]:
            case 0:
                if textObj.text_mode == 1:
                    new_coords = (obj.coords[0] + textObj.origin_adjust[0] - text_rect.width, obj.coords[1] + textObj.origin_adjust[1])
                else:
                    new_coords = (obj.coords[0] + textObj.origin_adjust[0], obj.coords[1] + textObj.origin_adjust[1])
            case 1:
                new_coords = (obj.coords[0] + (obj.size[0] / 2) - textObj.origin_adjust[0] - text_rect.width/2, obj.coords[1] + textObj.origin_adjust[1])
            case 2:
                if textObj.text_mode == 1:
                    new_coords = (obj.coords[0] + obj.size[0] - textObj.origin_adjust[0], obj.coords[1] + textObj.origin_adjust[1])
                else:
                    new_coords = (obj.coords[0] + obj.size[0] - textObj.origin_adjust[0] - text_rect.width, obj.coords[1] + textObj.origin_adjust[1])
        match origin[1]:
            case 0:
                new_coords = (new_coords[0], obj.coords[1] + textObj.origin_adjust[1])
            case 1:
                new_coords = (new_coords[0], obj.coords[1] + (obj.size[1] / 2) - textObj.origin_adjust[1] - text_rect.height/2)
            case 2:
                if textObj.text_mode == 1:
                    new_coords = (new_coords[0], obj.coords[1] + obj.size[1] - textObj.origin_adjust[1])
                else:
                    new_coords = (new_coords[0], obj.coords[1] + obj.size[1] - textObj.origin_adjust[1] - text_rect.height)
        match origin:
            case Origin.TOP_CENTER:
                if textObj.text_mode == 1:
                    new_coords = (obj.coords[0] + (obj.size[0] / 2) - textObj.origin_adjust[0] - text_rect.width/2, obj.coords[1] + textObj.origin_adjust[1] - text_rect.height)
            case Origin.BOTTOM_LEFT:
                if textObj.text_mode == 1:
                    new_coords = (obj.coords[0] + textObj.origin_adjust[0] - text_rect.width, obj.coords[1] + obj.size[1] - textObj.origin_adjust[1] - text_rect.height)
            case Origin.BOTTOM_RIGHT:
                if textObj.text_mode == 1:
                    new_coords = (obj.coords[0] + obj.size[0] - textObj.origin_adjust[0], obj.coords[1] + obj.size[1] - textObj.origin_adjust[1] - text_rect.height)
        return new_coords

    def SetOrigin(self, object):
        match object.origin[0]:
            case 0:
                object.coords = (10 + object.origin_adjust[0], object.coords[1] + object.origin_adjust[1])
            case 1:
                object.coords = (self.__display.get_width()/2 - (object.size[0]/2) + object.origin_adjust[0], object.coords[1])
            case 2:
                object.coords = (self.__display.get_width() - object.size[0] - 10 + object.origin_adjust[0], object.coords[1])
        match object.origin[1]:
            case 0:
                object.coords = (object.coords[0], 10 + object.origin_adjust[1])
            case 1:
                object.coords = (object.coords[0], self.__display.get_height()/2 - (object.size[1]/2) + object.origin_adjust[1])
            case 2:
                object.coords = (object.coords[0], self.__display.get_height() - object.size[1] - 10 + object.origin_adjust[1])

    def restart_display(self):
        self.__display = pg.display.set_mode(self.resolution, self.flags, vsync=1)

    def get_display(self):
        return self.__display.get_size()

#region Private Functions
    def __set_Icon(self):
        pg.display.set_icon(pg.image.load(self.__get_resource('icon.ico')))

    def __get_resource(self, filename):
        current_path = ""
        if getattr(sys, 'frozen', False):
            # we are running in a bundle
            current_path = os.path.join(sys._MEIPASS, filename)
            if os.path.exists(current_path):
                return current_path
        else:
            # we are running in a normal Python environment
            # current_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
            # if os.path.exists(current_path):
            #     return current_path
            pass

    def __GetEvents(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit = True
            if event.type == pg.MOUSEBUTTONDOWN:
                match event.button:
                    case 1:
                        self.clicks["left_click"] = True
                    case 2:
                        self.clicks["middle_click"] = True
                    case 3:
                        self.clicks["right_click"] = True
                    case 4:
                        self.clicks["scroll_up"] = True
                    case 5:
                        self.clicks["scroll_down"] = True
            if event.type == pg.MOUSEBUTTONUP:
                match event.button:
                    case 1:
                        self.clicks["left_release"] = True
                    case 2:
                        self.clicks["middle_release"] = True
                    case 3:
                        self.clicks["right_release"] = True
        x = pg.mouse.get_pressed(num_buttons=3)
        if x[0]:
            self.clicks["left_hold"] = True
        if x[1]:
            self.clicks["middle_hold"] = True
        if x[2]:
            self.clicks["right_hold"] = True

#region Set Values
    def __SetAllFalse(self, lst:list[any]=None, dct:dict[any]=None):
        if lst != None:
            print("list")
        elif dct != None:
            [self.__SetFalseKeyValuePair(self.clicks, key) for key in self.clicks]
    
    def __SetFalseKeyValuePair(self, dct, key):
        dct[key] = False

    def __InvertKeyValuePair(self, dct, key):
        dct[key] = not dct[key]

#endregion
#endregion

class Scene:
    
    def __init__(self) -> None:
        pass

# pyinstaller --onefile --noconsole --icon=icon.ico --add-data="icon.ico;." --name="NewName" filename.py
# pyinstaller --onefile --noconsole --icon=icon.ico --add-data="icon.ico;." --name="PoE Stasher" main.py