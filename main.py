from moderngl import TRIANGLE_STRIP
from moderngl_window import WindowConfig

from logging import getLogger
from colour import Color
from PIL import Image
from os.path import normpath, join
import numpy as np

logger = getLogger(__name__)

w, h = 1280, 720
a_ratio = 16 / 9

color_palette = [Color("black"), Color("blue"), Color("yellow"), Color("red")]

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
    resource_dir = normpath(join(__file__, '../data'))

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

        thirds = int(256 / (len(color_palette) - 1))
        color_bytes = np.array([[[0, 0, 0]]], dtype=np.uint8)
        for i in range(len(color_palette) - 1):
            section_gradient = list(color_palette[i].range_to(color_palette[i + 1], thirds))
            color_bytes = np.vstack((color_bytes, [np.array([list(color.get_rgb())]) * 255 for color in section_gradient]))

        # print(color_bytes.astype(np.uint8))
        # image = Image.open('./data/pal.png')
        # img = Image.fromarray(color_bytes.reshape(216, 1), 'RGB')
        # img.show()
        # self.texture = self.load_texture_2d("pal.png")
        # with open("./data/pal.png", "rb") as image:
        #   b = [x.strip() for x in image.readlines()]
        # print(b)
        # self.texture = self.ctx.texture((1, 256), 3, data=a)
        self.texture = self.ctx.texture((256, 1), 3, data=color_bytes.astype(np.uint8))
        # print(np.array(image))

        vertices = np.array([-1.0, -1.0, -1.0, 1.0, 1.0, -1.0, 1.0, 1.0], dtype='f4')

        # We control the 'in_vert' and `in_color' variables
        self.vbo = self.ctx.buffer(vertices)
        self.vao = self.ctx.simple_vertex_array(self.prog, self.vbo, 'in_vert')

    def render(self, time, frametime):
        self.ctx.clear(1.0, 1.0, 1.0)

        self.center.value = (0.5, 0.0)
        self.max_iters.value = 100
        self.scale.value = 1.5
        self.ratio.value = self.aspect_ratio

        self.texture.use()
        self.vao.render(TRIANGLE_STRIP)


if __name__ == "__main__":
    # MainWindow.run()
    thirds = int(256 / (len(color_palette) - 1))
    color_bytes = np.array([[[0, 0, 0]]])# np.zeros((256, 1, 3))
    for i in range(len(color_palette) - 1):
        section_gradient = list(color_palette[i].range_to(color_palette[i + 1], thirds))
        color_bytes = np.dstack((color_bytes, [np.array([[list(color.get_rgb())]]) * 255 for color in section_gradient]))

    print(color_bytes)
    # img = Image.fromarray(, 'RGB')
