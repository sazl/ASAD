from PySide import QtCore, QtGui
import interactive
import config

#-------------------------------------------------------------------------------

def browse(parent=None, isdir=True):
    directory = None
    if isdir:
        directory = QtGui.QFileDialog.getExistingDirectory(
            parent, "Find Directory", QtCore.QDir.currentPath())
    else:
        directory = QtGui.QFileDialog.getOpenFileNames(
            parent, "Find Files", QtCore.QDir.currentPath())
    return directory

def browseChangeComboBox(combo_box, isdir=True):
    def func(parent=None):
        directory = browse(parent, isdir)
        if directory:
            if not isdir:
                directory = directory[0][0]
            if combo_box.findText(directory) == -1:
                combo_box.addItem(directory)
            combo_box.setCurrentIndex(combo_box.findText(directory))
    return func

def comboBoxAddText(combo_box, text):
    combo_box.addItem(text)
    combo_box.setCurrentIndex(combo_box.findText(text))

def createLabel(text, wrap=True):
    label = QtGui.QLabel(text)
    label.setWordWrap(wrap)
    return label

def createButton(text, action):
    button = QtGui.QPushButton(text)
    button.clicked.connect(action)
    return button

def createLineEdit():
    return QtGui.QLineEdit()

def createComboBox(items=None):
    combo_box = QtGui.QComboBox()
    combo_box.setEditable(True)
    combo_box.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
    if items is not None:
        combo_box.addItems(items)
    return combo_box

def createCheckBox(text=""):
    return QtGui.QCheckBox(text)

def createErrorDialog(parent=None, text=''):
    return QtGui.QMessageBox.critical(parent, 'Error', text, QtGui.QMessageBox.Ok)

#-------------------------------------------------------------------------------

globalRunShell = None

def getRunShell():
    global globalRunShell
    if globalRunShell:
        return globalRunShell
    else:
        globalRunShell = interactive.Run_Shell()
        return globalRunShell

def readConfig():
    return config.GlobalConfig()

#-------------------------------------------------------------------------------

class AsadWizard(QtGui.QWizard):
    def __init__(self, parent=None):
        interactive.set_not_interactive()
        super(AsadWizard, self).__init__()
        self.addPage(IntroPage())
        self.addPage(ModelPage())
        self.addPage(ObservationPage())
        self.addPage(ObjectPage())
        self.addPage(PlotPage())

#-------------------------------------------------------------------------------

class IntroPage(QtGui.QWizardPage):
    def __init__(self, parent=None):
        super(IntroPage, self).__init__()
        self.setTitle("ASAD Introduction")
        self.setSubTitle("This wizard will guide you through the ASAD program.")

#-------------------------------------------------------------------------------

