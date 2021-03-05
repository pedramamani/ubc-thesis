import iPlot
import iProcess
import iConstants
from cfgcontrol import CfgControl
import numpy as np


class CfgSpectrum(CfgControl):
    def __init__(self, filePath: str, control: 'CfgSpectrum' = None):
        super().__init__(filePath)

        if control:
            self.cfgParams = control.cfgParams.copy()
            self.freqs = control.freqs.copy()
            self._redSlice = control._redSlice
            self._blueSlice = control._blueSlice
