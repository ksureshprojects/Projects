"""
Implement the canva of 2D graphical user interface for
the Logic Simulator.

Used in the Logic Simulator project to enable the user
to display the 2D simulation.

Classes passed to gui.py to be initialised as wx.canvas widgets.


Classes:
--------
MyOpenGLCanvas - Handles canvas drawing operations common to
                 both Traces and Labels canvas. Derrived class
                 of wxcanvas.GLCanvas.
MyTraces - Handles drawing operations specific to trace canvas.
           Derrived class of MyOpenGLCanvas.
MyLabels - Handles drawing operations specific to labels canvas.
           Derrived class of MyOpenGLCanvas.
MyAxis - Shows cycles axis. Derrived class of MyOpenGLCanvas.
"""

import wx
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser


class MyOpenGLCanvas(wxcanvas.GLCanvas):
    """
    Class to initialise an Open GL canvas.

    Parameters
    ----------
    parent: parent window.
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    on_size(self, event): Handles the canvas resize event.
    """
    # Class static attribute, common to all instances of class,
    # 'pan_y'. Ensures pan_y coordinate is the same in entire
    # application.
    pan_y = 0
    pan_x = 0
    max_y = 0
    max_y = 0
    spacex = 10

    def __init__(self, parent, devices, monitors, names):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)
        self.monitors = monitors
        self.devices = devices
        self.names = names
        self.start = (0, 0)
        # Bind events to the canvas
        self.Bind(wx.EVT_SIZE, self.on_size)
        # self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False


