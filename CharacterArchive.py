from tkinter import *
from tkinter import messagebox


def move_to_right():
    global left_box
    global right_box
    global characters

    selected = left_box.curselection()
    if not selected:
        #messagebox.showinfo("Error", "No option selected.")
        return

    uuid = left_box.get(selected[0], selected[0])[0].split("UUID:")[1]
    for c in characters:
        if c["UUID"] == uuid:
            if c["Active"]:
                response = messagebox.askyesno("Confirmation", "The character you are trying to archive is "
                                                               "currently an active character. Are you sure you want to "
                                                               "deactivate and archive this character?")
                if response:
                    c["Active"] = False
                    c["Archive"] = True
                else:
                    return

    item = left_box.get(selected)
    right_box.insert(END, item)
    left_box.delete(selected)


def move_to_left():
    global left_box
    global right_box
    global characters

    selected = right_box.curselection()
    if not selected:
        #messagebox.showinfo("Error", "No option selected.")
        return

    uuid = right_box.get(selected[0], selected[0])[0].split("UUID:")[1]
    for c in characters:
        if c["UUID"] == uuid:
            c["Archive"] = False

    item = right_box.get(selected)
    left_box.insert(END, item)
    right_box.delete(selected)


def CharacterArchive(root, chars):
    global cc_window
    global left_box
    global right_box
    global characters

    cc_window = Toplevel(root)
    cc_window.title("Archive Characters")
    cc_window.resizable(False, False)

    # Create frames for better layout management
    left_frame = Frame(cc_window)
    right_frame = Frame(cc_window)
    button_frame = Frame(cc_window)

    left_frame.grid(row=0, column=0, padx=10, pady=10)
    right_frame.grid(row=0, column=2, padx=10, pady=10)
    button_frame.grid(row=0, column=1, padx=10, pady=10)

    # Create the left listbox
    left_label = Label(left_frame, text="Available Characters")
    left_label.pack()
    left_box = Listbox(left_frame, selectmode=SINGLE, width=30, height=15)
    left_box.pack()

    # Create the right listbox
    right_label = Label(right_frame, text="Archived Characters")
    right_label.pack()
    right_box = Listbox(right_frame, selectmode=SINGLE, width=30, height=15)
    right_box.pack()

    # Populate the left listbox with some options
    characters = chars
    for c in chars:
        if c["Archive"]:
            right_box.insert(END, c["Name"] + " : " + str(c["Health"]) + "/" + str(c["Max_Health"]) + "HP" +
                             "                                                                         "
                             "                                                                         "
                             "                                                                         "
                             + "UUID:" + c["UUID"])
        else:
            left_box.insert(END, c["Name"] + " : " + str(c["Health"]) + "/" + str(c["Max_Health"]) + "HP" +
                            "                                                                         "
                            "                                                                         "
                            "                                                                         "
                            + "UUID:" + c["UUID"])

    # Add buttons
    btn_move_to_right = Button(button_frame, text=">>", command=move_to_right)
    btn_move_to_left = Button(button_frame, text="<<", command=move_to_left)

    btn_move_to_right.pack(pady=5)
    btn_move_to_left.pack(pady=5)

    # Run the application
    cc_window.mainloop()


cc_window = None
left_box = None
right_box = None
characters = None
