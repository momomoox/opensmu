import csv
from pathlib import Path
from unittest.mock import patch
import pytest
from model.smu_model import SMUModel


def complete_run(folder, sample):
    model = SMUModel()
    model.config['global'].update(meas_mode='R', save_folder=str(folder))
    model.config['R'].update(sample_name=sample, source_delay_ms=0)
    model.r_starter()
    while not model.r_collect_data():
        pass
    model.finish_resistance()
    model.finish_resistance()  # Do not duplicate an already finalized run.
    model.stoper()
    return model


def test_history_persists_across_instances(tmp_path):
    a = complete_run(tmp_path, 'Sample A')
    b = complete_run(tmp_path, 'Sample\tB\nnext')
    path = tmp_path / 'resistance_history.txt'
    with path.open() as handle:
        rows = list(csv.DictReader(handle, delimiter='\t'))
    assert len(rows) == 2
    assert [r['Sample_Name'] for r in rows] == ['Sample A', 'Sample B next']
    assert rows[0]['Instrument'] == 'simulation'
    assert float(rows[0]['R_Ohm']) == pytest.approx(1000, rel=.02)
    assert a.data.filepath != b.data.filepath
    assert Path(rows[0]['Raw_Data_File']).is_file()
    assert '# sample_name=Sample A' in Path(a.data.filepath).read_text()


def test_stopped_sweep_has_no_history(tmp_path):
    model = SMUModel()
    model.config['global'].update(meas_mode='R', save_folder=str(tmp_path))
    model.r_starter()
    model.r_collect_data()
    model.stoper()
    assert not (tmp_path / 'resistance_history.txt').exists()


def test_history_failure_keeps_fit_and_raw(tmp_path):
    with patch('model.resistance_history.append_resistance_history', side_effect=PermissionError('locked')):
        model = complete_run(tmp_path, '')
    assert model.resistance_history_error == 'locked'
    assert model.resistance_result is not None
    raw = Path(model.data.filepath).read_text()
    assert '# status=complete' in raw and '# sample_name=Unnamed' in raw
    assert not model.SMU.output_on
