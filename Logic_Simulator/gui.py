"""
Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
Gui - configures the main window and all the widgets.
"""

from canvas3D import My3DGLCanvas
from canva import MyTraces, MyLabels, MyAxis, MyOpenGLCanvas
from parse import Parser
from scanner import Scanner
from monitors import Monitors
from network import Network
from devices import Devices
from names import Names
import wx
import sys
import app_const as appC
import wx.glcanvas as wxcanvas
from OpenGL import GL, GLUT

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser

from canva import MyTraces, MyLabels, MyAxis, MyOpenGLCanvas
from canvas3D import My3DGLCanvas

import builtins
builtins.__dict__['_'] = wx.GetTranslation


class Gui(wx.Frame):
    """
    Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: Title of the window.
    path: Path of circuit specification file
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.
    network: instance of the network.Network() class.
    lang: Language specification.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.
    on_run_button(self, event): Event handler for when the user clicks the run
                                button.
    on_continue_button(self, event): Event handler for when the user clicks the
                                     continue button.
    on_config_button(self, event): Event handler for when user clicks apply
                                   button.
    on_show(self, event): Event handler for when user clicks show button.
    on_remove(self, event): Event handler for when user clicks remove button.
    on_conf_select(self, event): Update current conf var shown in gui
                                 when new config device selected.
    on_open(self): Handles event of loading a new circuit file in GUI.
    on_2D(self, event): Handles event when user clicks 2D view button.
    on_3D(self, event):Handles event when user clicks 3D view button.
    on_reset(self, event): Handles event when user clicks reset button.
    updateLanguage(self, lang): Update language shown in GUI.

    Private methods
    ---------------
    _re_render(self): Rerenders traces and labels after any action.
    _gen_lists(self): Set self.outputs, self.configurable, self.monitored.
    _run_network(self, cycles, warm_flag): Run network in response
                                           to some change.
    _verify_number(self, num, lower_bound, upper_bound): Validate config var.
    _regen_monitored(self): Update monitor display in GUI.
    _get_file_name(self, path_name): Extracts file name from path.
    _update_labels(self): Updates widget labels with selected language.
    """

    def __init__(self, title, path, names, devices,
                 network, monitors, lang=u"en"):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(928, 700))

        # Set locale
        self.locale = None
        wx.Locale.AddCatalogLookupPathPrefix('locale')
        self.updateLanguage(lang)
        # Configure the file menu
        self.fileMenu = wx.Menu()
        self.fileMenu.Append(wx.ID_ABOUT, _(u"&About"))
        self.fileMenu.Append(wx.ID_EXIT, _(u"&Exit"))
        self.fileMenu.Append(wx.ID_OPEN, _(u"&Open"))
        # Configure the language menu
        self.langMenu = wx.Menu()
        self.id_ro = wx.NewId()
        self.id_en = wx.NewId()
        self.langMenu.Append(self.id_en, _(u"&English"))
        self.langMenu.Append(self.id_ro, _(u"&Română"))
        # Configure view menu
        self.viewMenu = wx.Menu()
        self.viewMenu.Append(wx.ID_NO, _(u"2D Display"))
        self.viewMenu.Append(wx.ID_YES, _(u"3D Display"))
        self.currentview = wx.ID_NO
        # Create menu bar
        self.menuBar = wx.MenuBar()
        self.menuBar.Append(self.fileMenu, _(u"&File"))
        self.menuBar.Append(self.viewMenu, _(u"View"))
        self.menuBar.Append(self.langMenu, _(u"Language"))
        self.SetMenuBar(self.menuBar)

        # number of simulation cycles completed
        self.cycles_completed = 0
        # current file path
        self.path = path

        self.devices = devices
        self.monitors = monitors
        self.names = names
        self.network = network
        self.title = title

        # Creating 2D arrays with names and IDs of devices/signals
        # for all devices, configurable devices, and monitored signals.
        # self.monitored can change but self.outputs and
        # self.configurable can't change.
        [self.outputs, self.configurable,
         self.monitored] = self._gen_lists()

        # Configure the widgets/canvas:
        # Canvas for drawing signals
        self.my3D_canvas = My3DGLCanvas(self, devices, monitors, names)
        self.traces_canvas = MyTraces(self, devices, monitors, names)
        self.labels_canvas = MyLabels(self, devices, monitors, names)
        self.axis_canvas = MyAxis(self, self.cycles_completed)
        self.axis_title = wx.StaticText(self, wx.ID_ANY, "")
        # Connecting canva to share attributes.
        self.traces_canvas.labels = self.labels_canvas
        self.traces_canvas.axis = self.axis_canvas
        self.labels_canvas.traces = self.traces_canvas
        self.labels_canvas.SetInitialSize(wx.Size(110, -1))
        # Widget for error reporting/user feedback
        self.act_log = wx.TextCtrl(self, wx.ID_ANY,
                                   style=(wx.TE_MULTILINE |
                                          wx.TE_READONLY | wx.TE_LEFT |
                                          wx.TE_BESTWRAP),
                                   name="Activity Log Panel")
        font1 = wx.Font(10, wx.TELETYPE, wx.NORMAL, wx.NORMAL)
        self.act_log.SetFont(font1)
        # Widgets to control number of cycles.
        self.cycles = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, _("Run"))
        self.continue_button = wx.Button(self, wx.ID_ANY, _("Continue"))
        # Widgets to control configuration of clocks and switches.
        self.config_button = wx.Button(self, wx.ID_ANY, _("Apply"))
        self.config_list = wx.ComboBox(self, wx.ID_ANY, "",
                                       choices=self.configurable[0],
                                       style=(wx.CB_READONLY))
        # Deal with situation where circuit has no configurable devices.
        if len(self.configurable[0]) > 0:
            # Select first device in list as default
            self.config_list.SetSelection(0)
            self.config_var = wx.SpinCtrl(self, wx.ID_ANY,
                                          str(self.configurable[2][0]))
        else:
            # Initialise widget but disable button.
            self.config_var = wx.SpinCtrl(self, wx.ID_ANY)
            self.config_button.Disable()
        # Widgets to display/select all possible outputs.
        self.outs = wx.ListBox(self, wx.ID_ANY,
                               style=(wx.LB_MULTIPLE |
                                      wx.LB_NEEDED_SB),
                               choices=self.outputs[0])
        self.add_outs = wx.Button(self, wx.ID_ANY, _("Show"))
        # Widgets to display/remove all current monitored outputs.
        self.mons = wx.ListBox(self, wx.ID_ANY,
                               style=(wx.LB_MULTIPLE |
                                      wx.LB_NEEDED_SB),
                               choices=self.monitored[0])
        self.dele_mons = wx.Button(self, wx.ID_ANY, _("Remove"))
        # Toggle view and reload file buttons.
        self.view2D = wx.Button(self, wx.ID_ANY, _("2D View"))
        self.view3D = wx.Button(self, wx.ID_ANY, _("3D View"))
        self.reset = wx.Button(self, wx.ID_ANY, _("Reset View"))
        self.reload = wx.Button(self, wx.ID_ANY, _("Reload File"))

        # Styling text of titles in widgets
        self.title_font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.BOLD)
        # self.cyc_title.SetFont(self.title_font)
        # self.config_title.SetFont(self.title_font)
        # self.out_title.SetFont(self.title_font)
        # self.mon_title.SetFont(self.title_font)
        # self.uf_title.SetFont(self.title_font)
        self.axis_title.SetFont(self.title_font)

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.config_button.Bind(wx.EVT_BUTTON, self.on_config_button)
        self.add_outs.Bind(wx.EVT_BUTTON, self.on_show)
        self.dele_mons.Bind(wx.EVT_BUTTON, self.on_remove)
        self.config_list.Bind(wx.EVT_COMBOBOX, self.on_conf_select)
        self.view2D.Bind(wx.EVT_BUTTON, self.on_2D)
        self.view3D.Bind(wx.EVT_BUTTON, self.on_3D)
        self.reset.Bind(wx.EVT_BUTTON, self.on_reset)
        self.reload.Bind(wx.EVT_BUTTON, self.on_reload)

        # Root level app section splitter.
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        canv = wx.StaticBox(self, wx.ID_ANY)
        self.canv_maj_sizer = wx.StaticBoxSizer(canv, wx.VERTICAL)
        # Sizer to horizontally align labels canvas and trace
        # canvas.
        canv_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # Sizer to horizontally align axis title and axis.
        canv_axis_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # Sizer to vertically arrange 2D/3D canvas and user
        # feedback section.
        self.canv_feed_sizer = wx.BoxSizer(wx.VERTICAL)
        # Sizer to organise sidebar elements vertically.
        side_sizer = wx.BoxSizer(wx.VERTICAL)

        # Sizers and Boxes to organise sidebar elements.
        # StaticBoxes are parents of StaticBoxSizers.
        # Horizontal BoxSizers used to arrange side by side
        # elements in a StaticBox.
        self.uf = wx.StaticBox(self, wx.ID_ANY, _("Activity Log"))
        self.cyc = wx.StaticBox(self, wx.ID_ANY, _("Cycles"))
        self.conf = wx.StaticBox(self, wx.ID_ANY, _("Configure Devices"))
        self.out = wx.StaticBox(self, wx.ID_ANY, _("Outputs"))
        self.mon = wx.StaticBox(self, wx.ID_ANY, _("Monitored Outputs"))
        self.ax = wx.StaticBox(self, wx.ID_ANY)
        self.tog = wx.StaticBox(self, wx.ID_ANY)

        # To align with labels canvas
        self.ax.SetMinSize(wx.Size(110, 20))
        uf_sizer = wx.StaticBoxSizer(self.uf, wx.VERTICAL)
        cyc_sizer = wx.StaticBoxSizer(self.cyc, wx.VERTICAL)
        cyc_but_sizer = wx.BoxSizer(wx.HORIZONTAL)
        config_sizer = wx.StaticBoxSizer(self.conf, wx.VERTICAL)
        config_but_sizer = wx.BoxSizer(wx.HORIZONTAL)
        out_sizer = wx.StaticBoxSizer(self.out, wx.VERTICAL)
        mon_sizer = wx.StaticBoxSizer(self.mon, wx.VERTICAL)
        tog_sizer = wx.StaticBoxSizer(self.tog, wx.VERTICAL)
        dim_but_sizer = wx.BoxSizer(wx.HORIZONTAL)
        reset_but_sizer = wx.BoxSizer(wx.HORIZONTAL)
        ax_title = wx.StaticBoxSizer(self.ax, wx.HORIZONTAL)

        # Add widgets to relevent sizers/boxes. Add sub-sizers
        # to parent sizers. 'Add' method allows behaviour modes
        # of widgets to be specified using wx Stock Constants.
        # Order in which widgets are added to sizers are determined
        # by order in which Add methods called.
        # Box.Add(control, proportion, flag, border)
        # Left and Right sections of GUI
        self.main_sizer.Add(self.canv_feed_sizer, 4, wx.EXPAND | wx.ALL, 5)
        self.main_sizer.Add(side_sizer, 0, wx.ALL | wx.EXPAND, 5)
        # Canva and activity log
        self.canv_feed_sizer.Add(self.canv_maj_sizer, 4, wx.EXPAND |
                                 wx.ALL, 5)
        self.canv_feed_sizer.Add(self.my3D_canvas, 4, wx.EXPAND |
                                 wx.ALL, 5)
        self.canv_feed_sizer.Add(uf_sizer, 1, wx.EXPAND | wx.ALL, 1)
        self.canv_feed_sizer.Hide(1)
        # Trace/Labels sections and axis section
        self.canv_maj_sizer.Add(canv_sizer, 1, wx.EXPAND)
        self.canv_maj_sizer.Add(canv_axis_sizer, 0, wx.EXPAND)
        # Labels canvas and traces canvas
        canv_sizer.Add(self.labels_canvas, 0, wx.ALL | wx.EXPAND, 5)
        canv_sizer.Add(self.traces_canvas, 6, wx.EXPAND | wx.ALL, 5)
        # Axis title and axis.
        canv_axis_sizer.Add(ax_title, 0, wx.EXPAND | wx.ALL, 5)
        canv_axis_sizer.Add(self.axis_canvas, 6, wx.EXPAND | wx.ALL, 5)
        # To size and align axis title container.
        ax_title.Add(self.axis_title, 1, wx.EXPAND | wx.ALIGN_CENTER)
        # Activity log title and output box.
        # uf_sizer.Add(self.uf_title, 0, wx.LEFT, 5)
        uf_sizer.Add(self.act_log, 1, wx.EXPAND | wx.ALL, 5)
        # Right sidebar.
        side_sizer.Add(cyc_sizer, 0, wx.ALIGN_CENTER | wx.EXPAND)  # Cycles
        side_sizer.Add(config_sizer, 0,  wx.ALIGN_CENTER |
                       wx.EXPAND)  # Configure devices
        side_sizer.Add(out_sizer, 1,  wx.ALIGN_CENTER | wx.EXPAND)  # Outputs
        side_sizer.Add(mon_sizer, 1, wx.ALIGN_CENTER |
                       wx.EXPAND)  # Monitored Outputs
        side_sizer.Add(tog_sizer, 0, wx.ALIGN_CENTER |
                       wx.EXPAND)  # Toggle Buttons
        # Cycles
        # cyc_sizer.Add(self.cyc_title, 0, wx.BOTTOM, 10)  # Title
        cyc_sizer.Add(self.cycles, 0, wx.EXPAND | wx.ALL, 10)  # Textbox
        cyc_sizer.Add(cyc_but_sizer, 0, wx.ALIGN_CENTER, 1)  # Buttons
        # Organising run and continue button horizontally
        cyc_but_sizer.Add(self.run_button, 1, wx.ALL, 5)  # Run button
        cyc_but_sizer.Add(self.continue_button, 1,
                          wx.ALL, 5)  # Continue Button
        # Configure devices dropdown list
        # config_sizer.Add(self.config_title, 0, wx.BOTTOM, 10)  # Title

        # Second Interim Report Feedback Update: Swap widget order.

        config_sizer.Add(self.config_list, 1,
                         wx.EXPAND | wx.ALL, 16)  # Dropdown List
        config_sizer.Add(config_but_sizer, 0,
                         wx.ALL |
                         wx.ALIGN_CENTER, 5)  # Apply button
        # and textbox

        # Organising apply button and text box horizontally
        config_but_sizer.Add(self.config_button, 0,
                             wx.RIGHT, 6)  # Apply Button
        config_but_sizer.Add(self.config_var, 1,
                             wx.BOTTOM | wx.LEFT, 5)  # Textbox
        # Output list and add monitor button
        # out_sizer.Add(self.out_title, 0, wx.BOTTOM, 10)  # Title
        out_sizer.Add(self.outs, 1, wx.ALL | wx.EXPAND, 10)  # List
        out_sizer.Add(self.add_outs, 0, wx.ALIGN_CENTER | wx.ALL, 5)  # Button
        # Monitor list and delete button.
        # mon_sizer.Add(self.mon_title, 0, wx.BOTTOM, 10)  # Title
        mon_sizer.Add(self.mons, 1, wx.ALL | wx.EXPAND, 10)  # List
        mon_sizer.Add(self.dele_mons, 0, wx.ALIGN_CENTER | wx.ALL, 5)  # Button
        # 2D, 3D, Reset, Reload Buttons
        tog_sizer.Add(dim_but_sizer, 0,
                      wx.ALIGN_CENTER, 1)
        tog_sizer.Add(reset_but_sizer, 0,
                      wx.ALIGN_CENTER, 1)
        # 2D, 3D, View Buttons
        dim_but_sizer.Add(self.view2D,  1, wx.ALL, 5)
        dim_but_sizer.Add(self.view3D,  1, wx.ALL, 5)
        # reset, reload, View Buttons
        reset_but_sizer.Add(self.reset,  1, wx.ALL, 5)
        reset_but_sizer.Add(self.reload,  1, wx.ALL, 5)

        # Set min size of window.
        self.SetMinSize(wx.Size(1100, 900))
        self.SetInitialSize(wx.Size(1100, 900))
        # Set main_sizer as the main sizer of the wx.Frame
        self.SetSizer(self.main_sizer)

    def _re_render(self):
        """
        Private function that updates monitors and devices
        in classes in canva.py and then calls its render method
        to replot traces taking into account updates.
        """
        print('rendering')
        if self.currentview == wx.ID_NO:
            self.traces_canvas.SetColour("grey")
            self.traces_canvas.monitors = self.monitors
            self.traces_canvas.devices = self.devices
            self.traces_canvas.render()
            self.labels_canvas.monitors = self.monitors
            self.labels_canvas.devices = self.devices
            self.labels_canvas.render()
            self.axis_canvas.cycles = self.cycles_completed
            self.axis_canvas.render()
        if self.currentview == wx.ID_YES:
            self.my3D_canvas.monitors = self.monitors
            self.my3D_canvas.devices = self.devices
            self.my3D_canvas.render()

    def _gen_lists(self):
        """
        Create arrays of two sub-arrays for: all possible
        outputs, configurable outputs and monitored outputs.
        The first sub-array stores name strings of outputs
        and the second sub_array stores the device_id and
        output_id of the corresponding output.
        """
        outputs = [[] for i in range(2)]
        configurable = [[] for i in range(3)]
        monitored = [[] for i in range(2)]

        for device in self.devices.devices_list:
            # Get device name.
            dev_name = self.names.get_name_string(device.device_id)
            # Append output name to device name if output name explicit.
            if device.device_kind == self.devices.D_TYPE:
                for output in device.outputs:
                    out_name = self.names.get_name_string(output)
                    outputs[0].append(dev_name + "." + out_name)
                    outputs[1].append((device.device_id, output))
            else:
                outputs[0].append(dev_name)
                outputs[1].append((device.device_id, None))
            # Recording devices that are clocks or switches.
            if (device.device_kind == self.devices.CLOCK or
                    device.device_kind == self.devices.SWITCH):
                configurable[0].append(dev_name)
                configurable[1].append(device.device_id)
                if device.device_kind == self.devices.CLOCK:
                    configurable[2].append(device.clock_half_period)
                if device.device_kind == self.devices.SWITCH:
                    configurable[2].append(device.switch_state)
        # Recording monitored outputs.
        for monitor in self.monitors.monitors_dictionary:
            dev_name = self.names.get_name_string(monitor[0])
            out_name = self.names.get_name_string(monitor[1])
            if out_name is not None:
                monitored[0].append(dev_name + "." + out_name)
            else:
                monitored[0].append(dev_name)
            monitored[1].append(monitor)

        return [outputs, configurable, monitored]

    def _regen_monitored(self, monitor):
        """
        Private method to regenerate monitored outputs list in GUI.
        """
        dev_name = self.names.get_name_string(monitor[0])
        out_name = self.names.get_name_string(monitor[1])
        if out_name is not None:  # For DTYPE devices
            self.monitored[0].append(dev_name + "." + out_name)
            self.monitored[1].append(monitor)
            # Update Monitored Outputs List in GUI
            self.mons.InsertItems([dev_name + "." + out_name],
                                  self.mons.GetCount())
        else:
            self.monitored[0].append(dev_name)
            self.monitored[1].append(monitor)
            # Update Monitored Outputs List in GUI
            self.mons.InsertItems([dev_name], self.mons.GetCount())

    def _run_network(self, cycles, warm_flag=False):
        """
        Run the network for the specified number of simulation cycles.
        Return True if successful.
        """
        # If running network only to update traces.
        if warm_flag:
            self.monitors.reset_monitors()  # Clear previously stored signals

        for _ in range(cycles):
            # Network executed and signal recorded one cycle
            # at a time.
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                print("Error! Network oscillating.")
                self.act_log.AppendText(
                    _("***Error: Network oscillating.") + "\n")
                return False
        # Displays results in command line interface.
        self.monitors.display_signals()
        return True

    def _verify_number(self, num, lower_bound, upper_bound):
        """
        Return the current number if it is within provided bounds.
        Return None if no number is provided or if it falls outside the valid
        range.
        """
        if upper_bound is not None:
            if num > upper_bound:
                print("Number out of range.")
                return None

        if lower_bound is not None:
            if num < lower_bound:
                print("Number out of range.")
                return None

        return num

    def on_conf_select(self, event):
        """
        Handle event when user selects a configurable
        device and accordingly update default value in
        config var input box to current device config var
        value
        """
        config_var = self.configurable[2][self.config_list.GetCurrentSelection(
        )]
        self.config_var.SetValue(config_var)

    def on_menu(self, event):  # TODO DAVID
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox(_("Logic Simulator\nCreated by ") +
                          "David Almasan, " +
                          "Vatsal Raina, Karthik Suresh\nGF2 Software\n" +
                          _("2019 IIB Summer Term"), _("About Logsim"),
                          wx.ICON_INFORMATION | wx.OK)
        if Id == wx.ID_OPEN:
            self.on_open()

        if Id == wx.ID_YES:
            self.on_3D(None)

        if Id == wx.ID_NO:
            self.on_2D(None)

        if Id == self.id_en:
            self.updateLanguage(u"en")
            self._update_Labels()

        if Id == self.id_ro:
            self.updateLanguage(u"el")
            self._update_Labels()

    def on_2D(self, event):
        """Handle event when user clicks 2D view button"""
        if self.currentview == wx.ID_YES:
            # Hide 3D view
            self.canv_feed_sizer.Hide(1)
            # Show 2D view
            self.canv_feed_sizer.Show(0)
            # Reload
            self.main_sizer.Layout()
            self.Fit()
            # Update view record
            self.currentview = wx.ID_NO
            # Force axis update
            self.axis_canvas.cycles = self.cycles_completed
            self.axis_canvas.render()

    def on_3D(self, event):
        """Handle event when user clicks 3D view button"""
        if self.currentview == wx.ID_NO:
            # Hide 2D view
            self.canv_feed_sizer.Hide(0)
            # Show 3D view
            self.canv_feed_sizer.Show(1)
            # Reload
            self.main_sizer.Layout()
            self.Fit()
            # Update view record
            self.currentview = wx.ID_YES

    def on_reset(self, event):
        """Handle event when user clicks rest view"""
        # If 3D, reset rotation and pan variables.
        if self.currentview == wx.ID_YES:
            self.my3D_canvas.reset_pan()
        # If 2D, reset pan vairbles in all canvases.
        if self.currentview == wx.ID_NO:
            MyOpenGLCanvas.pan_x = 0
            MyOpenGLCanvas.pan_y = 0
            self.traces_canvas.init = False
            self.axis_canvas.init = False
            self.labels_canvas.init = False
            self.traces_canvas.Refresh()
            self.axis_canvas.Refresh()
            self.labels_canvas.Refresh()

    def on_run_button(self, event):
        """Run the simulation from scratch when user clicks Run button."""
        self.cycles_completed = 0
        cycles = self.cycles.GetValue()

        if cycles is not None:  # if the number of cycles provided is valid
            self.monitors.reset_monitors()  # Clear previously stored signals
            self.devices.cold_startup()  # Random initialisation
            if self._run_network(cycles):
                self.act_log.AppendText("".join([_("Running for "),
                                                 str(cycles), _(" cycles")]) +
                                        '\n')
                self.cycles_completed += cycles
                # Update pan variable to ensure new plot
                # not generated off screen.
                MyOpenGLCanvas.pan_x = 0
                self.traces_canvas.init = False
                self.axis_canvas.init = False
                self.labels_canvas.init = False
                self._re_render()  # Update plots

    def on_continue_button(self, event):
        """Continue a previously run simulation."""
        cycles = self.cycles.GetValue()
        if cycles is not None:  # if the number of cycles provided is valid
            if self.cycles_completed == 0:
                self.act_log.AppendText(
                    _("Error! Nothing to continue. Run first.") + '\n')
            elif self._run_network(cycles):
                self.cycles_completed += cycles
                self._re_render()  # Update plots
                self.act_log.AppendText("".join([_("Continuing for "),
                                                 str(cycles),
                                                 _(" cycles."), _(" Total:"),
                                                 str(self.cycles_completed)]) +
                                        '\n')

    def on_config_button(self, event):
        """Handle the event when the user clicks the apply button."""
        # Gather device id of device user wants to configure and
        # configure variable.
        config = self.config_var.GetValue()
        dev_id = self.configurable[1][self.config_list.GetSelection()]

        # Validate configure variable based on device type selected
        if self.devices.get_device(dev_id).device_kind == self.devices.SWITCH:
            switch_state = self._verify_number(config, 0, 1)
            if switch_state is not None:
                # Changing switch state.
                if self.devices.set_switch(dev_id, switch_state):
                    print("Successfully set switch " +
                          self.names.get_name_string(dev_id) +
                          "\n")
                    dv_id = dev_id  # pep8
                    self.act_log.AppendText(_("Successfully set switch ") +
                                            self.names.get_name_string(dv_id) +
                                            "\n")
                    self.configurable[2][
                        self.config_list.GetSelection()] = switch_state

                else:
                    print("Error! Invalid switch." + "\n")
                    self.act_log.AppendText(_("Error! Invalid switch.") + "\n")
            else:
                print("Error! Switch state must be " +
                      "0 (OFF) or 1 (ON)." + "\n")
                self.act_log.AppendText(_("Error! Switch state must be ") +
                                        _("0 (OFF) or 1 (ON).") + "\n")
        elif (self.devices.get_device(dev_id).device_kind ==
              self.devices.CLOCK):
            print("Changing clock half-period")
            half_period = self._verify_number(config, 1, None)
            if half_period is not None:
                # Changing clock period.
                if self.devices.set_clock(dev_id, half_period):
                    print(
                        "Successfully set CLOCK " +
                        self.names.get_name_string(dev_id) +
                        " half-period to " + str(config) + "\n")
                    self.act_log.AppendText(
                        _("Successfully set CLOCK ") +
                        self.names.get_name_string(dev_id) +
                        _(" half-period to ") + str(config) + "\n")
                    self.configurable[2][
                        self.config_list.GetSelection()] = half_period
                else:
                    print("Error! Invalid CLOCK." + "\n")
                    self.act_log.AppendText(_("Error! Invalid CLOCK.") + "\n")
            else:
                print("Error! CLOCK half-period must be " +
                      "positive integer" + "\n")
                self.act_log.AppendText(_("Error! CLOCK" +
                                          "half-period must be ") +
                                        _("positive integer") + "\n")
        self._re_render()  # Update plots

    def on_show(self, event):
        """
        Set the selected outputs to be monitored. Called in
        reponse to user clicking 'Show'.
        """
        # Get list indicies of outputs selected by user
        selected = self.outs.GetSelections()
        for i in selected:
            # Find names id from GUI list id
            monitor = self.outputs[1][i]
            if monitor is not None:
                [device, port] = monitor
                monitor_error = self.monitors.make_monitor(
                    device, port, self.cycles_completed)
                if monitor_error == self.monitors.NO_ERROR:
                    # print("Successfully made monitor.")
                    self.act_log.AppendText(
                        _("Successfully made monitor.") + '\n')
                    # Update monitored output gui list.
                    self._regen_monitored(monitor)
                else:
                    # print("Error! Could not make monitor.")
                    self.act_log.AppendText(_("Error! Monitor already ") +
                                            _("selected.") + '\n')
        self._re_render()

    def on_remove(self, event):
        """
        Remove selected monitored outputs. Called in
        reponse to user clicking 'Remove'.
        """
        # Get list indicies of outputs selected by user
        to_remove = self.mons.GetSelections()
        # Remove selected monitors in reverse order to
        # ensure indicies are not out of range.
        for i in to_remove[::-1]:
            # Find names id from GUI list id
            monitor = self.monitored[1][i]
            if monitor is not None:
                [device, port] = monitor
                if self.monitors.remove_monitor(device, port):
                    self.act_log.AppendText(_("Successfully zapped monitor") +
                                            '\n')
                    # Remove from displayed and internal lists.
                    self.mons.Delete(i)
                    self.monitored[0].pop(i)
                    self.monitored[1].pop(i)
                else:
                    # print("Error! Could not zap monitor.")
                    self.act_log.AppendText(
                        _("Error! Could not zap monitor.") +
                        '\n')
        # Remove relevant traces.
        self._re_render()

    def _get_file_name(self, path_name):
        """ Gets file name from file path """
        file_name = ""
        for c in path_name[::-1]:
            if c != '/':
                file_name += c
            else:
                break
        file_name = file_name[::-1]
        return file_name

    def on_open(self):
        """Handles user event to open a new file"""
        # otherwise ask the user what new file to open
        with wx.FileDialog(self, _("Open Text file"),
                           wildcard=_("Text files") + "(*.txt)|*.txt",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) \
                as fileDialog:

            if fileDialog.ShowModal() == wx.ID_EXIT:
                return  # the user changed their mind

            # Proceed loading the file chosen by the user
            path_name = fileDialog.GetPath()
            # Extract file name from path, show in title.
            # Second Interim Report Feedback Update: Show current file.
            self.SetTitle("Logic Simulator - " +
                          self._get_file_name(path_name))
        self.path = path_name
        self.on_reload(None, True)

    def on_reload(self, event, new=False):
        """
        Handles loading of circuit specification file.
        Called when new file loaded or current file reloaded.
        """
        # Create new render
        self.cycles_completed = 0
        self.start = (0, 0)
        self.names = Names()
        self.devices = Devices(self.names)
        self.network = Network(self.names, self.devices)
        self.monitors = Monitors(self.names, self.devices,
                                 self.network)
        self.scanner = Scanner(self.path, self.names)
        self.parser = Parser(self.names, self.devices,
                             self.network, self.monitors,
                             self.scanner)
        if self.parser.parse_network():
            self.run_button.Enable()
            self.continue_button.Enable()
            self.config_button.Enable()
            self.add_outs.Enable()
            self.dele_mons.Enable()
            self.view2D.Enable()
            self.view3D.Enable()
            self.reset.Enable()
            [self.outputs, self.configurable,
                self.monitored] = self._gen_lists()
            self.outs.Set(self.outputs[0])

            # Added after discovering application crashes
            # when SIGGEN circuit loaded. Before this every
            # ciruit had to include a configurable device.
            if len(self.configurable[0]) > 0:
                self.config_list.Set(self.configurable[0])
                self.config_list.SetSelection(0)
                self.config_var.SetValue(self.configurable[2][0])
            else:
                self.config_var.SetValue(0)
                self.config_list.Clear()
                self.config_button.Disable()

            self.mons.Set(self.monitored[0])
            # Ensure pan variables are restored,
            # and new file loaded in both views.
            self.on_reset(None)
            self._re_render()
            if self.currentview == wx.ID_YES:
                self.on_2D(None)
            else:
                self.on_3D(None)
            self.on_reset(None)
            self._re_render()
            if self.currentview == wx.ID_NO:
                self.on_3D(None)
            else:
                self.on_2D(None)
            self.act_log.Clear()
            if new:
                self.act_log.AppendText(_("Successfully loaded new file!") +
                                        "\n")
            else:
                self.act_log.AppendText(_("Successfully reloaded file!") +
                                        "\n")
        else:
            self.act_log.Clear()
            # if new:
            #     self.act_log.AppendText(_("Unsuccessful Load!")+ "\n\n")
            # else:
            #     self.act_log.AppendText(_("Unsuccessful Reload!")+ "\n\n")
            for err_msg in self.parser.print_gui:
                self.act_log.AppendText(_(err_msg))
            self.act_log.AppendText(_(self.scanner.broken_comment_msg) + '\n')
            self.act_log.AppendText(_("***ERROR: Circuit could not ") +
                                    _("be parsed. Try again") + "\n\n\n")
            self.run_button.Disable()
            self.continue_button.Disable()
            self.config_button.Disable()
            self.add_outs.Disable()
            self.dele_mons.Disable()
            self.view2D.Disable()
            self.view3D.Disable()
            self.reset.Disable()
            # Delete traces
            self.names = None
            self.devices = None
            self.network = None
            # Set devices and monitors on the right canvas to None
            self.config_list.SetValue("")
            self.outputs = [[] for i in range(2)]
            self.configurable = [[] for i in range(2)]
            self.monitored = [[] for i in range(2)]
            self.outs.Clear()
            self.config_list.Clear()
            self.mons.Clear()
            self.on_reset(None)
            self._re_render()
            if self.currentview == wx.ID_YES:
                self.on_2D(None)
            else:
                self.on_3D(None)
            self.on_reset(None)
            self._re_render()
            if self.currentview == wx.ID_NO:
                self.on_3D(None)
            else:
                self.on_2D(None)

    def updateLanguage(self, lang):
        """
        Update the language to the requested one.

        Make *sure* any existing locale is deleted before the new
        one is created.  The old C++ object needs to be deleted
        before the new one is created, and if we just assign a new
        instance to the old Python variable, the old C++ locale will
        not be destroyed soon enough, likely causing a crash.

        :param string `lang`: one of the supported language codes

        """
        # if an unsupported language is requested default to English
        if lang in appC.supLang:
            selLang = appC.supLang[lang]
        else:
            selLang = wx.LANGUAGE_DEFAULT

        if self.locale:
            assert sys.getrefcount(self.locale) <= 2
            del self.locale

        # create a locale object for this language
        self.locale = wx.Locale(selLang)
        if self.locale.IsOk():
            self.locale.AddCatalog(appC.langDomain)
            # self.act_log.AppendText("updated")
        else:
            self.locale = None

    def _update_Labels(self):
        """Updates labels in GUI to selected language."""
        self.run_button.SetLabel(_("Run"))
        self.continue_button.SetLabel(_("Continue"))
        self.config_button.SetLabel(_("Apply"))
        self.add_outs.SetLabel(_("Show"))
        self.dele_mons.SetLabel(_("Remove"))
        self.view2D.SetLabel(_("2D View"))
        self.view3D.SetLabel(_("3D View"))
        self.reset.SetLabel(_("Reset View"))
        self.reload.SetLabel(_("Reload File"))

        self.uf.SetLabel(_("Activity Log"))
        self.cyc.SetLabel(_("Cycles"))
        self.conf.SetLabel(_("Configure Devices"))
        self.out.SetLabel(_("Outputs"))
        self.mon.SetLabel(_("Monitored Outputs"))

        self.fileMenu.SetLabel(wx.ID_ABOUT, _(u"&About"))
        self.fileMenu.SetLabel(wx.ID_EXIT, _(u"&Exit"))
        self.fileMenu.SetLabel(wx.ID_OPEN, _(u"&Open"))
        self.viewMenu.SetLabel(wx.ID_NO, _("2D Display"))
        self.viewMenu.SetLabel(wx.ID_YES, _("3D Display"))
        self.langMenu.SetLabel(self.id_en, _(u"&English"))
        self.langMenu.SetLabel(self.id_ro, _(u"&Română"))
        self.menuBar.SetMenuLabel(0, _(u"&File"))
        self.menuBar.SetMenuLabel(1, _(u"View"))
        self.menuBar.SetMenuLabel(2, _(u"Language"))

        self.main_sizer.Layout()
        self.Fit()
