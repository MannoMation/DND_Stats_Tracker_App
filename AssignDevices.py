import time
import tkinter as tk
from tkinter import ttk, messagebox, END

import DNDHealthTracker
import FrameBuilder
import MessageDevice
from CharacterCreator import ValidateNum


def updateDevID(character_name, selected_id, characters, page_box):
    page_box.delete(0, END)
    if selected_id.get() == "None":
        page_box.config(state="readonly")
    else:
        page_box.config(state="normal")

    for c in characters:
        try:
            if c["Name"] == character_name:
                if selected_id.get() != "None":
                    c["Device"] = selected_id.get()

                    dupeDev = -1
                    for id in selected_ids:
                        if id.get() == c["Device"]:
                            dupeDev += 1
                    page_box.insert(0, dupeDev)
                else:
                    c["Device"] = None
                    c["Page"] = None
        except:
            pass
    print(f"Character: {character_name}, Device ID: {selected_id.get()}")


def updatePage(character_name, selected_page, characters):
    if selected_page.get() != "":
        for c in characters:
            try:
                if c["Name"] == character_name:
                    c["Page"] = int(selected_page.get())
            except:
                pass


def close(window, characters):
    MessageDevice.WriteMessage("IH")

    new_pages = []
    for c in characters:
        new_page = 0
        if c["Page"] is not None:
            for char in characters:
                if char != c and char["Page"] is not None:
                    if char["Page"] < c["Page"]:
                        new_page += 1
            new_pages.append(new_page)

    i = 0
    for c in characters:
        if c["Page"] is not None:
            c["Page"] = new_pages[i]
            i += 1

    assign_devices(characters)

    window.destroy()


def assign_devices(characters):
    for c in characters:
        try:
            if c["Device"] is not None:
                print('S' + str(c["Device"]) + ',' + str(c['Page']) + ',' + str(c['AC']) + "," + str(c['Health']) + "," + str(c['TempHealth'])
                               + "," + str(c['Action']) + "," + str(c['BonusAction']) + "," + str(c['Reaction']) + ',\n')
                MessageDevice.WriteMessageWithData("S" + str(c['Device']), (c['Page'], c['AC'], c['Health'], c['TempHealth'],
                                                         c['Action'], c['BonusAction'], c['Reaction'], c['Name']))
            if c["UUID"] == list(FrameBuilder.frames.keys())[DNDHealthTracker.initiative_count]:
                MessageDevice.WriteMessageWithData("S99", (0, c['AC'], c['Health'], c['TempHealth'],
                                                                            c['Action'], c['BonusAction'],
                                                                            c['Reaction'], c['Name']))
        except:
            pass

def create_character_device_window(characters):
    global selected_ids

    if not MessageDevice.IsConnected():
        messagebox.showerror("Error", "There are no connected devices")
        return

    MessageDevice.WriteMessage("IS")
    device_ids = ""

    time.sleep(0.5)
    data = MessageDevice.GetMessage('D')
    if data is not None:
        data = data[1:]
        print(data)
        device_ids = data.split(",")
        device_ids.remove(device_ids[len(device_ids) - 1])
        print(device_ids)
    device_ids.insert(0, "None")

    """Create a new window for character-device mapping."""
    window = tk.Toplevel()
    window.title("Character to Device Mapping")
    window.resizable(False, False)

    # Configure grid for consistent column sizes
    for i in range(2):
        window.grid_columnconfigure(i, weight=1, uniform="equal")

    # Title Label
    tk.Label(window, text="Assign Devices to Characters", font=("Arial", 14, "bold"))\
        .grid(row=0, column=0, columnspan=2, pady=10)

    validate_num = (DNDHealthTracker.root.register(ValidateNum), "%S")

    # Populate the window with character names and dropdowns
    row = 0
    for character in characters:
        row += 1

        # Character Name Label
        tk.Label(window, text=character["Name"], font=("Arial", 12))\
            .grid(row=row, column=0, padx=10, pady=5, sticky="w")

        # Dropdown for Device IDs
        selected_id = tk.StringVar()
        selected_id.set("Select Device")
        dropdown = ttk.Combobox(window, textvariable=selected_id, values=device_ids, state="readonly")
        dropdown.grid(row=row, column=1, padx=10, pady=5)
        selected_ids.append(selected_id)

        selected_page = tk.StringVar()
        selected_page.trace("w", lambda name, index, mode, c_name=character["Name"], page=selected_page: updatePage(c_name, page, characters))
        page_entry = tk.Entry(window, validate="key", validatecommand=validate_num, textvariable=selected_page, state="readonly")
        page_entry.grid(row=row, column=2, padx=10, pady=5, stick="w")

        if character["Device"] is not None:
            selected_id.set(character["Device"])
            page_entry.config(state="normal")
            page_entry.insert(0, character["Page"])

        # Print selection on device selection change
        dropdown.bind(
            "<<ComboboxSelected>>",
            lambda event, char_name=character["Name"], sel_id=selected_id, page_box=page_entry: updateDevID(char_name, sel_id, characters, page_box),
        )

    window.protocol("WM_DELETE_WINDOW", lambda: close(window, characters))

selected_ids = []
