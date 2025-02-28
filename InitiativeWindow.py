import tkinter as tk
from tkinter import ttk

import DNDHealthTracker


def create_item_movement_window(characters):
    """Create a new window for moving items between boxes and rearranging them."""
    window = tk.Toplevel()
    window.title("Item Movement and Rearrangement")

    # Configure grid layout
    for i in range(3):
        window.grid_columnconfigure(i, weight=1, uniform="equal")

    # Left and right listboxes
    left_box = tk.Listbox(window, selectmode=tk.SINGLE, height=15)
    right_box = tk.Listbox(window, selectmode=tk.SINGLE, height=15)

    # Populate the left box with sample items
    for c in characters:
        if c["Initiative"] is not None:
            right_box.insert(tk.END, c["Name"] + " : " + str(c["Health"]) + "/" + str(c["Max_Health"]) + "HP" +
                            "                                                                         "
                            "                                                                         "
                            "                                                                         "
                            + "UUID:" + c["UUID"])
        elif c["Active"]:
            left_box.insert(tk.END, c["Name"] + " : " + str(c["Health"]) + "/" + str(c["Max_Health"]) + "HP" +
                                    "                                                                         "
                                    "                                                                         "
                                    "                                                                         "
                                    + "UUID:" + c["UUID"])

    left_box.grid(row=0, column=0, padx=10, pady=10)
    right_box.grid(row=0, column=2, padx=10, pady=10)

    # Move item to the right box
    def move_to_right():
        selected = left_box.curselection()
        if selected:
            item = left_box.get(selected)
            right_box.insert(tk.END, item)
            left_box.delete(selected)

    # Move item to the left box
    def move_to_left():
        selected = right_box.curselection()
        if selected:
            item = right_box.get(selected)
            left_box.insert(tk.END, item)
            right_box.delete(selected)

    # Move selected item up in the right box
    def move_up():
        selected = right_box.curselection()
        if selected:
            index = selected[0]
            if index > 0:
                item = right_box.get(index)
                right_box.delete(index)
                right_box.insert(index - 1, item)
                right_box.select_set(index - 1)

    # Move selected item down in the right box
    def move_down():
        selected = right_box.curselection()
        if selected:
            index = selected[0]
            if index < right_box.size() - 1:
                item = right_box.get(index)
                right_box.delete(index)
                right_box.insert(index + 1, item)
                right_box.select_set(index + 1)

    def on_close():
        list = []
        list.extend(right_box.get(0, tk.END))
        rank = 0

        for c in characters:
            c["Initiative"] = None

        for l in list:
            uuid = l.split("UUID:")[1]
            for c in characters:
                if c["UUID"] == uuid:
                    c["Initiative"] = rank
                    print(c["Name"] + ", " + str(c["Initiative"]))
            rank += 1
        DNDHealthTracker.PopulateCharacters()
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_close)

    # Buttons for movement and rearrangement
    btn_frame = tk.Frame(window)
    btn_frame.grid(row=0, column=1, padx=10, pady=10)

    tk.Button(btn_frame, text="->", command=move_to_right).pack(pady=5)
    tk.Button(btn_frame, text="<-", command=move_to_left).pack(pady=5)
    tk.Button(btn_frame, text="Up", command=move_up).pack(pady=5)
    tk.Button(btn_frame, text="Down", command=move_down).pack(pady=5)