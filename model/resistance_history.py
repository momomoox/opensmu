"""Persistent, tab-separated overview of completed resistance sweeps."""
import csv
from datetime import datetime
from pathlib import Path


def append_resistance_history(folder, sample, result, raw_file, instrument, four_wire):
    path = Path(folder) / 'resistance_history.txt'
    columns = ['Date_Time', 'Sample_Name', 'R_Ohm', 'R_squared',
               'Fit_Standard_Error_Ohm', 'Offset_V', 'Points', 'Fit_Quality',
               'Instrument', 'Four_Wire', 'Raw_Data_File']
    # a+ preserves all existing rows across application restarts.
    with path.open('a+', encoding='utf-8', newline='') as handle:
        handle.seek(0, 2)
        empty = handle.tell() == 0
        writer = csv.writer(handle, delimiter='\t', lineterminator='\n')
        if empty:
            writer.writerow(columns)
        writer.writerow([
            datetime.now().astimezone().isoformat(timespec='seconds'),
            ' '.join(str(sample).split()) or 'Unnamed',
            format(result['resistance_ohm'], '.12g'),
            format(result['r_squared'], '.12g'),
            format(result['standard_error_ohm'], '.12g'),
            format(result['offset_V'], '.12g'), result['points'],
            'poor/non-ohmic' if result['r_squared'] < .99 else 'linear',
            instrument, four_wire, str(Path(raw_file).resolve())])
    return str(path.resolve())
