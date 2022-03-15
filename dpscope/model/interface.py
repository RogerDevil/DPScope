import logging
from serial import Serial

from model.command import Command, CommandReadback, CommandSetDac

# Set up logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


class DPScopeInterface(object):
    """
    Interface for all DPScope commands.

    Exposes all API methods. The DPSCope has a microcontroller that accepts
    commands sent from a serial interface. Each command sequence is
    initiated by a different command number. This class is responsible for
    formatting the command data packet for every command available, sending
    it, and receiving any data from the DPScope.
    """
    _conn = None  # serial connection to DPScope.

    def __init__(self, port):
        """
        Instantiates interface to DPScope.

        Sets up all API commands.

        Args:
            port (int): Port num to create socket with.
        """
        self._conn = Serial(port, 500000, timeout=1)

        # 0 byte
        self.read_adc = Command(self._conn, 3, ret='BB')
        self.ping = Command(self._conn, 4, ack=False, ret='7s')
        self.revision = Command(self._conn, 5, ack=False, ret='BB')  # assume
        # > 2.1
        self.abort = Command(self._conn, 6)
        self.read_adc_10 = Command(self._conn, 7, ret='HH', postack=True)
        self.measure_offset = Command(self._conn, 8, ret='HH', postack=True)

        # 1 byte
        self.trig_source = Command(self._conn, 21, args='B')
        self.trig_pol = Command(self._conn, 22, args='B')
        self.read_back = CommandReadback(self._conn, 23)
        self.sample_rate = Command(self._conn, 24, args='B')
        self.noise_reject = Command(self._conn, 25, args='B')
        self.arm = Command(self._conn, 26, args='B')
        self.adcon_from = Command(self._conn, 27, args='B')
        self.cal_mode = Command(self._conn, 28, args='B')
        self.pretriggger_mode = Command(self._conn, 29, args='B')
        self.timer_prescale = Command(self._conn, 30, args='B')
        self.post_trig_cnt = Command(self._conn, 31, args='B')
        self.serial_tx = Command(self._conn, 32, args='B')
        self.status_led = Command(self._conn, 33, args='B')

        # 2 bytes
        self.trig_level = Command(self._conn, 41, args='H')
        self.pre_gain = Command(self._conn, 42, args='BB')
        self.gain = Command(self._conn, 43, args='BB')
        self.set_dac = CommandSetDac(self._conn, 44, args='BB')
        self.arm_fft = Command(self._conn, 45, args='BB')
        self.set_delay = Command(self._conn, 49, args='H')
        self.timer_period = Command(self._conn, 51, args='H')

    def __enter__(self):
        """
        Opens connection to DPScope.

        Returns:
            DPScopeInterface: This interface instance.
        """
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Closes socket.
        """
        self.close()

    def open(self):
        """
        Open connection to DPscope.
        """
        if self._conn.isOpen():
            _LOGGER.info("Port is already. Closing port before reopening for "
                         "data acquisition.")
            self._conn.close()
        _LOGGER.info("Opening connection to DPScope (port: {}| baudrate: {})"
                     "".format(self._conn.portstr, self._conn.baudrate))
        self._conn.open()

    def close(self):
        """
        Closes connection to DPScope.
        """
        if self._conn.isOpen():
            _LOGGER.info("Closing connection to DPScope.")
            self._conn.close()
        else:
            _LOGGER.info("DPScope connection is already closed. No further "
                         "action required.")
