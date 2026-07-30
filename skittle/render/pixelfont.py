from pyglm import glm
import moderngl
import typing
import skittle
import json

class TextRenderer():
    def __init__(
            self,
            ctx: moderngl.Context,
            spritesheet: skittle.resource.Spritesheet,
            codepoints: str,
            rows: int,
            cols: int,
            caps_only: bool = False,
            default_glyph_width: int = 0, 
            glyph_widths: dict[str, int] = {}
            ) -> None:
        self.spritesheet = spritesheet
        self.codepoints = codepoints
        self.rows = rows
        self.cols = cols
        self.caps_only = caps_only
        self.default_glyph_width = default_glyph_width
        self.glyph_widths = glyph_widths

        self.mesh = skittle.render.MultiInstanceSpritesheetQuad(ctx, self.spritesheet)


    def get_character_width(self, char: str) -> int:
        if char in self.glyph_widths:
            return self.glyph_widths[char]
        else:
            return self.default_glyph_width if self.default_glyph_width != 0 else self.spritesheet.sprite_w

    def get_codepoint_pos(self, char: str) -> tuple[int, int]:
        if self.caps_only:
            char = char.upper()

        if len(char) != 1:
            raise ValueError("char must be a single character")
        
        if not char in self.codepoints:
            raise ValueError(f"char must be in the list of codepoints, {char} is not")
        
        idx = self.codepoints.index(char)
        x = 0
        y = 0

        while idx >= self.cols:
            y += 1
            idx -= self.cols
        x = idx

        return (x, y)
    
    def verify_all_codepoints(self, text: str) -> tuple[bool, str]:
        for c in text:
            if not c in self.codepoints and not c in ['\x0a']: # ignore line feeds
                return False, c
        return True, ""
    
    def calculate_size_for_text(self, text: str) -> tuple[int, int]:
        longest_line_width = -1
        lines = 1

        line_width = 0

        for char in text:
            if char == '\n':
                lines += 1
                if line_width > longest_line_width:
                    longest_line_width = line_width
                line_width = 0
            else:
                line_width += self.get_character_width(char)

        if line_width > longest_line_width:
            longest_line_width = line_width

        return (longest_line_width, lines * self.spritesheet.sprite_h)

    def render(self, camera: skittle.render.Camera, text: str, pos: glm.vec2, scale: float = 1, rotation_radians: float = 0, color: skittle.color.Color = skittle.color.WHITE, overlay: bool = False):

        passed, bad_char = self.verify_all_codepoints(text)
        if not passed:
            skittle.err(f"tried to render text with invalid character '{bad_char}'")
            return None

        if self.caps_only:
            text = text.upper()

        inst_data: list[skittle.render.MultiInstanceSpritesheetQuad._InstanceData] = []

        width_pos = 0
        line = 0
        for char in text:

            if char == '\n':
                line += 1
                width_pos = 0
            else:
                cx, cy = self.get_codepoint_pos(char)
                width = self.get_character_width(char)
                inst_data.append((
                    width_pos + self.spritesheet.sprite_w / 2,
                    -line * self.spritesheet.sprite_h - self.spritesheet.sprite_h / 2,
                    cx, cy
                ))
                width_pos += width

        self.mesh.bake_instances(inst_data)

        self.mesh.position = pos
        self.mesh.scale = scale
        self.mesh.color = color
        self.mesh.rotation_radians = rotation_radians
        self.mesh.render(camera, overlay)


    def release(self):
        self.mesh.release()


    @staticmethod
    def from_json(ctx: moderngl.Context, json_path: str) -> TextRenderer:
        import os
        with open(json_path, "rb") as f:
            obj: dict[str, typing.Any] = json.load(f)
        
        return TextRenderer(
            ctx, 
            skittle.resource.spritesheet(
                obj["spritesheet_path"], 
                sprite_w=obj.get("sprite_width", 16),
                sprite_h=obj.get("sprite_height", 16),
                sep_x=obj.get("seperation_x", 0),
                sep_y=obj.get("seperation_y", 0),
                ),
                ''.join(obj["glyphs"]),
                obj["rows"],
                obj["columns"],
                obj.get("caps_only", False),
                obj.get("default_glyph_width", 0),
                obj.get("glyph_widths", {}),
            )