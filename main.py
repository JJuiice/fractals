from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QWindow, QOpenGLWindow

from OpenGL import GL

from logging import getLogger
import numpy as np
import sys
import ctypes

logger = getLogger(__name__)

w, h = 400, 400

vtx_code = '''
attribute vec2 position;
void main()
{
  gl_Position = vec4(position, 0.0, 1.0);
}
'''

frags_code = '''
void main()
{
  gl_FragColor = vec4(1.0, 0.0, 1.0, 0.0);
}
'''


class MainWindow(QOpenGLWindow):
    def __init__(self):
        super().__init__()

        self.resize(w, h)
        self.setSurfaceType(QWindow.OpenGLSurface)
        self.setTitle("Mandelbrot")

    def initializeGL(self) -> None:
        # Create Program and Shaders
        program = GL.glCreateProgram()
        vtx = GL.glCreateShader(GL.GL_VERTEX_SHADER)
        frag = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)

        for name, shader, source in (('Vertex', vtx, vtx_code), ('Fragment', frag, frags_code)):
            # Set shaders source
            GL.glShaderSource(shader, source)

            # Compile shaders
            GL.glCompileShader(shader)
            if not GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS):
                error = GL.glGetShaderInfoLog(shader).decode()
                logger.error("%s shader compilation error: %s", name, error)

            GL.glAttachShader(program, shader)

        GL.glLinkProgram(program)
        if not GL.glGetProgramiv(program, GL.GL_LINK_STATUS):
            print(GL.glGetProgramInfoLog(program))
            raise RuntimeError('Linking error')

        GL.glDetachShader(program, vtx)
        GL.glDetachShader(program, frag)

        GL.glUseProgram(program)

        # Build data and request buffer slot from GPU
        data = np.zeros((3, 2), dtype=np.float32)
        buffer = GL.glGenBuffers(1)

        # Set default buffer and vertex attribute array
        stride = data.strides[0]
        offset = ctypes.c_void_p(0)
        loc = GL.glGetAttribLocation(program, "position")
        GL.glEnableVertexAttribArray(loc)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, buffer)
        GL.glVertexAttribPointer(loc, 2, GL.GL_FLOAT, False, stride, offset)

        # CPU data
        data[...] = [(-1, +1), (+0.5, -1), (-1, -1)]

        # Upload CPU data to GPU buffer
        GL.glBufferData(
            GL.GL_ARRAY_BUFFER, data.nbytes, data, GL.GL_DYNAMIC_DRAW)

    def paintGL(self) -> None:
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        GL.glDrawArrays(GL.GL_TRIANGLE_STRIP, 0, 3)


def compute():
    pass


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    logger.info("Beginning OpenGL execution")
    sys.exit(app.exec_())
