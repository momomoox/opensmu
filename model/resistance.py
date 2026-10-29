"""Resistance regression independent of instrument and UI."""
import numpy as np


def fit_resistance(voltage, current):
    v, i = np.asarray(voltage, dtype=float), np.asarray(current, dtype=float)
    if v.shape != i.shape or v.ndim != 1 or len(v) < 3:
        raise ValueError('At least three paired measurements are required.')
    if not np.all(np.isfinite(v)) or not np.all(np.isfinite(i)):
        raise ValueError('Invalid or non-finite readings; fit rejected.')
    if np.any(np.abs(v) >= 1e30) or np.any(np.abs(i) >= 1e30):
        raise ValueError('Instrument overflow readings; fit rejected.')
    di, dv = i - i.mean(), v - v.mean()
    sii, svv = float(di @ di), float(dv @ dv)
    if sii == 0 or svv == 0:
        raise ValueError('No measurable current or voltage variation; fit unavailable.')
    r = float(di @ dv / sii)
    offset = float(v.mean() - r * i.mean())
    residual = v - (r * i + offset)
    r2 = float(1 - residual @ residual / svv)
    stderr = float(np.sqrt((residual @ residual) / (len(i) - 2) / sii))
    return {'resistance_ohm': r, 'offset_V': offset, 'r_squared': r2,
            'standard_error_ohm': stderr, 'points': len(i)}


def sweep_voltages(config):
    start, stop, step = (float(config[k]) for k in ('startV', 'stopV', 'stepV'))
    if not all(np.isfinite([start, stop, step])) or step == 0:
        raise ValueError('Sweep parameters must be finite, with nonzero step.')
    count = (stop - start) / step
    if count < 2 or count > 100000:
        raise ValueError('Use 3–100001 points and a step directed toward the stop voltage.')
    if not np.isclose(count, round(count), rtol=0, atol=1e-7):
        raise ValueError('Stop minus start must be an integer multiple of the step.')
    if config['current_range'] <= 0 or config['source_delay_ms'] < 0:
        raise ValueError('Current limit must be positive; delay cannot be negative.')
    if config['voltage_range'] and max(abs(start), abs(stop)) > config['voltage_range']:
        raise ValueError('Sweep exceeds selected voltage range.')
    return np.linspace(start, stop, round(count) + 1).tolist()