class ModelPage(QtGui.QWizardPage):
    def __init__(self, parent=None):
        super(ModelPage, self).__init__()
        self.setTitle("Model")
        self.setSubTitle("Model Options")
        self.createWidgets()
        self.registerWidgets()
        self.initializeLayout()
        self.initializeWidgets()

    def createWidgets(self):
        self.model_read_label = createLabel("Input File")
        self.model_read_combo_box = createComboBox()
        self.model_browse_button = createButton(
            "&Browse...", browseChangeComboBox(self.model_read_combo_box, False))
        self.model_smoothen_label = createLabel("Interpolation Step")
        self.model_smoothen_input = createLineEdit()
        self.model_interpolation_wavelength_start_label = createLabel("Interpolation Wavelength Start");
        self.model_interpolation_wavelength_start_input = createLineEdit()
        self.model_wavelength_range_start_label = createLabel("Wavelength Start")
        self.model_wavelength_range_start_input = createLineEdit()
        self.model_wavelength_range_end_label = createLabel("Wavelength End")
        self.model_wavelength_range_end_input = createLineEdit()
        self.model_normalize_label = createLabel("Normalize Wavelength")
        self.model_normalize_input = createLineEdit()
        self.model_normalize_check = createCheckBox()
        self.model_output_label = createLabel("Output Directory")
        self.model_output_combo_box = createComboBox()
        self.model_output_browse_button = createButton(
            "&Browse...", browseChangeComboBox(self.model_output_combo_box))

    def initializeWidgets(self):
        globalConfig = readConfig()
        comboBoxAddText(self.model_read_combo_box, globalConfig['model_input_directory'])
        self.model_interpolation_wavelength_start_input.insert(globalConfig['model_interpolation_wavelength_start'])
        self.model_smoothen_input.insert(globalConfig['model_interpolation_step'])
        self.model_wavelength_range_start_input.insert(globalConfig['model_wavelength_start'])
        self.model_wavelength_range_end_input.insert(globalConfig['model_wavelength_end'])
        self.model_normalize_input.insert(globalConfig['model_normalize_wavelength'])
        comboBoxAddText(self.model_output_combo_box, globalConfig['model_output_directory'])
    
    def registerWidgets(self):
        self.registerField("model_read_combo_box", self.model_read_combo_box)
        self.registerField("model_interpolation_wavelength_start_input",
                           self.model_interpolation_wavelength_start_input)
        self.registerField("model_smoothen_input", self.model_smoothen_input)
        self.registerField("model_wavelength_range_start_input",
                           self.model_wavelength_range_start_input)
        self.registerField("model_wavelength_range_end_input",
                           self.model_wavelength_range_end_input)
        self.registerField("model_normalize_input", self.model_normalize_input)
        self.registerField("model_normalize_check", self.model_normalize_check)
        self.registerField("model_output_combo_box", self.model_output_combo_box)
    
    def initializeLayout(self):
        layout = QtGui.QGridLayout()
        layout.addWidget(self.model_read_label, 0, 0)
        layout.addWidget(self.model_read_combo_box, 0, 1)
        layout.addWidget(self.model_browse_button, 0, 2)
        layout.addWidget(self.model_interpolation_wavelength_start_label, 1, 0)
        layout.addWidget(self.model_interpolation_wavelength_start_input, 1, 1)
        layout.addWidget(self.model_smoothen_label, 2, 0)
        layout.addWidget(self.model_smoothen_input, 2, 1)
        layout.addWidget(self.model_wavelength_range_start_label, 3, 0)
        layout.addWidget(self.model_wavelength_range_start_input, 3, 1)
        layout.addWidget(self.model_wavelength_range_end_label, 4, 0)
        layout.addWidget(self.model_wavelength_range_end_input, 4, 1)
        layout.addWidget(self.model_normalize_label, 5, 0)
        layout.addWidget(self.model_normalize_input, 5, 1)
        layout.addWidget(self.model_normalize_check, 5, 2)
        layout.addWidget(self.model_output_label, 6, 0)
        layout.addWidget(self.model_output_combo_box, 6, 1)
        layout.addWidget(self.model_output_browse_button, 6, 2)
        self.setLayout(layout)

    def validatePage(self):
        try:
            self.interpolation_wavelength_start = float(self.model_interpolation_wavelength_start_input.text())
            self.interpolation_step = float(self.model_smoothen_input.text())
            self.wavelength_start = float(self.model_wavelength_range_start_input.text())
            self.wavelength_end = float(self.model_wavelength_range_end_input.text())
            self.wavelength_normalize = float(self.model_normalize_input.text())
            self.commitPage()
            return True
        except Exception as e:
            createErrorDialog(parent=self, text=unicode(e))
            print e
            return False

    def commitPage(self):
        globalConfig = readConfig()
        globalConfig['model_input_directory'] = self.model_read_combo_box.currentText()
        globalConfig['model_interpolation_wavelength_start'] = self.interpolation_wavelength_start
        globalConfig['model_interpolation_step'] = unicode(self.interpolation_step)
        globalConfig['model_wavelength_start'] = unicode(self.wavelength_start)
        globalConfig['model_wavelength_end'] = unicode(self.wavelength_end)
        globalConfig['model_normalize_wavelength'] = unicode(self.wavelength_normalize)
        globalConfig['model_output_directory'] = self.model_output_combo_box.currentText()
        globalConfig.write_config_file()
        runShell = getRunShell()
        runShell.model_read()
        runShell.model_interpolation_wavelength_start()
        runShell.model_smoothen()
        runShell.model_wavelength_range()
        runShell.model_normalize_wavelength()
        runShell.model_output()
        runShell.update_config()

