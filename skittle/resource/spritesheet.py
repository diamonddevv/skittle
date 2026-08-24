import pygame
import moderngl

class Spritesheet():
    def __init__(self, 
                 surface: pygame.Surface,
                 sprite_w: int = 16,
                 sprite_h: int = 16,
                 seperation_x: int = 0,
                 seperation_y: int = 0
                 ) -> None:
        self.surface = surface
        self.sprite_w = sprite_w
        self.sprite_h = sprite_h
        self.seperation_x = seperation_x
        self.seperation_y = seperation_y

        self._stitches = 1


    def uv(self, cell_x: int, cell_y: int, stitch_idx: int = 0) -> tuple[float, float, float, float]:
        sprites_per_row_per_stitch = self.surface.width / (self.sprite_w + self.seperation_x) / self._stitches

        sheet_w, sheet_h = self.surface.size
        px_step_x = 1 / sheet_w
        px_step_y = 1 / sheet_h

        px_tl_x = (cell_x + (stitch_idx * sprites_per_row_per_stitch)) * (self.sprite_w + self.seperation_x)
        px_tl_y = cell_y * (self.sprite_h + self.seperation_y)


        u0 = px_step_x * px_tl_x
        v0 = px_step_y * px_tl_y
        u1 = u0 + px_step_x * self.sprite_w 
        v1 = v0 + px_step_y * self.sprite_h

        return u0, v0, u1, v1
    
    @staticmethod
    def stitch(*spritesheets: Spritesheet) -> Spritesheet:
        """
        take multiple similar spritesheets and stitch them together into, internally, one large spritesheet.
        """
        total_w = 0 # stack horizontally
        max_h = 0

        agreed_sprite_w = spritesheets[0].sprite_w
        agreed_sprite_h = spritesheets[0].sprite_h
        agreed_sep_x = spritesheets[0].seperation_x
        agreed_sep_y = spritesheets[0].seperation_y

        agreed_sheet_w = spritesheets[0].surface.width

        for ss in spritesheets:
            if ss.sprite_w != agreed_sprite_w: raise ValueError("tried to stitch together spritesheets with different sprite widths")
            if ss.sprite_h != agreed_sprite_h: raise ValueError("tried to stitch together spritesheets with different sprite heights")
            if ss.seperation_x != agreed_sep_x: raise ValueError("tried to stitch together spritesheets with different seperation widths")
            if ss.seperation_y != agreed_sep_y: raise ValueError("tried to stitch together spritesheets with different seperation heights")

            if ss.surface.width != agreed_sheet_w: raise ValueError("tried to stitch together spritesheets with different spritesheet widths")

            total_w += ss.surface.width
            if ss.surface.height > max_h:
                max_h = ss.surface.height

        surf = pygame.Surface((total_w, max_h), pygame.SRCALPHA)
        
        for idx, ss in enumerate(spritesheets):
            surf.blit(ss.surface, (idx * agreed_sheet_w, 0))

        spritesheet = Spritesheet(surf, agreed_sprite_w, agreed_sprite_h, agreed_sep_x, agreed_sep_y)
        spritesheet._stitches = len(spritesheets)
        return spritesheet