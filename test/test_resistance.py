import numpy as np
import pytest
from model.resistance import fit_resistance, sweep_voltages
from model.smu_model import SMUModel


def test_offset_resistance():
    i = np.linspace(-0.001, 0.001, 21)
    result = fit_resistance(1234 * i + .003, i)
    assert result['resistance_ohm'] == pytest.approx(1234)
    assert result['offset_V'] == pytest.approx(.003)
    assert result['r_squared'] == pytest.approx(1)


@pytest.mark.parametrize('v,i', [([0, 1], [0, 1]), ([0, 1, 2], [0, 0, 0]),
                                ([0, 1, float('nan')], [0, 1, 2]),
                                ([0, 1, 2], [0, 1, 9.9e37])])
def test_invalid_fit(v, i):
    with pytest.raises(ValueError):
        fit_resistance(v, i)


def test_descending_and_bad_step():
    cfg = SMUModel().config['R']
    cfg.update(startV=.1, stopV=-.1, stepV=-.01)
    assert len(sweep_voltages(cfg)) == 21
    cfg['stepV'] = .01
    with pytest.raises(ValueError):
        sweep_voltages(cfg)


def test_simulation_sweep_file_and_shutdown(tmp_path):
    model = SMUModel()
    model.config['global']['meas_mode'] = 'R'
    model.config['global']['save_folder'] = str(tmp_path)
    model.config['R']['source_delay_ms'] = 0
    model.SMU.create_smu_connector('')
    model.r_starter()
    while not model.r_collect_data():
        pass
    result = model.finish_resistance()
    model.stoper()
    assert result['resistance_ohm'] == pytest.approx(1000, rel=.02)
    assert not model.SMU.output_on
    text = open(model.data.filepath).read()
    assert 'status=complete' in text and 'resistance_ohm=' in text


def test_current_limit_rejects_and_stops(tmp_path):
    model = SMUModel()
    model.config['global'].update(meas_mode='R', save_folder=str(tmp_path))
    model.config['R'].update(current_range=1e-8, source_delay_ms=0)
    model.r_starter()
    with pytest.raises(ValueError, match='limit'):
        model.r_collect_data()
    model.stoper()
    assert not model.SMU.output_on
    assert 'status=incomplete' in open(model.data.filepath).read()


def test_2450_uses_voltage_readback(tmp_path):
    from unittest.mock import MagicMock
    model = SMUModel()
    model.config['global'].update(smu_type='keithley2450', meas_mode='R', save_folder=str(tmp_path))
    model.config['R']['source_delay_ms'] = 0
    smu = MagicMock()
    smu.query_smu.side_effect = ['0,"No error"', '-0.099,-0.000099']
    model.SMU = smu
    model.r_starter()
    model.r_collect_data()
    assert model.data.x_vals == [-0.099]
    smu.write_smu.assert_any_call(':SENS:CURR:RSEN ON')
    smu.query_smu.assert_any_call(':READ? "defbuffer1", SOUR, READ')
    model.stoper()
    smu.set_output_off.assert_called_once()


def test_r_ui_roundtrip():
    from PyQt5.QtWidgets import QApplication
    from view.components.config_dialog import ConfigDialog
    from view.view import View
    app = QApplication.instance() or QApplication([])
    cfg = SMUModel().config
    cfg['global']['meas_mode'] = 'R'
    dialog = ConfigDialog(cfg)
    assert dialog.tabs_IV_RT.currentIndex() == 2
    assert dialog.get_config()['R']['four_wire'] is True
    view = View()
    view.plot_resistance([-.1, 0, .1], [-.0001, 0, .0001],
                         fit_resistance([-.1, 0, .1], [-.0001, 0, .0001]))
    assert 'Fit:' in view.figure.axes[0].get_legend_handles_labels()[1][1]
    dialog.deleteLater()
    view.deleteLater()