class MyTraces(MyOpenGLCanvas):
    """
    Handle all drawing operations for Traces.

    This class contains functions for drawing traces on a open GL
    canvas. It also contains handlers for events relating to the
    canvas.

    Parameters
    ----------
    parent: parent window.
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    render(self, text): Handles all drawing operations.
    on_paint(self, event): Handles the paint event.
    on_mouse(self, event): Handles mouse events.
    init_gl(self): Configures the OpenGL context.

    Private methods
    --------------
    _gen_trace(self): Creates list of trace vertices and anchor
                      points.
    """

    def __init__(self, parent, devices, monitors, names):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, devices, monitors, names)
        self.traces = []
        self.quads = []
        # Give Traces class access to labels class.
        self.labels = None
        self.axis = None
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position
        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)
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

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(MyOpenGLCanvas.pan_x, MyOpenGLCanvas.pan_y, 0.0)
        # GL.glScaled(self.zoom, self.zoom, self.zoom)

    def _gen_trace(self):
        """Generates list of trace vertices and anchor points for traces"""
        # Anchor point initialisations and steps.
        tran_y = 5  # Y offset from start
        tran_x = 5  # X offset from start
        step_x = 20  # Change in x over one cycle
        step_y = 55  # Change in y between trace y anchors
        quad_off = 4  # Offset by which trace background exceeds trace.
        # Reinitialise traces array
        self.traces = []
        self.quads = []
        # For each monitored output record trace corresponding to
        # signal in its signal list.

        for device_id, output_id in self.monitors.monitors_dictionary:
            tran_x = 5  # X offset from start
            rise = 25  # Change in Y for high signal.
            trace = []
            quad = []
            quad.append((tran_x, tran_y - quad_off))
            quad.append((tran_x, tran_y + rise + quad_off))
            signal_list = self.monitors.monitors_dictionary[(
                device_id, output_id)]
            blank_count = 0
            for ind, signal in enumerate(signal_list):
                # Rise/Fall lines have to be specified separately
                # with an offset to create smooth trace.
                if signal == self.devices.HIGH:
                    if ind != blank_count:
                        # Rise/Fall line
                        trace.append((self.start[0] + tran_x,
                                      self.start[1] + tran_y + rise + 1))
                    trace.append((self.start[0] + tran_x,
                                  self.start[1] + tran_y + rise))
                    tran_x += step_x  # Next signal
                    trace.append((self.start[0] + tran_x,
                                  self.start[1] + tran_y + rise))
                    # Rise/Fall line
                    trace.append((self.start[0] + tran_x,
                                  self.start[1] + tran_y + rise + 1))
                if signal == self.devices.LOW:
                    if ind != blank_count:
                        # Rise/Fall line
                        trace.append((self.start[0] + tran_x,
                                      self.start[1] + tran_y - 2))
                    trace.append((self.start[0] + tran_x,
                                  self.start[1] + tran_y))
                    tran_x += step_x  # Next signal
                    trace.append((self.start[0] + tran_x,
                                  self.start[1] + tran_y))
                    # Rise/Fall line
                    trace.append((self.start[0] + tran_x,
                                  self.start[1] + tran_y - 2))
                if signal == self.devices.RISING:
                    print("/", end="")
                if signal == self.devices.FALLING:
                    print("\\", end="")
                if signal == self.devices.BLANK:
                    blank_count += 1
                    tran_x += step_x
            quad.append((tran_x, tran_y + rise + quad_off))
            quad.append((tran_x, tran_y - quad_off))
            self.quads.append(quad)
            self.traces.append(trace)
            # Increment y for next trace.
            tran_y += step_y
        MyOpenGLCanvas.max_y = tran_y
        MyOpenGLCanvas.max_x = tran_x

    def render(self):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        # Generate trace vertices for each monitor.
        if self.devices is not None:
            self._gen_trace()
            # Draw trace for each monitor.
            for i, key in enumerate(self.monitors.monitors_dictionary.keys()):
                # Shade trace in a color corresponding to device type
                device_id = key[0]
                if self.devices is not None:
                    color = self.devices.get_device(device_id).device_kind
                    GL.glColor4f(*self.color_dict[color])
                    GL.glBegin(GL.GL_QUADS)
                    for q in self.quads[i]:
                        x, y = q
                        GL.glVertex2f(x, y)
                    GL.glEnd()
                    GL.glColor3f(0.0, 0.0, 1.0)
                    GL.glLineWidth(GL.GLfloat(3))
                    # GL_LINES differs from GL_LINE_STRIP, in that
                    # lines are only created between pairs of vertices.
                    GL.glBegin(GL.GL_LINES)
                    for k in self.traces[i]:
                        x, y = k
                        GL.glVertex2f(x, y)
                    GL.glEnd()
        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_mouse(self, event):
        """Handle mouse events."""
        if event.ButtonDown():
            # Register location where main mouse pressed.
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
        if event.Dragging():
            # Panning variables are static global in base class.
            # Don't allow positive panning (fix left trace edge to window)
            if MyOpenGLCanvas.pan_x + (event.GetX() - self.last_mouse_x) > 0:
                MyOpenGLCanvas.pan_x = 0
            # Don't allow panning past end of trace.
            elif (MyOpenGLCanvas.pan_x + (event.GetX() - self.last_mouse_x) <
                  min(self.GetSize()[0] - MyOpenGLCanvas.max_x, 0)):
                MyOpenGLCanvas.pan_x = min(self.GetSize()[0] -
                                           MyOpenGLCanvas.max_x -
                                           MyOpenGLCanvas.spacex, 0)
            else:
                MyOpenGLCanvas.pan_x += event.GetX() - self.last_mouse_x
            # Don't allow positive panning (fix left trace edge to window)
            if MyOpenGLCanvas.pan_y - (event.GetY() - self.last_mouse_y) > 0:
                MyOpenGLCanvas.pan_y = 0
            # Don't allow panning past end of trace.
            elif (MyOpenGLCanvas.pan_y - (event.GetY() - self.last_mouse_y) <
                  min(self.GetSize()[1] - MyOpenGLCanvas.max_y, 0)):
                MyOpenGLCanvas.pan_y = min(
                    self.GetSize()[1] - MyOpenGLCanvas.max_y, 0)
            else:
                MyOpenGLCanvas.pan_y -= event.GetY() - self.last_mouse_y

            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            # To ensure self.init_GL called in self.render()
            # and self.labels.render().
            self.init = False
            self.axis.init = False
            self.labels.init = False
        self.axis.render()  # Update value in axis.
        self.labels.render()  # Update value in labels.
        self.render()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True
        self.render()