#-------------------------------------------------------------------------------

class ObservationPage(QtGui.QWizardPage):

    def __init__(self, parent=None):
        super(ObservationPage, self).__init__()
        self.setTitle("Observation")
        self.setSubTitle("Observations Options")
        self.createWidgets()
        self.registerWidgets()
        self.initializeLayout()
        self.initializeWidgets()

    def createWidgets(self):
        self.observation_read_label = createLabel("Input Directory")
        self.observation_read_combo_box = createComboBox()
        self.observation_browse_button = createButton(
            "&Browse...", browseChangeComboBox(self.observation_read_combo_box))
        self.observation_smoothen_label = createLabel("Interpolation Step")
        self.observation_smoothen_input = createLineEdit()
        self.observation_interpolation_wavelength_start_label = createLabel("Interpolation Wavelength Start");
        self.observation_interpolation_wavelength_start_input = createLineEdit()
        self.observation_reddening_start_label = createLabel("Reddening Start")
        self.observation_reddening_start_input = createLineEdit()
        self.observation_reddening_end_label = createLabel("Reddening End")
        self.observation_reddening_end_input = createLineEdit()
        self.observation_reddening_step_label = createLabel("Reddening Step")
        self.observation_reddening_step_input = createLineEdit()
        self.observation_wavelength_range_start_label = createLabel("Wavelength Start")
        self.observation_wavelength_range_start_input = createLineEdit()
        self.observation_wavelength_range_end_label = createLabel("Wavelength End")
        self.observation_wavelength_range_end_input = createLineEdit()
        self.observation_normalize_label = createLabel("Normalize Wavelength")
        self.observation_normalize_input = createLineEdit()
        self.observation_normalize_check = createCheckBox()
        self.observation_output_label = createLabel("Output Directory")
        self.observation_output_combo_box = createComboBox()
        self.observation_output_browse_button = createButton(
            "&Browse...", browseChangeComboBox(self.observation_output_combo_box))

    def initializeWidgets(self):
        globalConfig = readConfig()
        comboBoxAddText(self.observation_read_combo_box, globalConfig['observation_input_directory'])
        self.observation_interpolation_wavelength_start_input.insert(globalConfig['observation_interpolation_wavelength_start'])
        self.observation_smoothen_input.insert(globalConfig['observation_interpolation_step'])
        self.observation_reddening_start_input.insert(globalConfig['observation_reddening_start'])
        self.observation_reddening_step_input.insert(globalConfig['observation_reddening_step'])
        self.observation_reddening_end_input.insert(globalConfig['observation_reddening'])
        self.observation_wavelength_range_start_input.insert(globalConfig['observation_wavelength_start'])
        self.observation_wavelength_range_end_input.insert(globalConfig['observation_wavelength_end'])
        self.observation_normalize_input.insert(globalConfig['observation_normalize_wavelength'])
        comboBoxAddText(self.observation_output_combo_box, globalConfig['observation_output_directory'])

    def registerWidgets(self):
        self.registerField("observation_read_combo_box", self.observation_read_combo_box)
        self.registerField("observation_interpolation_wavelength_start_input",
                           self.observation_interpolation_wavelength_start_input)
        self.registerField("observation_smoothen_input", self.observation_smoothen_input)
        self.registerField("observation_reddening_start_input",
                           self.observation_reddening_start_input)
        self.registerField("observation_reddening_end_input",
                           self.observation_reddening_end_input)
        self.registerField("observation_reddening_step_input",
                           self.observation_reddening_step_input)
        self.registerField("observation_wavelength_range_start_input",
                           self.observation_wavelength_range_start_input)
        self.registerField("observation_wavelength_range_end_input",
                           self.observation_wavelength_range_end_input)
        self.registerField("observation_normalize_input", self.observation_normalize_input)
        self.registerField("observation_normalize_check", self.observation_normalize_check)
        self.registerField("observation_output_combo_box", self.observation_output_combo_box)

    def initializeLayout(self):
        layout = QtGui.QGridLayout()
        layout.addWidget(self.observation_read_label, 0, 0)
        layout.addWidget(self.observation_read_combo_box, 0, 1)
        layout.addWidget(self.observation_browse_button, 0, 2)
        layout.addWidget(self.observation_interpolation_wavelength_start_label, 1, 0)
        layout.addWidget(self.observation_interpolation_wavelength_start_input, 1, 1)
        layout.addWidget(self.observation_smoothen_label, 2, 0)
        layout.addWidget(self.observation_smoothen_input, 2, 1)
        layout.addWidget(self.observation_reddening_start_label, 3, 0)
        layout.addWidget(self.observation_reddening_start_input, 3, 1)
        layout.addWidget(self.observation_reddening_end_label, 4, 0)
        layout.addWidget(self.observation_reddening_end_input, 4, 1)
        layout.addWidget(self.observation_reddening_step_label, 5, 0)
        layout.addWidget(self.observation_reddening_step_input, 5, 1)
        layout.addWidget(self.observation_wavelength_range_start_label, 6, 0)
        layout.addWidget(self.observation_wavelength_range_start_input, 6, 1)
        layout.addWidget(self.observation_wavelength_range_end_label, 7, 0)
        layout.addWidget(self.observation_wavelength_range_end_input, 7, 1)
        layout.addWidget(self.observation_normalize_label, 8, 0)
        layout.addWidget(self.observation_normalize_input, 8, 1)
        layout.addWidget(self.observation_normalize_check, 8, 2)
        layout.addWidget(self.observation_output_label, 9, 0)
        layout.addWidget(self.observation_output_combo_box, 9, 1)
        layout.addWidget(self.observation_output_browse_button, 9, 2)
        self.setLayout(layout)

    def validatePage(self):
        try:
            self.interpolation_wavelength_start = float(self.observation_interpolation_wavelength_start_input.text())
            self.interpolation_step = float(self.observation_smoothen_input.text())
            self.reddening_start = float(self.observation_reddening_start_input.text())
            self.reddening_end = float(self.observation_reddening_end_input.text())
            self.reddening_step = float(self.observation_reddening_step_input.text())
            self.wavelength_start = float(self.observation_wavelength_range_start_input.text())
            self.wavelength_end = float(self.observation_wavelength_range_end_input.text())
            self.wavelength_normalize = float(self.observation_normalize_input.text())
            self.commitPage()
            return True
        except Exception as err:
            createErrorDialog(parent=self, text=unicode(err))
            return False

    def commitPage(self):
        globalConfig = readConfig()
        globalConfig['observation_input_directory'] = self.observation_read_combo_box.currentText()
        globalConfig['observation_interpolation_wavelength_start'] = self.interpolation_wavelength_start
        globalConfig['observation_interpolation_step'] = unicode(self.interpolation_step)
        globalConfig['observation_reddening_start'] = self.reddening_start
        globalConfig['observation_reddening_step'] = self.reddening_step
        globalConfig['observation_reddening'] = self.reddening_end
        globalConfig['observation_wavelength_start'] = self.wavelength_start
        globalConfig['observation_wavelength_end'] = self.wavelength_end
        globalConfig['observation_normalize_wavelength'] = self.wavelength_normalize
        globalConfig['observation_output_directory'] = self.observation_output_combo_box.currentText()
        globalConfig.write_config_file()
        runShell = getRunShell()
        runShell.observation_read()
        runShell.observation_interpolation_wavelength_start()
        runShell.observation_smoothen()        
        runShell.observation_reddening()
        runShell.observation_wavelength_range()
        runShell.observation_normalize_wavelength()
        runShell.observation_output()
        runShell.update_config()

