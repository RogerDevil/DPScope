import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from portselect import get_port
from tkinter import (Tk, Frame, LabelFrame, BOTH, Button, Label, Spinbox, X,
                     LEFT, Scale, Checkbutton, BooleanVar, W, StringVar,
                     OptionMenu, Radiobutton, HORIZONTAL, IntVar, E)

import high
from model.controller.helper.trigger import TriggerSource
from model.controller.helper.voltage_measure import VoltageResolution
from view.director import Director
from view.builder.standard import StandardViewBuilder

root = Tk()
root.title("DPScope")
fig = Figure()


pltr = high.Plotter(fig)

class Datalogger(high.Task):
    def __init__(self, widget, interval):
        high.Task.__init__(self, widget, interval)
        self.ch1 = []
        self.ch2 = []

    def task(self):
        data = ch1, ch2 = pltr.volt_read()
        self.ch1.append(ch1)
        self.ch2.append(ch2)
        pltr.plot([], self.ch1, [], self.ch2)

stopfn = lambda: None

def start():
    global stopfn
    if view.signals['Horizontal.sample_mode'] in "Datalog mode":
        dl = Datalogger(root, 100)
        stopfn = dl.stop
        dl.start()

def stop():
    stopfn()


view_builder = Director(StandardViewBuilder())
view_builder.view_build()
view = view_builder.view_get()

pltr.scope = get_port(view.window)

with pltr.scope as dpscope:
    # defaults
    dpscope.trigger.source = TriggerSource.auto
    dpscope.voltages.resolution = VoltageResolution.low
    dpscope.gain_set(0, 0)
    dpscope.gain_set(1, 0)
    dpscope.pregain_set(0, 0)
    dpscope.pregain_set(1, 0)

    view.show()