class MyLabels(MyOpenGLCanvas):
    """
    Handle all drawing operations for labels.

    Class is derrived from parant general canvas class
    and only handles display and event handling with regards
    to trace labels.

    Parameters
    ----------
    parent: parent window.
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    render(self, text): Handles all drawing operations.
    on_paint(self, event): Handles the paint event.
    on_mouse(self, event): Handles mouse events.
    init_gl(self): Configures the OpenGL context.

    Private methods
    --------------
    _gen_text(self): Creates list of trace labels and anchor
                     points.
    _render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent, devices, monitors, names):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, devices, monitors, names)
        self.texts = []
        # Allow traces canvas to be accessed from labels canvas.
        self.traces = None
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(0, MyOpenGLCanvas.pan_y, 0.0)

    def _gen_text(self):
        """Generates list of labels and anchor points for traces"""
        # Anchor point initialisations and steps.
        tran_y = 25  # Y offset from start
        perm_x = 10  # Constant x offset
        step_y = 55  # Change in y between label y anchors.
        # Reinitialise labels array
        self.texts = []

        # For each monitored output get device name, type and configuration
        # variable.
        for device_id, output_id in self.monitors.monitors_dictionary:
            monitor_name = self.devices.get_signal_name(device_id, output_id)
            typ = self.devices.get_device(device_id).device_kind

            # Truncate device name to 14 characters if
            # longer than 14 characters.
            typ = self.names.get_name_string(typ)
            if len(monitor_name) > 14:
                monitor_name = monitor_name[:14]
            # Format label
            text = monitor_name + "\n" + typ
            # Append label and anchor point to list
            self.texts.append([text, (self.start[0] + perm_x,
                                      self.start[1] + tran_y)])
            # Increment anchor point
            tran_y += step_y

    def render(self):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Generate array of trace labels for all monitored devices,
        # and corresponding coordinate anchor points.
        if self.devices is not None:
            self._gen_text()

            # Display labels.
            for i in range(len(self.monitors.monitors_dictionary.keys())):
                text_x, text_y = self.texts[i][1]
                self._render_text(self.texts[i][0], text_x, text_y)

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        self.render()

    def _render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_10

        # Format and display each character in text.
        for character in text:
            if character == '\n':
                GL.glColor3f(1.0, 0.0, 0.0)
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

    def on_mouse(self, event):
        """Handle mouse events."""
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()

        if event.Dragging():
            # Panning variables are static global in base class.
            # Don't allow positive panning (fix left trace edge to window)
            if MyOpenGLCanvas.pan_y - (event.GetY() - self.last_mouse_y) > 0:
                MyOpenGLCanvas.pan_y = 0
            # Don't allow panning past end of trace.
            elif (MyOpenGLCanvas.pan_y - (event.GetY() - self.last_mouse_y) <
                  min(self.GetSize()[1] - MyOpenGLCanvas.max_y, 0)):
                MyOpenGLCanvas.pan_y = min(
                    self.GetSize()[1] - MyOpenGLCanvas.max_y, 0)
            else:
                MyOpenGLCanvas.pan_y -= event.GetY() - self.last_mouse_y

            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            # Ensure self.init_GL called in both self.render()
            # and self.traces.render().
            self.traces.init = False
            self.init = False
        self.traces.render()
        self.render()


class MyAxis(MyOpenGLCanvas):
    """
    Handles drawing of cycles axis for Traces.

    This class contains functions for drawing axis on a open GL
    canvas. It also contains handlers for events relating to the
    canvas.

    Parameters
    ----------
    parent: parent window.
    cycles: number of completed cycles in current simulation

    Public methods
    --------------
    render(self, text): Handles all drawing operations.
    on_paint(self, event): Handles the paint event.
    on_mouse(self, event): Handles mouse events.
    init_gl(self): Configures the OpenGL context.


    Private methods
    --------------
    _gen_axis(self): Creates list of axis vertices.
    _render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent, cycles):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, None, None, None)
        self.axis = []
        self.cycles = cycles
        self.num = []
        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(MyOpenGLCanvas.pan_x, 0, 0.0)

    def _gen_axis(self):
        """Generates list of trace vertices and anchor points for traces"""
        # Anchor point initialisations and steps.
        tran_y = 20  # Y offset from start
        tran_y_num = 10  # Y offset from start
        tran_x = 5
        step_x = 20  # Change in x over one cycle
        step_y = 5  # Tick Heights
        # Create axis showing each execution cycle.
        self.axis = []
        self.num = []
        for i in range(self.cycles):
            # Gen axis line trace
            self.axis.append(
                (self.start[0] + tran_x, self.start[0] + tran_y + step_y))
            self.axis.append((self.start[0] + tran_x, self.start[0] + tran_y))
            # Gen axis labels
            if (i + 1) % 10 == 0:
                self.num.append((str(i + 1), (self.start[0] + tran_x + 3,
                                              self.start[0] + tran_y_num)))
            tran_x += step_x
            self.axis.append((self.start[0] + tran_x, self.start[0] + tran_y))
            self.axis.append(
                (self.start[0] + tran_x, self.start[0] + tran_y + step_y))

    def render(self):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        # Generate axis vertices
        self._gen_axis()
        # Draw axis.
        GL.glColor3f(0.0, 0.0, 0.0)
        GL.glBegin(GL.GL_LINE_STRIP)
        for k in self.axis:
            x, y = k
            GL.glVertex2f(x, y)
        GL.glEnd()
        # Draw axis values on axis.
        for t in self.num:
            text_x, text_y = t[1]
            self._render_text(t[0], text_x, text_y)

        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True
        self.render()

    def _render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_10

        # Format and display each character in text.
        for character in text:
            if character == '\n':
                GL.glColor3f(1.0, 0.0, 0.0)
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))
