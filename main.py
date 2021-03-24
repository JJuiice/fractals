from moderngl_window import WindowConfig

from logging import getLogger
import numpy as np

logger = getLogger(__name__)

w, h = 200, 200


class MainWindow(WindowConfig):
    gl_version = (3, 3)
    window_size = (h, w)
    aspect_ratio = 1
    title = "Mandelbrot"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Do initialization here
        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330
                in vec2 in_vert;
                in vec3 in_color;
                out vec3 v_color;
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                    v_color = in_color;
                }
            ''',
            fragment_shader='''
                #version 330
                in vec3 v_color;
                out vec4 f_color;
                void main() {
                    f_color = vec4(v_color, 1.0);
                }
            ''',
        )

        # Point coordinates are put followed by the vec3 color values
        # [x, y, r, g, b, ...]
        vertices = compute()
        # vertices = np.array([np.random.uniform(-1, 1) if ind % 5 < 2 else np.random.random_sample() for ind, x in enumerate(range(w))])

        self.vbo = self.ctx.buffer(vertices)

        # We control the 'in_vert' and `in_color' variables
        self.vao = self.ctx.vertex_array(
            self.prog,
            [
                # Map in_vert to the first 2 floats
                # Map in_color to the next 3 floats
                (self.vbo, '2f 3f', 'in_vert', 'in_color')
            ],
        )

        # np.set_printoptions(threshold=np.inf)
        print(vertices)

    def render(self, time, frametime):
        self.ctx.clear(1.0, 1.0, 1.0)
        self.vao.render()


def compute():
    max_iters = 999
    ms_x_space = np.linspace(-2.5, 1, w)
    ms_y_space = np.linspace(-1, 1, h)
    data = []

    for x_inx, x in enumerate(ms_x_space):
        mgl_x = ms_y_space[x_inx]
        for y in ms_y_space:
            iter_n = 0
            c = complex(x, y)
            z = complex(0, 0)

            while z.real**2 + z.imag**2 <= 4 and iter_n < max_iters:
                z = z**2 + c
                iter_n += 1

            iter_n_str = f"{iter_n:03d}"
            r = 0 if int(iter_n_str[0]) == 0 else 0.1*int(iter_n_str[0])
            g = 0 if int(iter_n_str[1]) == 0 else 0.1*int(iter_n_str[1])
            b = 0 if int(iter_n_str[2]) == 0 else 0.1*int(iter_n_str[2])

            data.extend([mgl_x, y, r, g, b])

    return np.array(data)


if __name__ == "__main__":
    MainWindow.run()
