import serial
import binascii
import argparse

class SerialSink():
    def __init__(self):

        # Command line arguments
        self._args = {}

        # Serial connection from which we read
        self._connection = None
        self._byteCnt = 0

    def main(self):
        parser = argparse.ArgumentParser()

        parser.add_argument('-i', '--serial-input-port', required=True, help="Input port, e.g. /dev/pts/1 no default")

        self._args = parser.parse_args()

        self.connect()
        while True:
            self.process()

    # Connect to the serial port when we run the script
    def connect(self):
        try:
            self._connection = serial.Serial(
                port=self._args.serial_input_port,
                baudrate=115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
            )
        except (serial.SerialException, OSError) as err:
            print("ERROR")


    # Start processing incoming data
    def process(self):
        try:
            raw_data = self._connection.read()
        except serial.SerialException:
            return

        self._byteCnt = self._byteCnt + 1

        if self._byteCnt == 50000:
           print("Read 50000 byte")
           self._byteCnt = 0


if __name__ == '__main__':
    serial_sink = SerialSink()
    serial_sink.main()
