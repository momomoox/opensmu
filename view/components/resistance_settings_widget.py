from PyQt5 import QtWidgets as qtw
from .iv_settings_widget import IVSettingsWidget


class ResistanceSettingsWidget(IVSettingsWidget):
    """Independent voltage sweep and Kelvin sense settings for resistance."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sample_name = qtw.QLineEdit()
        self.sample_name.setPlaceholderText('e.g. Sample_A')
        self.layout.insertRow(0, 'Sample name', self.sample_name)
        self.current_range_label.setText('I range / current limit (A)')
        self.four_wire = qtw.QCheckBox('Four-wire (Kelvin): connect FORCE and SENSE leads')
        self.four_wire.setChecked(True)
        self.layout.addRow(self.four_wire)
        note = qtw.QLabel('Keithley 2450 (SCPI) or Simulation. Fits V = R·I + offset. '
                          'Use a small voltage range where the sample is ohmic.')
        note.setWordWrap(True)
        self.layout.addRow(note)

    def get_config(self):
        return {**super().get_config(), 'four_wire': self.four_wire.isChecked(),
                'sample_name': self.sample_name.text().strip()}

    def apply_config(self, config):
        super().apply_config(config)
        self.sample_name.setText(config.get('sample_name', ''))
        self.four_wire.setChecked(config.get('four_wire', True))
