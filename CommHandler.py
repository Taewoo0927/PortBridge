import serial

class PyUART:
    def __init__(self, port, baudrate=9600, parity=serial.PARITY_NONE, timeout=1):
        # Initialize the UART connection.
        self._port = port
        self._baudrate = baudrate
        self._parity = parity
        self._timeout = timeout
        self._connection = None

    def open(self):
        # Connect to the UART
        try:
            self._connection = serial.Serial(
                port=self._port,
                baudrate=self._baudrate,
                parity=self._parity,
                timeout= self._timeout
            )
            print(f"Connected to {self.port} at {self.baudrate} baud.")
        except serial.SerialException as e:
            print(f"Failed to open port {self.port}: {e}")

    def close(self):
        # Close the UART
        if self._connection and self._connection.is_open:
            self._connection.close()
            print(f"Connection to {self.port} closed.")
    
    def send(self, data):
        # Send data via UART
        if self._connection and self._connection.is_open:
            if isinstance(data, str):
                data = data.encode()
            self._connection.write(data)
            print(f"Sent: {data}")
        else:
            print("Connection is not open. Unable to send data.")
    
    def receive(self):
        # Receive data via UART
        if self._connection and self._connection.is_open:
            try:
                data = self._connection.readline().decode().strip()
                print(f"Received: {data}")
                return data
            except Exception as e:
                print(f"Error reading data: {e}")
                return None
        else:
            print("Connection is not open. Unable to receive data.")
            return None