"""
Sends and receives command to DPScope.
"""
from abc import ABC, abstractmethod
import logging
import struct
from threading import Lock

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


class CommandBase(ABC):
    """
    Class API for sending and receiving commands.

    Usage:
        Instantiate class with at least a connection and command integer.
        The external code should call the instantiated object as a function
        (implemented in the __call__() method).
    """
    @abstractmethod
    def __call__(self, *args, **kwargs):
        """
        Command class must be a callable.
        """


class Command(CommandBase):
    """
    Manages command sending and receiving.

    Create one instance per DPScope command. This is a generalised class
    suitable for most commands. There are some commands which require specific
    implementations, but those are defined as separate subclasses of
    CommandBase.
    """
    _conn = None  # Holds the serial connection
    _cmd = None  # Holds the command number, as an int
    _endian = "!"  # Big endianess
    _ackb = None  # Whether DPScope responds immediately to sent command
    _postack = None  # Whether DPScope return data following the command.
    _ret = None  # Format specifier for the data response.
    _args = None  # Format specifier for the parameters associated with the
    # sent command.

    _conn_lock = Lock()  # Threading lock to protect the serial connection.

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

        with self._conn_lock:
            # Send command and parameters
            self._conn.write(self.cmd)
            self._conn.write(struct.pack(self._endian+self._args, *args))

            # Check DPScope's acknowledgement
            if self._ackb:
                self._ack()

            # receives data
            retlen = struct.calcsize(self._endian + self._ret)
            res = struct.unpack(self._endian + self._ret,
                                self._conn.read(retlen))
            if self._postack:
                self._ack()
            if self._conn.inWaiting() != 0:
                raise CommsException("{} unexpected unread bytes after "
                                     "DPScope response."
                                     "".format(self._conn.inWaiting()))

        return res


class CommandReadback(CommandBase):
    """
    Specialised Command class that implements readback of acquired data record.
    """
    _conn = None  # Holds the serial connection
    _cmd = None  # Holds the command num for initiating readback operation.

    _conn_lock = Lock()  # Threading lock to protect the serial connection.

    def __init__(self, conn, cmd):
        """
        Instantiate with the command for implementing the readback command.

        Args:
            conn (serial.Serial): The serial connection
            cmd (int): The command num for initiating readback operation.
        """
        self._conn = conn
        self._cmd = cmd

    def __call__(self, nob):
        """
        Read back a specific num of bytes.

        Args:
            nob (int): Num of bytes.

        Return:
            Results.
        """
        with self._conn_lock:
            self._conn.write(bytes(chr(self._cmd) + chr(nob), "utf-8"))
            status = self._conn.read()
            res = None
            if status:
                read_buffer = self._conn.read(1 + (2 * nob))
                res = [ord(char) for char in read_buffer.decode("utf-8")]
            if self._conn.inWaiting() != 0:
                raise CommsException("{} unexpected unread bytes."
                                     "".format(self._conn.inWaiting()))

        return res


class CommandSetDac(Command):
    """
    Specialised Command class that implements the Set DAC command.
    """
    def __call__(self, ch, dac):
        """
        Parameters for implementing Set DAC command.

        Args:
            ch (byte): Channel num
            dac (byte): DAC output voltage in mV

        Returns:
            Response from DPScope.
        """
        ch = 0x80 * (ch % 2)
        B1 = (ch + 0x10) + (dac >> 8)
        B2 = dac & 0xff
        return super().__call__(B1, B2)
