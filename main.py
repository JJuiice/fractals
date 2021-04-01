from moderngl import TRIANGLE_STRIP
from moderngl_window import WindowConfig

from logging import getLogger
from colour import Color
import numpy as np

logger = getLogger(__name__)

w, h = 1920, 1080
a_ratio = 16 / 9
max_zoom_out = 1.5

color_palette = [Color("black"), Color("blue"), Color("red")]
color_palette_len = len(color_palette)

max_sig_figs = 5
scale_list = [round(0.1 ** x, max_sig_figs) for x in range(1, max_sig_figs + 1)]

mand_vtx_shader = '''
#version 330

in vec2 in_vert;
out vec2 v_text;

void main() {
    gl_Position = vec4(in_vert, 0.0, 1.0);
    v_text = in_vert;
}
'''

mand_frag_shader = '''
# version 330

in vec2 v_text;
out vec4 f_color;

uniform sampler2D u_texture;
uniform vec2 u_translate;
uniform float u_scale;
uniform float u_ratio;
uniform int u_max_iters;

void main()
{
    vec2 c;
    int i;

    c.x = u_ratio * v_text.x * u_scale - 0.5 + u_translate.x;
    c.y = v_text.y * u_scale + u_translate.y;

    vec2 z = c;

    for (i = 0; i < u_max_iters; i++) {
        float x = (z.x * z.x - z.y * z.y) + c.x;
        float y = 2 * z.x * z.y + c.y;

        if ((x * x + y * y) > 4.0)
            break;
        
        z.x = x;
        z.y = y;
    }

    f_color = texture(u_texture, vec2(float(i) / float(u_max_iters), 0.0));
}
'''


def correction_xy(x, y):
    norm_x = -2.65 + 5.3 * float(x / w)
    norm_y = 1.5 - 3.0 * float(y / h)

    return norm_x, norm_y


class MainWindow(WindowConfig):
    gl_version = (3, 3)
    window_size = (w, h)
    aspect_ratio = a_ratio
    title = "Mandelbrot"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.ctx.program(
            vertex_shader=mand_vtx_shader,
            fragment_shader=mand_frag_shader
        )

        self.translate = self.prog['u_translate']
        self.scale = self.prog['u_scale']
        self.ratio = self.prog['u_ratio']
        self.max_iters = self.prog['u_max_iters']

        start_inx = 0
        sections = int(256 / color_palette_len)
        end_inx = sections

        color_bytes = np.zeros((256, 1, 3), dtype=np.uint8)

        if color_palette_len % 2 != 0:
            start_inx += 1
            end_inx += 1
            color_bytes[0, 0] = np.array([0, 0, 0]).astype(np.uint8)

        for i in range(len(color_palette) - 1):
            section_gradient = list(color_palette[i].range_to(color_palette[i + 1], sections))
            color_bytes[start_inx: end_inx, 0] = [np.array(np.array(list(color.get_rgb())) * 255).astype(np.uint8)
                                                  for color in section_gradient]
            start_inx = end_inx
            end_inx += sections

        self.mouse_ref = [0, 0]

        self.translate.value = (0, 0)
        self.scale.value = max_zoom_out
        self.max_iters.value = 100
        self.ratio.value = self.aspect_ratio
        self.texture = self.ctx.texture((256, 1), 3, data=color_bytes)

        vertices = np.array([-1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0], dtype='f4')

        self.vbo = self.ctx.buffer(vertices)
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert')

    def render(self, time, frametime):
        self.ctx.clear(1.0, 1.0, 1.0)

        self.texture.use()
        self.vao.render(TRIANGLE_STRIP)

    def mouse_scroll_event(self, x_offset: float, y_offset: float):
        correction_factor = 0.6

        if y_offset > 0 and self.scale.value > scale_list[-1]:
            for i in scale_list:
                if self.scale.value > i:
                    self.scale.value -= i * correction_factor
                    break

        elif y_offset < 0:
            if self.scale.value < max_zoom_out:
                scaled = 0
                for i in reversed(scale_list):
                    if self.scale.value < (i * 10):
                        self.scale.value += i * correction_factor
                        scaled = 1
                        break

                if not scaled:
                    self.scale.value += 0.1 * correction_factor
            else:
                self.scale.value = max_zoom_out
                self.translate.value = (0, 0)

    def mouse_position_event(self, x, y, dx, dy):
        if self.scale.value == max_zoom_out:
            self.mouse_ref = [x, y]

    def mouse_drag_event(self, x: int, y: int, dx: int, dy: int):
        new_center = (
            self.mouse_ref[0] + (dx * self.scale.value * -1.0),
            self.mouse_ref[1] + (dy * self.scale.value * -1.0))

        self.translate.value = correction_xy(new_center[0], new_center[1])

        self.mouse_ref[0] = new_center[0]
        self.mouse_ref[1] = new_center[1]


if __name__ == "__main__":
    MainWindow.run()
