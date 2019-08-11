"""
Implement the canva of 3D graphical user interface for
the Logic Simulator.

Used in the Logic Simulator project to enable the user
to display the 3D simulation.

Classes passed to gui.py to be initialised as wx.canvas widgets.

Classes:
--------
My3DGLCanvas - Handles all 3D canvas drawing operations. Derrived
               class of wxcanvas.GLCanvas.
"""
import wx
import wx.glcanvas as wxcanvas
import numpy as np
import math
from OpenGL import GL, GLU, GLUT

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


class My3DGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.
    render(self): Handles all drawing operations.
    on_paint(self, event): Handles the paint event.
    on_size(self, event): Handles the canvas resize event.
    on_mouse(self, event): Handles mouse events.
    reset_pan(self): Resets 3D view to zero pan and 1 zoom.

    Private methods
    --------------
    _gen_text(self, device_id, output_id): Formats device name and type
                                           into label for 3D display.
    _render_text(self, text, x_pos, y_pos, z_pos): Handles text drawing
                                                  operations.
    _draw_cuboid(x, z, half_width, half_depth, height): Draw cuboids
        of varying heights to represent high, low, blank signals.
    """

    def __init__(self, parent, devices, monitors, names):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Circuit properties
        self.monitors = monitors
        self.devices = devices
        self.names = names
        self.cycles = 0
        self.color_dict = {
            devices.AND: [1, 0.6, 0.6, 0.4],  # Pink
            devices.OR: [0.5, 1.0, 0.0, 0.4],  # Green
            devices.NAND: [1, 0.6, 0.2, 0.4],  # Orange
            devices.NOR: [1, 1, 0.4, 0.4],  # Yellow
            devices.XOR: [0.4, 1, 1, 0.4],  # Light blue
            devices.CLOCK: [1, 0.2, 1, 0.4],  # Hot pink
            devices.SWITCH: [0.8, 0.6, 1, 0.4],  # Light purple
            devices.D_TYPE: [0, 0.8, 0.8, 0.4],  # Teal
            devices.SIGGEN: [0.6, 0.6, 0.6, 0.4]  # Grey
        }

        # Constants for OpenGL materials and lights
        self.mat_diffuse = [0.0, 0.0, 0.0, 1.0]
        self.mat_no_specular = [0.0, 0.0, 0.0, 0.0]
        self.mat_no_shininess = [0.0]
        self.mat_specular = [0.5, 0.5, 0.5, 1.0]
        self.mat_shininess = [50.0]
        self.top_right = [1.0, 1.0, 1.0, 0.0]
        self.straight_on = [0.0, 0.0, 1.0, 0.0]
        self.no_ambient = [0.0, 0.0, 0.0, 1.0]
        self.dim_diffuse = [0.5, 0.5, 0.5, 1.0]
        self.bright_diffuse = [1.0, 1.0, 1.0, 1.0]
        self.med_diffuse = [0.75, 0.75, 0.75, 1.0]
        self.full_specular = [0.5, 0.5, 0.5, 1.0]
        self.no_specular = [0.0, 0.0, 0.0, 1.0]

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise the scene rotation matrix
        self.scene_rotate = np.identity(4, 'f')

        # Initialise variables for zooming
        self.zoom = 1

        # Offset between viewpoint and origin of the scene
        self.depth_offset = 1000

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)

        GL.glViewport(0, 0, size.width, size.height)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(45, size.width / size.height, 10, 10000)

        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()  # lights positioned relative to the viewer
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, self.no_ambient)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, self.med_diffuse)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_SPECULAR, self.no_specular)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, self.top_right)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_AMBIENT, self.no_ambient)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_DIFFUSE, self.dim_diffuse)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_SPECULAR, self.no_specular)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_POSITION, self.straight_on)

        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SPECULAR, self.mat_specular)
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SHININESS, self.mat_shininess)
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE,
                        self.mat_diffuse)
        GL.glColorMaterial(GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE)

        GL.glClearColor(0.0, 0.0, 0.0, 0.0)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glCullFace(GL.GL_BACK)
        GL.glEnable(GL.GL_COLOR_MATERIAL)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_LIGHT0)
        GL.glEnable(GL.GL_LIGHT1)
        GL.glEnable(GL.GL_NORMALIZE)

        # Viewing transformation - set the viewpoint back from the scene
        GL.glTranslatef(0.0, 0.0, - self.depth_offset)

        # Modelling transformation - pan, zoom and rotate
        GL.glTranslatef(self.pan_x, self.pan_y, 0.0)
        GL.glMultMatrixf(self.scene_rotate)
        GL.glScalef(self.zoom, self.zoom, self.zoom)

    def render(self):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the OpenGL rendering context
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # Draw traces extending into negative z dimension, with different
        # devices having different x values.
        if self.devices is not None:
            x = (- self.GetSize()[0] // 2 + 20)
            text_y = -20  # Constant text y position
            step_x = 100  # Change in x for new device.
            half_width, half_depth = (5, 10)
            for i, key in enumerate(self.monitors.monitors_dictionary.keys()):
                device_id = key[0]
                output_id = key[1]
                signal_list = self.monitors.monitors_dictionary[(
                    device_id, output_id)]
                # Device specific color of trace
                color = self.devices.get_device(device_id).device_kind
                GL.glColor4f(*self.color_dict[color])
                step_z = 20
                z = self.cycles // 2 * step_z
                text_z = self.cycles // 2 * step_z + 10
                # Traces drawn backward to appear drawn into screen.
                # Negative z is into screen.
                for ind, signal in enumerate(signal_list):
                    if signal == self.devices.LOW:
                        self._draw_cuboid(x, z, half_width, half_depth, 5)
                    elif signal == self.devices.HIGH:
                        self._draw_cuboid(x, z, half_width, half_depth, 15)
                    elif signal == self.devices.BLANK:
                        self._draw_cuboid(x, z, half_width, half_depth, 1)
                    z -= step_z
                GL.glColor3f(1.0, 1.0, 1.0)  # text is white
                self._render_text(self._gen_text(device_id, output_id),
                                  x-100//2, text_y, text_z)
                x += step_x
        # We have been drawing to the back buffer,
        # flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def _gen_text(self, device_id, output_id):
        """Generates labels for 3D traces"""
        monitor_name = self.devices.get_signal_name(device_id, output_id)
        typ = self.devices.get_device(device_id).device_kind

        # Truncate device name to 7 characters if
        # longer than 7 characters.
        typ = self.names.get_name_string(typ)
        if len(monitor_name) > 7:
            monitor_name = monitor_name[:7]
        # Format label
        text = monitor_name + "\n" + typ
        return text

    def reset_pan(self):
        """Resets pan and rotation of 3D view"""
        self.scene_rotate = np.identity(4, 'f')
        self.pan_x = 0
        self.pan_y = 0
        self.zoom = 1
        self.init = False
        self.Refresh()

    def _draw_cuboid(self, x_pos, z_pos, half_width, half_depth, height):
        """
        Draw a cuboid at the specified position, with the specified
        dimensions.
        """
        GL.glBegin(GL.GL_QUADS)
        GL.glNormal3f(0, -1, 0)
        GL.glVertex3f(x_pos - half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos + half_depth)
        GL.glNormal3f(0, 1, 0)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos + half_depth)
        GL.glNormal3f(-1, 0, 0)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos + half_depth)
        GL.glNormal3f(1, 0, 0)
        GL.glVertex3f(x_pos + half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos + half_depth)
        GL.glNormal3f(0, 0, -1)
        GL.glVertex3f(x_pos - half_width, -6, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos - half_depth)
        GL.glNormal3f(0, 0, 1)
        GL.glVertex3f(x_pos - half_width, -6 + height, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, -6 + height, z_pos + half_depth)
        GL.glEnd()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the OpenGL rendering context
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render()

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        self.SetCurrent(self.context)

        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()

        if event.Dragging():
            GL.glMatrixMode(GL.GL_MODELVIEW)
            GL.glLoadIdentity()
            x = event.GetX() - self.last_mouse_x
            y = event.GetY() - self.last_mouse_y
            if event.LeftIsDown():
                GL.glRotatef(math.sqrt((x * x) + (y * y)), y, x, 0)
            if event.MiddleIsDown():
                GL.glRotatef((x + y), 0, 0, 1)
            if event.RightIsDown():
                self.pan_x += x
                self.pan_y -= y
            GL.glMultMatrixf(self.scene_rotate)
            GL.glGetFloatv(GL.GL_MODELVIEW_MATRIX, self.scene_rotate)
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False

        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False

        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False

        self.Refresh()  # triggers the paint event

    def _render_text(self, text, x_pos, y_pos, z_pos):
        """Handle text drawing operations."""
        GL.glDisable(GL.GL_LIGHTING)
        GL.glRasterPos3f(x_pos, y_pos, z_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_10
        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos3f(x_pos, y_pos, z_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

        GL.glEnable(GL.GL_LIGHTING)
