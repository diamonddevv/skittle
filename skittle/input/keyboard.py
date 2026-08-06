import pygame
import skittle

def keys_down() -> pygame.key.ScancodeWrapper:
    return pygame.key.get_pressed()

def keys_click() -> pygame.key.ScancodeWrapper:
    return pygame.key.get_just_pressed()

def keys_released() -> pygame.key.ScancodeWrapper:
    return pygame.key.get_just_released()

class TextInput():
    
    _TEXT: str = ""
    _CURSOR: int = 0
    _ACTIVE: bool = False

    @staticmethod
    def start(initial_text: str = ""):
        pygame.key.start_text_input()
        TextInput._TEXT = initial_text
        TextInput._CURSOR = len(initial_text)
        TextInput._ACTIVE = True

    @staticmethod
    def end():
        pygame.key.stop_text_input()
        TextInput._ACTIVE = False

    @staticmethod
    def get_text() -> str:
        return (
                    TextInput._TEXT[0:TextInput._CURSOR]
                    + "|" if TextInput._ACTIVE else ""
                    + TextInput._TEXT[TextInput._CURSOR:]
                )
    
    @staticmethod
    def is_active() -> bool:
        return TextInput._ACTIVE

    @staticmethod
    def get_cursor_pos() -> int:
        return TextInput._CURSOR
    
    @staticmethod
    def _move_cursor(delta: int, to_word: bool = False):
        if to_word:
            i = delta
            while (TextInput._CURSOR + i >= 0 and 
                   TextInput._CURSOR + i < len(TextInput._TEXT) and
                   (TextInput._TEXT[TextInput._CURSOR + i] != " ")):
                i += delta
            delta = i

        TextInput._CURSOR = skittle.math.clamp(TextInput._CURSOR + delta, 0, len(TextInput._TEXT))

    @staticmethod
    def _textinput_event(event: pygame.Event):
        if event.type == pygame.KEYDOWN:
            key = event.key
            mod = event.mod

            highlights = mod & pygame.KMOD_SHIFT != 0
            moves_word = mod & pygame.KMOD_CTRL != 0

            if key == KEY_BACKSPACE:
                TextInput._move_cursor(-1, moves_word)
                TextInput._TEXT = TextInput._TEXT[:TextInput._CURSOR] + TextInput._TEXT[TextInput._CURSOR + 1:]

            if key == KEY_DELETE:
                TextInput._TEXT = TextInput._TEXT[:TextInput._CURSOR] + TextInput._TEXT[TextInput._CURSOR + 1:]

            if key == KEY_LEFT:
                TextInput._move_cursor(-1, moves_word)

            if key == KEY_RIGHT:
                TextInput._move_cursor(1, moves_word)

        if event.type == pygame.TEXTINPUT:
            char = event.text

            TextInput._TEXT = (
                    TextInput._TEXT[0:TextInput._CURSOR]
                    + char
                    + TextInput._TEXT[TextInput._CURSOR:]
                )
            TextInput._CURSOR += 1



