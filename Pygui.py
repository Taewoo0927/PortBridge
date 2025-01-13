import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
import openpyxl
import os
import time
from Pyfile import Pyfile_manipulate
from Pybase import _Pybase
import pyautogui
import threading

class Py_Gui(tk.Tk):

    def __init__(self):

        # Initialization
        super().__init__()
        self.title("Pull-Planner Data Extracter")
        self.style = ttk.Style(self)
        
        try:
            #self.tk.call("source", "forest-light.tcl")
            self.tk.call("source", "forest-dark.tcl")
            self.style.theme_use("forest-dark")

        except Exception as e:
            print(f"Error loading theme: {e}")
            self.style.theme_use("default")  # Fallback theme

        # Frame
        frame = ttk.Frame(self)
        frame.pack()

        # Frame - Widget frame
        widget_frame = ttk.Labelframe(frame, text="Basic Data")
        widget_frame.grid(row=0, column=0, padx=20, pady=10)

        # Frame - Widget frame - folder address entry
        self.path_entry = ttk.Entry(widget_frame)
        self.path_entry.insert(0, "Folder Path")
        self.path_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.path_entry, "Folder Path"))
        self.path_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(self.path_entry, "Folder Path"))
        self.path_entry.grid(row=0, column=0, padx=5, pady=(0, 5), sticky="w")

        # Frame - Widget frame - Doc name entry
        self.doc_name_entry = ttk.Entry(widget_frame)
        self.doc_name_entry.insert(0, "Document Name")
        self.doc_name_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(self.doc_name_entry, "Document Name"))
        self.doc_name_entry.bind("<FocusOut>", lambda e: self.restore_placeholder(self.doc_name_entry, "Document Name"))
        self.doc_name_entry.grid(row=1, column=0, padx=5, pady=10, sticky="ew")

        # Frame - Widget frame - Extract data button
        extract_data_button = ttk.Button(widget_frame, text="Extract Data", command=self.data_extract)
        extract_data_button.grid(row=2, column=0, padx=5, pady=10, sticky="nsew")
        
        # Frame - Widget frame - refresh button
        refresh_button = ttk.Button(widget_frame, text="Refresh", command=self.load_data)
        refresh_button.grid(row=3, column=0, padx=5, pady=10, sticky="nsew")

        # Frame - Widget frame - Extract report button
        extract_report_button = ttk.Button(widget_frame, text="Extract Report", command=self.start_report_extraction_thread)
        extract_report_button.grid(row=4, column=0, padx=5, pady=10, sticky="nsew")

        # Frame - Widget frame - Using continuous button mode
        self.continuous_var = tk.IntVar()
        self.continuous_chkbox = ttk.Checkbutton(widget_frame, text='Continuous Mode', variable=self.continuous_var, command=self.continous_mode_onoff)
        self.continuous_chkbox.grid(row=5, column=0, padx=5, pady=10, sticky="nsew")

        # Seperator
        seperator = ttk.Separator(widget_frame)
        seperator.grid(row=6, column=0, padx=(20, 20), pady=10, sticky="ew")

        # Frame - widget frame - output
        self.output_box = tk.Text(widget_frame, height=4, width=3, wrap="word")
        self.output_box.grid(row=7, column=0, padx=10, pady=10, sticky="ew")

        # Frame - TreeFrame
        treeFrame = ttk.Frame(frame)
        treeFrame.grid(row=0, column=1, pady=10)

        # Frame - TreeFrame - scrollbar
        treescroll = ttk.Scrollbar(treeFrame)
        treescroll.pack(side="right",  fill="y")

        # Frame - TreeFrame - treeview
        cols = ("File Name", "Max Tension (kN)", "Max SideWallPressure (kN/m)")
        self.treeview = ttk.Treeview(treeFrame, show="headings",yscrollcommand=treescroll.set, columns=cols, height=15)
        self.treeview.pack()
        self.treeview.column("File Name", width=380)
        self.treeview.column("Max Tension (kN)", width=100)
        self.treeview.column("Max SideWallPressure (kN/m)", width=180)

        treescroll.config(command=self.treeview.yview)

    def clear_placeholder(self, entry_widget, placeholder):
        # Clear the placeholder text if it matches
        if entry_widget.get() == placeholder:
            entry_widget.delete(0, tk.END)

    def restore_placeholder(self, entry_widget, placeholder):
        # Restore the placeholder text if the entry is empty
        if not entry_widget.get():
            entry_widget.insert(0, placeholder)

    # Someone might want light mode
    # To do: Make toggle switch changing the theme color dark <-> light
    def toggle_mode(self):

        if self.mode_switch.instate(["selected"]):
            self.style.theme_use("forest-light")
        else:
            self.style.theme_use("forest-dark")
            
    def load_data(self):

        if self.path_entry.get():

            path = self.path_entry.get()

            # Check if direction is correct
            if path == "Folder Path":
                self.display_output(f"Enter the Path\n")
                return
            # Check if direction exist
            if not os.path.isdir(path):
                self.display_output(f"Invalid folder location: {path}\n")
                return
            
            obj_filemanipulate = Pyfile_manipulate(path)
            
            try:
                file_names = obj_filemanipulate.locate_file(".xlsx")

                # Only allow one excel file to be loaded
                if file_names:

                    # Delete all items in the Treeview
                    for item in self.treeview.get_children():
                        self.treeview.delete(item)

                    for file_name in file_names:
                        print(file_name)
                        full_path = os.path.join(path, file_name)
                    
                        workbook = openpyxl.load_workbook(full_path)
                        sheet = workbook.active
                        list_values = list(sheet.values)

                        # Load all the datas
                        for col_name in list_values[0]:
                            self.treeview.heading(col_name, text=col_name)

                        for value_tuple in list_values[1:]:
                            self.treeview.insert('', tk.END, values=value_tuple)

                        self.display_output(f"Files found: {', '.join(file_names)}\n Loading the File")

                elif PermissionError:
                    self.display_output(f"Error: The file '{file_names}' is already open. Please close it and try again.\n")

                else:
                    self.display_output("Please locate .xlsx files in the specified folder.\n")

            except Exception as e:
                self.display_output(f"An error occurred: {e}")
                return


        else:
            self.display_output("Please Enter the Path.")

    def data_extract(self):
        if self.path_entry.get():

            path = self.path_entry.get()
            # Check if direction is correct
            if path == "Folder Path":
                self.display_output(f"Enter the Path\n")
                return
            
            # Check if direction exist
            if not os.path.isdir(path):
                self.display_output(f"Invalid folder location: {path}\n")
                return
            
            if self.doc_name_entry.get():
                doc_name = self.doc_name_entry.get()
                if doc_name == "Document Name":
                    self.display_output(f"Type File Name\n")
                    return
            else:
                self.display_output(f"Invalid File Name {path}\n")
                return

            test1 = _Pybase(path)


            if os.path.exists(path):
                
                self.display_output(f"Extracting the data \nSaved as:{doc_name}\n")
                if test1.auto_extract_xpll():
                    final_seg_datas, final_largest_datas, final_duct_length = test1.auto_extract_xpll()

                    # These values are not used since team didn't need it.
                    #print(final_duct_length)
                    #test1.create_bulk_report(doc_name, final_seg_datas)
                    #test1.create_bulk_report(doc_name, final_largest_datas)
                    test1.create_excel_report(doc_name, final_largest_datas)
                else:
                    self.display_output(f"No XPLL files exist\n")


            else:
                self.display_output(f"Invalid folder location: {path}\n")
                return

        else:
            self.display_output("Please Enter the Path.")
 
    def display_output(self, output):
        # Clear the output box
        self.output_box.delete(1.0, tk.END)
        # Insert some sample output text
        self.output_box.insert(tk.END, output)

    def report_extract(self):
        errorcode1 = False

        # Thread safe - disabling the changing state of the chkbx
        self.continuous_chkbox.state(["disabled"])

        if self.path_entry.get():
            path = self.path_entry.get()

            # Check if direction is correct
            if path == "Folder Path":
                self.display_output(f"Enter the Path\n")
                self.continuous_chkbox.state(["!disabled"])
                return
            
            # Check if direction exist
            if not os.path.isdir(path):
                self.display_output(f"Invalid folder location: {path}\n")
                self.continuous_chkbox.state(["!disabled"])
                return

            # Code to extract the report from xpll files - Just object in this function
            obj_pydata_report = Pyfile_manipulate(path)

            # Locate the files
            file_names = obj_pydata_report.locate_file(".xpll")

            self.display_output("Report Extraction start.")

            if(file_names):

                for file_name in file_names:
                    
                    obj_pydata_report.open_file(file_name)
                    self.display_output(f"File is opened: {file_name}")
                    time.sleep(10)
                    self.display_output("File is now opened.")

                    obj_pydata_report.download_report(file_name)
                    obj_pydata_report.find_element_with_pywinauto("Reverse_Segment_ButtonImg")
                    obj_pydata_report.download_report(file_name + " Reversed")


                    if(self.continuous_var.get()==0):
                        if not mb.askyesno('Verify', "Is this report successfully extracted?"):
                            mb.showwarning('No', "Sorry, Please talk to developer about the issue")
                            errorcode1 = True
                            break
                        mb.showinfo('Yes', "Thanks, Proceeding next file")
                    else:
                        if obj_pydata_report.close_window_with_pywinauto(f"Pull-Planner™ 4.0 Version 2020.1.113 - [ ]") and pyautogui.press('enter'):
                            print("File closed successfully.")
                        else:
                            print("Could not close the file.")

                # enable the chkbox again
                self.continuous_chkbox.state(["!disabled"])

                if(errorcode1):
                    self.display_output("Program Stopped")
                else:
                    self.display_output("Extraction Finished!")
            else:
                self.display_output("Empty folder!") 

        else:
            self.display_output("Please Enter the Path.")

    def continous_mode_onoff(self):
        if(self.continuous_var.get() == 1):
            self.display_output("Continuous mode ON")
        else:
            self.display_output("Continuous mode OFF")
    
    def start_report_extraction_thread(self):
        self.report_extraction_thread = threading.Thread(target=self.report_extract)
        self.report_extraction_thread.start()

if __name__ == "__main__":
    app = Py_Gui()
    app.mainloop()