import os

if os.name == 'posix':
    from PI.visualization.MicroView.libMicroViewPython import *
else:
    from PI.visualization.MicroView.MicroViewPython import *
