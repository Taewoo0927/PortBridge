import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
from CommHandler import PyUART
import threading
import re

class Py_Gui(tk.Tk):

    def __init__(self):

        # Initialization
        super().__init__()
        self.title("PortBridge")
        self.style = ttk.Style(self)
        
        try:
            #self.tk.call("source", "forest-light.tcl")
            self.tk.call("source", "forest-dark.tcl")
            self.style.theme_use("forest-dark")

        except Exception as e:
            print(f"Error loading theme: {e}")
            self.style.theme_use("default")  # Fallback theme

        # Initialize PortBridge
        self.uart_handler = None

        # Frame
        frame = ttk.Frame(self, width=800)
        frame.pack()

        # Frame - Widget frame
        widget_frame = ttk.Labelframe(frame, text="Basic Data")
        widget_frame.grid(row=0, column=0, padx=20, pady=10)

        # Frame - Widget frame - folder address entry
        self.port_entry = ttk.Entry(widget_frame)
        self.port_entry.insert(0, "Port")
        self.port_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.port_entry, "Port"))
        self.port_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(self.port_entry, "Port"))
        self.port_entry.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="w")

        # Frame - Widget frame - baud rate entry
        self.baud_rate_entry = ttk.Entry(widget_frame)
        self.baud_rate_entry.insert(0, "Baud Rate")
        self.baud_rate_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.baud_rate_entry, "Baud Rate"))
        self.baud_rate_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(self.baud_rate_entry, "Baud Rate"))
        self.baud_rate_entry.grid(row=1, column=0, padx=5, pady=10, sticky="ew")

        # Frame - Widget frame - Connect Port data button
        connect_button = ttk.Button(widget_frame, text="Connect Port", command=self.connection_thread)
        connect_button.grid(row=2, column=0, padx=5, pady=10, sticky="nsew")
        
        # Frame - Widget frame - Read Data button
        read_button = ttk.Button(widget_frame, text="Read Data", command=self.read_data)
        read_button.grid(row=3, column=0, padx=5, pady=10, sticky="nsew")

        # Frame - Widget frame - Extract report button
        #extract_report_button = ttk.Button(widget_frame, text="Extract Report", command=self.start_report_extraction_thread)
        #extract_report_button.grid(row=4, column=0, padx=5, pady=10, sticky="nsew")

        # Frame - Widget frame - Using continuous button mode
        #self.continuous_var = tk.IntVar()
        #self.continuous_chkbox = ttk.Checkbutton(widget_frame, text='Continuous Mode', variable=self.continuous_var, command=self.continous_mode_onoff)
        #self.continuous_chkbox.grid(row=5, column=0, padx=5, pady=10, sticky="nsew")

        # Seperator
        seperator = ttk.Separator(widget_frame)
        seperator.grid(row=6, column=0, padx=(20, 20), pady=10, sticky="ew")

        # Frame - widget frame - output
        self.output_box = tk.Text(widget_frame, height=4, width=3, wrap="word")
        self.output_box.grid(row=7, column=0, padx=10, pady=10, sticky="ew")

        # Frame - TreeFrame
        treeFrame = ttk.Labelframe(frame, text="Output Frame")
        treeFrame.grid(row=0, column=1, padx=10, pady=10, sticky="new")

        # Frame - TreeFrame - text widget with wrapping
        self.input_data_frame = tk.Text(treeFrame, wrap="word")
        self.input_data_frame.grid(row=0, column=0, padx=2, pady=2, sticky="ew")


    def clear_placeholder(self, entry_widget, placeholder):
        # Clear the placeholder text if it matches
        if entry_widget.get() == placeholder:
            entry_widget.delete(0, tk.END)

    def restore_placeholder(self, entry_widget, placeholder):
        # Restore the placeholder text if the entry is empty
        if not entry_widget.get():
            entry_widget.insert(0, placeholder)
 
    def display_output(self, output):
        # Clear the output box
        self.output_box.delete(1.0, tk.END)
        # Insert some sample output text
        self.output_box.insert(tk.END, output)
    
    def connection_thread(self):
        self.report_extraction_thread = threading.Thread(target=self.connection)
        self.report_extraction_thread.start()

    ###################################
    # Custom function for CommHandler #
    ###################################

    # Check if it connected properly
    def connection(self):
        # Retrieve port and baud rate from entries
        port = self.port_entry.get()
        baud_rate = self.baud_rate_entry.get()

        # Validate input & Check if already connected
        if not self.is_number([port, baud_rate]):
            self.display_output("Error: Please enter a valid port and baud rate.")
            return False
        if self.uart_handler and self.uart_handler.is_connect():
            self.display_output(f"Already connected to port: {port} & baud rate: {baud_rate}")
            return False

        try:
            # Initialize and open UART connection
            self.uart_handler = PyUART(port, baud_rate)
            self.uart_handler.open()

            if self.uart_handler.is_connect():
                self.display_output(f"Successfully connected to port: {port} & baud rate: {baud_rate}")
                return True
            else:
                raise RuntimeError("Connection failed for unknown reasons.")
        except Exception as e:
            self.display_output(f"Error: {e}")
            return False

    # Send Data if it's connected properly
    def send_data(self):
        if not self.uart_handler.is_connect():
            self.display_output(f"Error: Please connect to the port first")
            return False
        elif not self.input_data_frame.get():
            self.display_output(f"Error: Please Type something")
            return False
        try:
            tx_data = self.uart_handler.preprocess_data(self.input_data_frame.get())
            self.uart_handler.send(tx_data)
        except Exception as E:
            self.display_output(f"Error: {E}")
        finally:
            self.display_output(f"Successfully sent {self.input_data_frame.get()}")
            self.uart_handler.close()
    
    # Receive Data if it's connected and run until it gets nothing or user stops
    def read_data(self):
        if not self.uart_handler.is_connect():
            self.display_output(f"Error: Please connect to the port first")
            return False
        try:
            # Clear the output box
            self.input_data_frame.delete(1.0, tk.END)
            while True:
                rx_data = self.uart_handler.receive()
                if rx_data:
                    self.display_output(f"Received: {rx_data}")
                    self.input_data_frame.insert(tk.END, rx_data)
                else:
                    break  # No more data, exit loop
        except KeyboardInterrupt:
            self.display_output("Reading stopped by user.")
        except Exception as E:
            self.display_output(f"Error: {E}")
        
        finally:
            self.uart_handler.close()
            self.display_output("Connection closed.")


    def is_number(self, input_data):
        # Regex pattern to check if the input is a valid number
        pattern = r'^-?\d+(\.\d+)?$'
        
        if isinstance(input_data, list):
            # Return False if any element is not a number
            return all(bool(re.match(pattern, str(item))) for item in input_data)
        
        # Handle single value input
        return bool(re.match(pattern, str(input_data)))


if __name__ == "__main__":
    app = Py_Gui()
    app.mainloop()