#-------------------------------------------------------------------------------

class ObjectPage(QtGui.QWizardPage):

    def __init__(self, parent=None):
        super(ObjectPage, self).__init__()
        self.setTitle("Combined Model and Object")
        self.setSubTitle("Combined Options")
        self.createWidgets()
        self.registerWidgets()
        self.initializeLayout()
        self.initializeWidgets()

    def createWidgets(self):
        self.object_output_label = createLabel("Output Directory")
        self.object_output_combo_box = createComboBox()
        self.object_browse_button = createButton(
            "&Browse...", browseChangeComboBox(self.object_output_combo_box))
        self.object_output_chosen_label = createLabel("Output Chosen Directory")
        self.object_output_chosen_combo_box = createComboBox()
        self.object_chosen_browse_button = createButton(
            "&Browse...", browseChangeComboBox(self.object_output_chosen_combo_box))

    def initializeWidgets(self):
        globalConfig = readConfig()
        comboBoxAddText(self.object_output_combo_box, globalConfig['object_output_directory'])
        comboBoxAddText(self.object_output_chosen_combo_box, globalConfig['object_chosen_directory'])

    def registerWidgets(self):
        self.registerField("object_output_combo_box", self.object_output_combo_box)
        self.registerField("object_output_chosen_combo_box", self.object_output_combo_box)

    def initializeLayout(self):
        layout = QtGui.QGridLayout()
        layout.addWidget(self.object_output_label, 0, 0)
        layout.addWidget(self.object_output_combo_box, 0, 1)
        layout.addWidget(self.object_browse_button, 0, 2)
        layout.addWidget(self.object_output_chosen_label, 1, 0)
        layout.addWidget(self.object_output_chosen_combo_box, 1, 1)
        layout.addWidget(self.object_chosen_browse_button, 1, 2)
        self.setLayout(layout)
        
    def validatePage(self):
        try:
            self.commitPage()
            return True
        except Exception as err:
            createErrorDialog(parent=self, text=unicode(err))
            return False

    def commitPage(self):
        globalConfig = readConfig()
        globalConfig['object_output_directory'] = self.object_output_combo_box.currentText()
        globalConfig['object_chosen_directory'] = self.object_output_chosen_combo_box.currentText()
        globalConfig.write_config_file()
        runShell = getRunShell()
        runShell.object_generate()
        runShell.object_output()
        runShell.object_calculate_chosen()
        runShell.object_output_chosen()
        runShell.update_config()

