import logging
from serial import Serial
import struct

# Set up logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)


class CommsException(Exception):
    """
    Communications exception - connection to device exists, but failure at
    the traffic layer.
    """


class CommandException(Exception):
    """
    The sent command is not structured correctly.
    """


class Command(object):
    """
    Manages command sending and receiving.

    Create one instance per DPScope command.
    """
    _conn = None  # Holds the serial connection
    _cmd = None  # Holds the command number, as an int
    _endian = "!"  # Big endianess
    _ackb = None  # Whether DPScope responds immediately to sent command
    _postack = None  # Whether DPScope return data following the command.
    _ret = None  # Format specifier for the data response.
    _args = None  # Format specifier for the parameters associated with the
    # sent command.

    @property
    def cmd(self):
        """
        Returns:
            bytes: Command number, in bytes form.
        """
        return bytes(chr(self._cmd), "utf-8")

    def __init__(self, conn, cmd, ack=True, postack=False, ret='', args=''):
        """
        Creates a controller for sending and receiving an individual DPScope
        command.

        Args:
            conn (serial.Serial): The serial connection.
            cmd (int): The command number.
            ack (bool): Determines if DPScope is expected to acknowledge as
            soon as a command is sent.
            postack (bool): Determines if DPScope is expected to send back
            data to the DPScope.
            ret (str): Sets the format of the data response (where applicable)
            from the DPScope.
            args (str): Sets the format of the command parameters sent to
            DPScope.
        """
        self._conn = conn
        self._cmd = cmd
        self._ackb = ack
        self._postack = postack
        self._ret = ret
        self._args = args

    def _ack(self):
        """
        Implements DPScope's acknowledgement protocol.

        On most commands, DPScope responds with the same command number as a
        simple error checking algorithm.
        """
        ackb = self._conn.read(1)
        if self.cmd != ackb:
            raise CommsException("Command sent was {}; DPScope responded "
                                 "with {}. DPScope did not acknowledge with a "
                                 "copy of the original command. Could be "
                                 "connected to a different device, or the "
                                 "scope is malfunctioning."
                                 "".format(self._cmd, ord(ackb)))

    def __call__(self, *args):
        """
        Communicates with DPScope.

        Sends commands, checks for command acknowledgement, and receives the
        actual responses from DPScope (where applicable).

        Args:
            *args: DPScope command parameters.

        Returns:
            Response from DPScope, the return format is dependent on the
            return format specifier in _ret.
        """
        arglen = struct.calcsize(self._endian+self._args)
        if len(args) != arglen:
            raise CommandException("Wrong number of arguments, command '{}' "
                                   "requires {} arguments. {} provided."
                                   "".format(self._cmd, arglen, len(args)))

        # Send command and parameters
        self.write(self.cmd)
        self.write(struct.pack(self._endian+self._args, *args))

        # Check DPScope's acknowledgement
        if self._ackb:
            self._ack()

        # receives data
        retlen = struct.calcsize(self._endian + self._ret)
        res = struct.unpack(self._endian + self._ret, self._conn.read(retlen))
        if self._postack:
            self._ack()
        if self._conn.inWaiting() != 0:
            raise CommsException("{} unexpected unread bytes after DPScope "
                                 "response.".format(self._conn.inWaiting()))

        return res


class DPScopeInterface(object):
    """
    Interface for DPScope.

    Exposes all API methods.
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

    def __enter__(self):
        """
        Opens connection to DPScope.

        Returns:
            DPScopeInterface: This interface instance.
        """
        self._conn.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Closes socket.
        """
        self._conn.close()


class DPScope(serial.Serial):


    def __init__(self, port):
        serial.Serial.__init__(self, port, 500000, timeout=1)

    def _ack(self, cmd):
        ackb = self.read(1)
        assert cmd == ord(ackb), "Command(%s) not the same as ack(%s)" % (cmd, ord(ackb))

    def _cmd(cmd, ack=True, postack=False, ret='', args=''):
        def cmd_impl(self, *params):
            endian = '!' #big
            arglen = struct.calcsize(endian+args)
            assert len(params) == arglen, "Wrong number of arguments, requires %s" % arglen
            self.write(bytes(chr(cmd), "utf-8"))
            self.write(struct.pack(endian+args, *params))

            if ack:
                self._ack(cmd)
            
            retlen = struct.calcsize(endian+ret)
            res = struct.unpack(endian+ret, self.read(retlen))

            if postack:
                self._ack(cmd)

            assert self.inWaiting() == 0, "%s unexpected unread bytes" % self.inWaiting()
            return res

        return cmd_impl
    
    # 0 bytes
    read_adc = _cmd(3, ret='BB')
    ping = _cmd(4, ack=False, ret='7s')
    revision = _cmd(5, ack=False, ret='BB') # assume > 2.1
    abort = _cmd(6)
    read_adc_10 = _cmd(7, ret='HH', postack=True)
    measure_offset = _cmd(8, ret='HH', postack=True)
    # 1 byte
    trig_source = _cmd(21, args='B')
    trig_pol = _cmd(22, args='B')
    def read_back(self, nob):
        self.write(bytes(chr(23)+chr(nob), "utf-8"))
        status = self.read()
        res = None
        if status:
            # res = map(ord, self.read(1+(2*nob)))
            read_buffer = self.read(1+(2*nob))
            res = [ord(char) for char in read_buffer.decode("utf-8")]
        assert self.inWaiting() == 0, "%s unexpected unread bytes" % self.inWaiting()
        return res

    sample_rate = _cmd(24, args='B')
    noise_reject = _cmd(25, args='B')
    arm = _cmd(26, args='B')
    adcon_from = _cmd(27, args='B')
    cal_mode = _cmd(28, args='B')
    pretriggger_mode = _cmd(29, args='B')
    timer_prescale = _cmd(30, args='B')
    post_trig_cnt = _cmd(31, args='B')
    serial_tx = _cmd(32, args='B')
    status_led = _cmd(33, args='B')
    # 2 bytes
    trig_level = _cmd(41, args='H')
    pre_gain = _cmd(41, args='BB')
    gain = _cmd(43, args='BB')
    _set_dac = _cmd(44, args='BB')
    def set_dac(self, ch, dac):
        ch = 0x80 * (ch % 2)
        B1 = (ch + 0x10) + (dac >> 8)
        B2 = dac & 0xff;
        self._set_dac(B1, B2)

    arm_fft = _cmd(45, args='BB')
    set_delay = _cmd(49, args='H')
    timer_period = _cmd(51, args='H')
