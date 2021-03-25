from moderngl import TRIANGLE_STRIP
from moderngl_window import WindowConfig

from logging import getLogger
from colour import Color
from os.path import normpath, join
import numpy as np

logger = getLogger(__name__)

w, h = 1280, 720
a_ratio = 16 / 9

color_palette = [Color("black"), Color("blue"), Color("red")]

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

uniform sampler2D Texture;
uniform vec2 Center;
uniform float Scale;
uniform float Ratio;
uniform int Max_Iters;

void main()
{
    vec2 c;
    int i;

    c.x = Ratio * v_text.x * Scale - Center.x;
    c.y = v_text.y * Scale - Center.y;

    vec2 z = c;

    for (i = 0; i < Max_Iters; i++) {
        float
        x = (z.x * z.x - z.y * z.y) + c.x;
        float
        y = (z.y * z.x + z.x * z.y) + c.y;

        if ((x * x + y * y) > 4.0) {
            break;
        }
        
        z.x = x;
        z.y = y;
    }

    f_color = texture(Texture, vec2((i == Max_Iters ? 0.0: float(i)) / 100.0, 0.0));
}
'''


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

        self.center = self.prog['Center']
        self.scale = self.prog['Scale']
        self.ratio = self.prog['Ratio']
        self.max_iters = self.prog['Max_Iters']

        start_inx = 0
        sections = int(256 / (len(color_palette) - 1))
        end_inx = sections
        color_bytes = np.zeros((256, 1, 3), dtype=np.uint8)
        for i in range(len(color_palette) - 1):
            section_gradient = list(color_palette[i].range_to(color_palette[i + 1], sections))
            color_bytes[start_inx: end_inx, 0] = [np.array(np.array(list(color.get_rgb())) * 255).astype(np.uint8)
                                                   for color in section_gradient]
            start_inx = sections
            end_inx += sections

        print(color_bytes)
        self.mouse_center = (0.5, 0.0)
        self.center.value = self.mouse_center
        self.scale.value = 1.5
        self.max_iters.value = 100
        self.ratio.value = self.aspect_ratio
        self.texture = self.ctx.texture((256, 1), 3, data=color_bytes)

        vertices = np.array([-1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0], dtype='f4')

        # We control the 'in_vert' and `in_color' variables
        self.vbo = self.ctx.buffer(vertices)
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert')

    def render(self, time, frametime):
        self.ctx.clear(1.0, 1.0, 1.0)

        self.texture.use()
        self.vao.render(TRIANGLE_STRIP)

    def mouse_scroll_event(self, x_offset: float, y_offset: float):
        if y_offset > 0:
            if self.scale.value > 0.1:
                self.center.value = normalize_xy(self.mouse_center[0], self.mouse_center[1])
                self.scale.value -= 0.1
            elif self.scale.value > 0.01:
                self.center.value = normalize_xy(self.mouse_center[0], self.mouse_center[1])
                self.scale.value -= 0.01
            elif self.scale.value > 0.001:
                self.center.value = normalize_xy(self.mouse_center[0], self.mouse_center[1])
                self.scale.value -= 0.001
        elif y_offset < 0 and self.scale.value < 1.5:
            if self.scale.value < 1.5:
                self.center.value = normalize_xy(self.mouse_center[0], self.mouse_center[1])
                self.scale.value += 0.1
            else:
                self.center.value = (0.5, 0.0)
                self.scale.value = 1.5

    def mouse_position_event(self, x, y, dx, dy):
        self.mouse_center = (x, y)


def normalize_xy(x, y):
    norm_x = 1.0 - 2.0 * float(x / w);
    norm_y = -1.0 + 2.0 * float(y / h);

    return norm_x, norm_y


if __name__ == "__main__":
    MainWindow.run()
