from model.controller import DPScopeController
from multiprocessing.pool import ThreadPool
from tkinter import BooleanVar
from threading import Semaphore


class Task(object):

    def __init__(self, widget, interval):
        self.widget = widget
        self.interval = interval
        self.timer = None
        self.s = Semaphore()

    def start(self):
        self.s.acquire()
        self.timer = self.widget.after(self.interval, self.start)
        self.s.release()
        self.task()

    def stop(self):
        if self.timer:
            self.s.acquire()
            self.widget.after_cancel(self.timer)
            self.s.release()

class Plotter(object):

    def __init__(self, fig):
        self._scope = None
        self.fig = fig
        self.plt = fig.add_subplot(111)
        self.ch1, self.ch2 = self.plt.plot([], [], [], [])
        self.pool = ThreadPool()

        self.ch1b = BooleanVar()
        self.ch1b.set(True)

        self.ch2b = BooleanVar()
        self.ch2b.set(True)

        self._fft = BooleanVar()
        self._fft.set(False)

        self._xy = BooleanVar()
        self._xy.set(False)

        self._USB_voltage = None

    @property
    def scope(self):
        return self._scope

    @scope.setter
    def scope(self, port):
        self._scope = DPScopeController(port)

    @property
    def both_channels(self):
        return self.ch1b.get() and self.ch2b.get()

    @property
    def xy(self):
        return self._xy.get()

    @property
    def fft(self):
        return self._fft.get()
    
    @property
    def USB_voltage(self):
        return self._scope.voltages.usb

    def volt_read(self):
        return self._scope.volt_read()

    def poll(self):
        ch1, ch2 = self._scope.poll()
        if self.xy:
            self.plot(ch1, ch2, [], [])
        else:
            self.plot([], ch1, [], ch2)

    def plot(self, x1=[], y1=[], x2=[], y2=[]):
        if len(y1) and not len(x1):
            x1 = range(len(y1))

        if len(y2) and not len(x2):
            x2 = range(len(y2))

        self.ch1.set_data(x1, y1)
        self.ch2.set_data(x2, y2)

        self.plt.relim()
        self.plt.autoscale_view()
        self.fig.canvas.draw()
