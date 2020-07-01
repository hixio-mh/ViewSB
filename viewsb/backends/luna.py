#
# This file is part of ViewSB.
#
""" Work in progress backend for LUNA. """

# pylint: disable=maybe-no-member,access-member-before-definition

from ..backend import ViewSBBackend
from ..packet import USBPacket

try:
    from luna.gateware.applets.analyzer import \
        USBAnalyzerConnection, \
        USB_SPEED_FULL, USB_SPEED_HIGH, USB_SPEED_LOW

except (ImportError, ModuleNotFoundError):
    pass


class LUNABackend(ViewSBBackend):
    """ Capture backend that captures packets from a LUNA board. """

    UI_NAME = "luna"
    UI_DESCRIPTION = "LUNA hardware analyzers"


    SPEEDS = {
        'high': USB_SPEED_HIGH,
        'full': USB_SPEED_FULL,
        'low':  USB_SPEED_LOW
    }


    @staticmethod
    def reason_to_be_disabled():

        # If we can't import LUNA, it's probably not installed.
        if not 'USBAnalyzerConnection' in globals():
            return "python luna package not available"

        return None


    @classmethod
    def speed_from_string(cls, string):

        try:
            return cls.SPEEDS[string]
        except KeyError:
            return string


    @classmethod
    def add_options(cls, parser):

        # Parse user input and try to extract our class options.
        parser.add_argument('--speed', dest='capture_speed', default='high', choices=cls.SPEEDS.keys(),
            help="The speed of the USB data to capture.")


    def __init__(self, capture_speed, suppress_packet_callback=None):
        """ Creates a new LUNA capture backend.

        Args:
            capture_speed -- The speed at which to capture.
        """

        super().__init__()

        # TODO: validate
        self.capture_speed = self.speed_from_string(capture_speed)

        # Set up our connection to the analyzer.
        self.analyzer = USBAnalyzerConnection()

        # Build our analyzer gateware, and configure our FPGA.
        self.analyzer.build_and_configure(self.capture_speed)


    def run_capture(self):

        # Capture a single packet from LUNA.
        raw_packet, timestamp, _ = self.analyzer.read_raw_packet()

        # TODO: handle flags
        packet = USBPacket.from_raw_packet(raw_packet, timestamp=timestamp)
        self.emit_packet(packet)