KEY_BACKSPACE  = pygame.K_BACKSPACE   
KEY_TAB        = pygame.K_TAB         
KEY_CLEAR      = pygame.K_CLEAR       
KEY_RETURN     = pygame.K_RETURN      
KEY_PAUSE      = pygame.K_PAUSE       
KEY_ESCAPE     = pygame.K_ESCAPE      
KEY_SPACE      = pygame.K_SPACE       
KEY_EXCLAIM    = pygame.K_EXCLAIM     
KEY_QUOTEDBL   = pygame.K_QUOTEDBL    
KEY_HASH       = pygame.K_HASH        
KEY_DOLLAR     = pygame.K_DOLLAR      
KEY_AMPERSAND  = pygame.K_AMPERSAND   
KEY_QUOTE      = pygame.K_QUOTE       
KEY_LEFTPAREN  = pygame.K_LEFTPAREN   
KEY_RIGHTPAREN = pygame.K_RIGHTPAREN  
KEY_ASTERISK   = pygame.K_ASTERISK    
KEY_PLUS       = pygame.K_PLUS        
KEY_COMMA      = pygame.K_COMMA       
KEY_MINUS      = pygame.K_MINUS       
KEY_PERIOD     = pygame.K_PERIOD      
KEY_SLASH      = pygame.K_SLASH       
KEY_0          = pygame.K_0           
KEY_1          = pygame.K_1           
KEY_2          = pygame.K_2           
KEY_3          = pygame.K_3           
KEY_4          = pygame.K_4           
KEY_5          = pygame.K_5           
KEY_6          = pygame.K_6           
KEY_7          = pygame.K_7           
KEY_8          = pygame.K_8           
KEY_9          = pygame.K_9           
KEY_COLON      = pygame.K_COLON       
KEY_SEMICOLON  = pygame.K_SEMICOLON   
KEY_LESS       = pygame.K_LESS        
KEY_EQUALS     = pygame.K_EQUALS      
KEY_GREATER    = pygame.K_GREATER     
KEY_QUESTION   = pygame.K_QUESTION    
KEY_AT         = pygame.K_AT          
KEY_LEFTBRACKET= pygame.K_LEFTBRACKET 
KEY_BACKSLASH  = pygame.K_BACKSLASH   
KEY_RIGHTBRACKE= pygame.K_RIGHTBRACKET
KEY_CARET      = pygame.K_CARET       
KEY_UNDERSCORE = pygame.K_UNDERSCORE  
KEY_BACKQUOTE  = pygame.K_BACKQUOTE   
KEY_a          = pygame.K_a           
KEY_b          = pygame.K_b           
KEY_c          = pygame.K_c           
KEY_d          = pygame.K_d           
KEY_e          = pygame.K_e           
KEY_f          = pygame.K_f           
KEY_g          = pygame.K_g           
KEY_h          = pygame.K_h           
KEY_i          = pygame.K_i           
KEY_j          = pygame.K_j           
KEY_k          = pygame.K_k           
KEY_l          = pygame.K_l           
KEY_m          = pygame.K_m           
KEY_n          = pygame.K_n           
KEY_o          = pygame.K_o           
KEY_p          = pygame.K_p           
KEY_q          = pygame.K_q           
KEY_r          = pygame.K_r           
KEY_s          = pygame.K_s           
KEY_t          = pygame.K_t           
KEY_u          = pygame.K_u           
KEY_v          = pygame.K_v           
KEY_w          = pygame.K_w           
KEY_x          = pygame.K_x           
KEY_y          = pygame.K_y           
KEY_z          = pygame.K_z           
KEY_DELETE     = pygame.K_DELETE      
KEY_KP0        = pygame.K_KP0         
KEY_KP1        = pygame.K_KP1         
KEY_KP2        = pygame.K_KP2         
KEY_KP3        = pygame.K_KP3         
KEY_KP4        = pygame.K_KP4         
KEY_KP5        = pygame.K_KP5         
KEY_KP6        = pygame.K_KP6         
KEY_KP7        = pygame.K_KP7         
KEY_KP8        = pygame.K_KP8         
KEY_KP9        = pygame.K_KP9         
KEY_KP_PERIOD  = pygame.K_KP_PERIOD   
KEY_KP_DIVIDE  = pygame.K_KP_DIVIDE   
KEY_KP_MULTIPLY= pygame.K_KP_MULTIPLY 
KEY_KP_MINUS   = pygame.K_KP_MINUS    
KEY_KP_PLUS    = pygame.K_KP_PLUS     
KEY_KP_ENTER   = pygame.K_KP_ENTER    
KEY_KP_EQUALS  = pygame.K_KP_EQUALS   
KEY_UP         = pygame.K_UP          
KEY_DOWN       = pygame.K_DOWN        
KEY_RIGHT      = pygame.K_RIGHT       
KEY_LEFT       = pygame.K_LEFT        
KEY_INSERT     = pygame.K_INSERT      
KEY_HOME       = pygame.K_HOME        
KEY_END        = pygame.K_END         
KEY_PAGEUP     = pygame.K_PAGEUP      
KEY_PAGEDOWN   = pygame.K_PAGEDOWN    
KEY_F1         = pygame.K_F1          
KEY_F2         = pygame.K_F2          
KEY_F3         = pygame.K_F3          
KEY_F4         = pygame.K_F4          
KEY_F5         = pygame.K_F5          
KEY_F6         = pygame.K_F6          
KEY_F7         = pygame.K_F7          
KEY_F8         = pygame.K_F8          
KEY_F9         = pygame.K_F9          
KEY_F10        = pygame.K_F10         
KEY_F11        = pygame.K_F11         
KEY_F12        = pygame.K_F12         
KEY_F13        = pygame.K_F13         
KEY_F14        = pygame.K_F14         
KEY_F15        = pygame.K_F15         
KEY_NUMLOCK    = pygame.K_NUMLOCK     
KEY_CAPSLOCK   = pygame.K_CAPSLOCK    
KEY_SCROLLOCK  = pygame.K_SCROLLOCK   
KEY_RSHIFT     = pygame.K_RSHIFT      
KEY_LSHIFT     = pygame.K_LSHIFT      
KEY_RCTRL      = pygame.K_RCTRL       
KEY_LCTRL      = pygame.K_LCTRL       
KEY_RALT       = pygame.K_RALT        
KEY_LALT       = pygame.K_LALT        
KEY_RMETA      = pygame.K_RMETA       
KEY_LMETA      = pygame.K_LMETA       
KEY_LSUPER     = pygame.K_LSUPER      
KEY_RSUPER     = pygame.K_RSUPER      
KEY_MODE       = pygame.K_MODE        
KEY_HELP       = pygame.K_HELP        
KEY_PRINT      = pygame.K_PRINT       
KEY_SYSREQ     = pygame.K_SYSREQ      
KEY_BREAK      = pygame.K_BREAK       
KEY_MENU       = pygame.K_MENU        
KEY_POWER      = pygame.K_POWER       
KEY_EURO       = pygame.K_EURO        
KEY_AC_BACK    = pygame.K_AC_BACK     