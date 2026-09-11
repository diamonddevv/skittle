from pyglm import glm
import moderngl
import typing
import skittle
import json

type _Orientation = typing.Literal['left_to_right', 'right_to_left', 'top_to_bottom', 'bottom_to_top']


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
        self.skip_invalid_chars = False

        self.mesh = skittle.render.mesh.InstancedSpritesheetMesh(ctx, self.spritesheet)


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
    
    def calculate_size_for_text(self, text: str, scale: float) -> tuple[float, float]:
        longest_line_width = 0
        line_width = 0
        line = 0
        for char in text:

            if char == '\n':
                line += scale * self.spritesheet.sprite_h
                if line_width > longest_line_width:
                    longest_line_width = line_width
                line_width = 0
            else:
                if self.skip_invalid_chars and char not in self.codepoints:
                    continue

                width = self.get_character_width(char) * scale
                
                line_width += width

        return (longest_line_width, line)

    def render(self, camera: skittle.camera.Camera, text: str, pos: glm.vec2, scale: float = 1, color: skittle.color.Color = skittle.color.WHITE, orientation: _Orientation = 'left_to_right', overlay: bool = False):
        camera.submit(lambda: self._render_now(
            camera, text, pos, scale, color, orientation, overlay
            ), layer=camera.calc_layer(0, overlay))

    def _render_now(self, camera: skittle.camera.Camera, text: str, pos: glm.vec2, scale: float = 1, color: skittle.color.Color = skittle.color.WHITE, orientation: _Orientation = 'left_to_right', overlay: bool = False):
        """
        call `render` instead. this function exists to hack around the fact a single mesh could only draw one piece of text per frame, so instead they're indiviudally batched on a layer of abstraction higher than the mesh itself
        """
        if self.caps_only:
            text = text.upper()

        passed, bad_char = self.verify_all_codepoints(text)
        if not passed and not self.skip_invalid_chars:
            skittle.err(f"tried to render text with invalid character '{bad_char}'")
            return None

        if orientation == 'right_to_left':
            raise Exception("text cant be drawn right to left")
        if orientation == 'top_to_bottom':
            raise Exception("top to bottom doesnt work and im lazy, i dont want it to work right now")

        inst_data: list[skittle.render.RenderInstance] = []

        width_pos = 0
        line = 0
        for char in text:

            if char == '\n':
                line += scale
                width_pos = 0
            else:
                if self.skip_invalid_chars and char not in self.codepoints:
                    continue

                cx, cy = self.get_codepoint_pos(char)
                width = self.get_character_width(char) * scale


                sizing_offset = glm.vec2(
                    self.spritesheet.sprite_w / 2,
                    -self.spritesheet.sprite_h / 2
                )

                inst_data.append(skittle.render.RenderInstance(
                    (glm.vec2(
                        width_pos,
                        -line * self.spritesheet.sprite_h 
                    ) if orientation == 'left_to_right' else glm.vec2(
                        line * self.spritesheet.sprite_h,
                        width_pos,
                    )) + sizing_offset,
                    (cx, cy),
                    color,
                    0 if orientation == 'left_to_right' else 3*glm.half_pi(),
                    glm.vec2(scale)
                ))
                width_pos += width

        self.mesh.bake_instances(inst_data)

        self.mesh._render_now(camera, pos, overlay=overlay)

    def release(self):
        self.mesh.release()


    @staticmethod
    def from_json(ctx: moderngl.Context, json_path: str) -> TextRenderer:
    
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