#-------------------------------------------------------------------------------

class PlotPage(QtGui.QWizardPage):
    
    OUTPUT_FORMATS = ['png', 'eps', 'pdf', 'jpeg', 'bmp']
    
    def __init__(self, parent=None):
        super(PlotPage, self).__init__()
        self.setTitle("Plot")
        self.setSubTitle("Plot Options")
        self.createWidgets()
        self.registerWidgets()
        self.initializeLayout()
        self.initializeWidgets()

    def createWidgets(self):
        self.plot_output_format_label = createLabel("Output Format")
        self.plot_output_format_combo_box = createComboBox()
        self.plot_output_format_combo_box.addItems(PlotPage.OUTPUT_FORMATS)
        self.plot_output_surface_label = createLabel("Output Surface")
        self.plot_output_surface_combo_box = createComboBox()
        self.plot_output_surface_browse = createButton(
            '&Browse...', browseChangeComboBox(self.plot_output_surface_combo_box))
        self.plot_output_scatter_label = createLabel("Output Scatter")
        self.plot_output_scatter_combo_box = createComboBox()
        self.plot_output_scatter_browse = createButton(
            '&Browse...', browseChangeComboBox(self.plot_output_scatter_combo_box))
        self.plot_output_residual_label = createLabel("Output Residual")
        self.plot_output_residual_combo_box = createComboBox()
        self.plot_output_residual_browse = createButton(
            '&Browse...', browseChangeComboBox(self.plot_output_residual_combo_box))
        self.plot_output_surface_error_label = createLabel("Output Surface Error")
        self.plot_output_surface_error_combo_box = createComboBox()
        self.plot_output_surface_error_browse = createButton(
            '&Browse...', browseChangeComboBox(self.plot_output_surface_error_combo_box))

    def initializeWidgets(self):
        globalConfig = readConfig()
        comboBoxAddText(self.plot_output_format_combo_box, globalConfig['plot_output_format'])
        comboBoxAddText(self.plot_output_surface_combo_box, globalConfig['plot_surface_directory'])
        comboBoxAddText(self.plot_output_scatter_combo_box, globalConfig['plot_scatter_directory'])
        comboBoxAddText(self.plot_output_residual_combo_box, globalConfig['plot_residual_directory'])
        comboBoxAddText(self.plot_output_surface_error_combo_box, globalConfig['plot_surface_error_directory'])

    def registerWidgets(self):
        self.registerField('plot_output_format_combo_box', self.plot_output_format_combo_box)
        self.registerField('plot_output_surface_combo_box', self.plot_output_surface_combo_box)
        self.registerField('plot_output_scatter_combo_box', self.plot_output_scatter_combo_box)
        self.registerField('plot_output_residual_combo_box', self.plot_output_residual_combo_box)
        self.registerField('plot_output_surface_error_combo_box', self.plot_output_surface_error_combo_box)

    def initializeLayout(self):
        layout = QtGui.QGridLayout()
        layout.addWidget(self.plot_output_format_label, 0, 0)
        layout.addWidget(self.plot_output_format_combo_box, 0, 1)
        layout.addWidget(self.plot_output_surface_label, 1, 0)
        layout.addWidget(self.plot_output_surface_combo_box, 1, 1)
        layout.addWidget(self.plot_output_surface_browse, 1, 2)
        layout.addWidget(self.plot_output_scatter_label, 2, 0)
        layout.addWidget(self.plot_output_scatter_combo_box, 2, 1)
        layout.addWidget(self.plot_output_scatter_browse, 2, 2)
        layout.addWidget(self.plot_output_residual_label, 3, 0)
        layout.addWidget(self.plot_output_residual_combo_box, 3, 1)
        layout.addWidget(self.plot_output_residual_browse, 3, 2)
        layout.addWidget(self.plot_output_surface_error_label, 4, 0)
        layout.addWidget(self.plot_output_surface_error_combo_box, 4, 1)
        layout.addWidget(self.plot_output_surface_error_browse, 4, 2)
        self.setLayout(layout)

    def validatePage(self):
        try:
            self.commitPage()
            return True
        except Exception as err:
            createErrorDialog(parent=self, text=unicode(err))
            return False

    def commitPage(self):
        globalConfig = readConfig()
        globalConfig['plot_output_format'] = self.plot_output_format_combo_box.currentText()
        globalConfig['plot_surface_directory'] = self.plot_output_surface_combo_box.currentText()
        globalConfig['plot_scatter_directory'] = self.plot_output_scatter_combo_box.currentText()
        globalConfig['plot_residual_directory'] = self.plot_output_residual_combo_box.currentText()
        globalConfig['plot_surface_error_directory'] = self.plot_output_surface_error_combo_box.currentText()
        globalConfig.write_config_file()
        runShell = getRunShell()
        runShell.plot_output_format()
        runShell.plot_surface_output()
        runShell.plot_scatter_output_aux()
        runShell.plot_residual_output()
        runShell.plot_surface_error_output()
        runShell.update_config()

#-------------------------------------------------------------------------------

def init():
    import sys
    app = QtGui.QApplication(sys.argv)
    wizard = AsadWizard()
    sys.exit(wizard.exec_())
