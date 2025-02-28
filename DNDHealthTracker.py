import time
from tkinter import *
from tkinter import filedialog, messagebox
import json, copy

import serial.tools.list_ports

import CharacterCreator
import ConfigureCharacters
import CharacterArchive
import FrameBuilder
import AssignDevices
import InitiativeWindow
import MessageDevice


def NewProject():
    global project_directory
    global characters
    global last_save

    if not IsSaved():
        return

    project_directory = ""
    characters = []
    last_save = characters
    PopulateCharacters()


def ExitProgram():
    if not IsSaved():
        return

    root.destroy()


def OpenProject():
    global project_directory
    global characters
    global last_save

    if not IsSaved():
        return

    project_directory = filedialog.askopenfilename(
        filetypes=[("DND files", "*.dnd"), ("All files", "*.*")],  # File types options
        title="Open a file"
    )

    if project_directory:  # Check if a valid file path was selected
        try:
            with open(project_directory, 'r') as file:
                content = file.read()
                characters = json.loads(content)
                last_save = copy.deepcopy(characters)

                PopulateCharacters()
        except Exception as e:
            print(f"Error opening file: {e}")

    if MessageDevice.IsConnected():
        AssignDevices.assign_devices(characters)


def IsSaved():
    if not last_save == characters:
        response = messagebox.askyesnocancel("Confirmation", "Do you want to save? Any unsaved data will be lost.")
        if response is None:  # Cancel
            return False
        elif response:  # Yes
            SaveProject()
        else:  # No
            pass
    return True


def GetActiveCharacters():
    activeCharacters = []
    for c in characters:
        if c["Initiative"] is not None:
            activeCharacters.append(c)
    return activeCharacters


def UpdateDeviceLeds():
    global initiative_count

    for c in characters:
        if c["UUID"] == list(FrameBuilder.frames.keys())[initiative_count]:
            print("Current " + str(c["Device"]))
            MessageDevice.WriteMessageWithData("M" + str(c["Device"]), ["A", "True"])
            MessageDevice.WriteMessageWithData("M" + str(c["Device"]), ["N", "False"])
        else:
            if initiative_count + 1 >= len(FrameBuilder.frames):
                if c["UUID"] == list(FrameBuilder.frames.keys())[0]:
                    print("On Deck " + str(c["Device"]))
                    MessageDevice.WriteMessageWithData("M" + str(c["Device"]), ["N", "True"])
            else:
                if c["UUID"] == list(FrameBuilder.frames.keys())[initiative_count + 1]:
                    print("On Deck " + str(c["Device"]))
                    MessageDevice.WriteMessageWithData("M" + str(c["Device"]), ["N", "True"])

            if initiative_count - 1 < 0:
                if c["UUID"] == list(FrameBuilder.frames.keys())[len(FrameBuilder.frames) - 1]:
                    print("Last " + str(c["Device"]))
                    MessageDevice.WriteMessageWithData("M" + str(c["Device"]), ["A", "False"])
            else:
                if c["UUID"] == list(FrameBuilder.frames.keys())[initiative_count - 1]:
                    print("Last " + str(c["Device"]))
                    MessageDevice.WriteMessageWithData("M" + str(c["Device"]), ["A", "False"])


def PopulateCharacters():
    global reset_buttons

    for f in FrameBuilder.frames.items():
        f[1].destroy()
    FrameBuilder.frames.clear()
    reset_buttons = {}

    offset = 0
    #for idx, entity in enumerate(characters):
    #    if entity["Active"]:
    #        temp = FrameBuilder.create_entity_widget(entity, root, idx - offset)
    #        reset_buttons[temp[0]] = temp[1]
    #    else:
    #        offset += 1

    characters.sort(key=lambda char: char["Initiative"] if char["Initiative"] is not None else char["Max_Health"])

    rank = 0
    for c in characters:
        if c["Initiative"] is not None:
            temp = FrameBuilder.create_entity_widget(c, root, rank)
            reset_buttons[temp[0]] = temp[1]
            rank += 1
        else:
            offset += 1

    if len(characters) - offset == 0:  # 0
        #btn_last_character.grid(column=0, columnspan=2)
        #btn_next_character.grid(column=1, columnspan=2, sticky="e")
        btn_last_character.grid_forget()
        btn_next_character.grid_forget()
        no_characters_text.grid(column=0, row=0)
    elif (len(characters) - offset) == 1:  # 1
        btn_last_character.grid(column=0, row=0, sticky="w")
        btn_next_character.grid(column=0, row=0, sticky="e")
        no_characters_text.grid_forget()
    elif (len(characters) - offset) % 2 == 0 or (len(characters) - offset) > 4:  # Even
        btn_last_character.grid(column=int((len(characters) - offset) / 2) - 1, row=0, sticky="")
        btn_next_character.grid(column=int((len(characters) - offset) / 2), row=0, sticky="")
        no_characters_text.grid_forget()
    else:  #Odd
        btn_last_character.grid(column=int((len(characters) - offset) / 2), row=0, sticky="w")
        btn_next_character.grid(column=int((len(characters) - offset) / 2), row=0, sticky="e")
        no_characters_text.grid_forget()

    MessageDevice.WriteMessage("C")
    UpdateDeviceLeds()


def SaveProject():
    global project_directory
    global last_save

    if project_directory == "":
        project_directory = filedialog.asksaveasfilename(
            defaultextension=".dnd",  # Default file extension
            filetypes=[("DND files", "*.dnd"), ("All files", "*.*")],  # File types options
            title="Save your file"
        )

    if project_directory:  # Check if a valid file path was selected
        try:
            data = json.dumps(characters)
            with open(project_directory, 'w') as file:
                file.write(data)  # Example content
        except:
            return

        last_save = copy.deepcopy(characters)


def SaveAsProject():
    global project_directory

    project_directory = ""
    SaveProject()


def ConnectToDevice():
    global arduino

    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "CH340" in p.description:
            print(f"Arduino found on port {p.device}")
            arduino = serial.Serial(port=p.device, baudrate=115200, timeout=.1)
            MessageDevice.Init(arduino)
            time.sleep(2)
            MessageDevice.WriteMessage("Connect")
            print(arduino)

            time.sleep(1)
            AssignDevices.assign_devices(characters)


initiative_count = 0
#@profile
def ProgressCharacter(forward):
    global initiative_count
    global reset_buttons

    list(FrameBuilder.frames.items())[initiative_count][1].config(highlightbackground="#A0A0A0")

    initiative_count += forward
    if initiative_count > len(FrameBuilder.frames) - 1:
        initiative_count = 0
    elif initiative_count < 0:
        initiative_count = len(FrameBuilder.frames) - 1

    try:
        if forward > 0:
            reset_buttons[list(FrameBuilder.frames.items())[initiative_count][1]].invoke()
    except:
        pass

    list(FrameBuilder.frames.items())[initiative_count][1].config(highlightbackground="#606060")

    UpdateDeviceLeds()

    for c in characters:
        if c["UUID"] == list(FrameBuilder.frames.keys())[initiative_count]:
            MessageDevice.WriteMessageWithData("S99", (0, c['AC'], c['Health'], c['TempHealth'],
                                                       c['Action'], c['BonusAction'],
                                                       c['Reaction'], c['Name']))
            print(c['Name'])


def UpdateCharacterData(msg):
    # (code [1]) (dev id [2]) (page [1]) (data id [1]) (data value [remaining])
    # e.g. U120214

    # data ids
    # 0 - hp
    # 1 - temp hp
    # 2 - ac
    # 3 - action
    # 4 - bonus action
    # 5 - reaction
    # 6 - death saving success
    # 7 - death saving fail

    for c in characters:
        if ((c["Device"] is not None and int(c["Device"]) == int(msg[1] + msg[2]) and c["Page"] == int(msg[3])) or
                (int(msg[1] + msg[2]) == 99 and c["UUID"] == list(FrameBuilder.frames.keys())[initiative_count])):
            match int(msg[4]):
                case 0:
                    c["AC"] = int(msg[5:])
                case 1:
                    c["Health"] = int(msg[5:])
                    if c["Health"] == 0:
                        FrameBuilder.trigger_death_saving(c, FrameBuilder.health_labels[c["UUID"]])
                case 2:
                    c["TempHealth"] = int(msg[5:])
                case 3:
                    c["Action"] = int(msg[5]) == 1
                case 4:
                    c["BonusAction"] = int(msg[5]) == 1
                case 5:
                    c["Reaction"] = int(msg[5]) == 1
                case 6:
                    c["DeathSuccess"] = int(msg[5])
                case 7:
                    c["DeathFail"] = int(msg[5])

            if int(msg[4]) != 6 or int(msg[4]) != 7:
                FrameBuilder.update_entity_widget(c)
            else:
                FrameBuilder.handle_save(c, None)
                pass


def Init():
    global btn_last_character
    global btn_next_character
    global no_characters_text
    global root

    root = Tk()
    root.title('DND Health Tracker')

    menu = Menu(root)
    root.config(menu=menu)

    file_menu = Menu(menu, tearoff=0)
    menu.add_cascade(label='File', menu=file_menu)
    file_menu.add_command(label='New', command=NewProject)
    file_menu.add_command(label='Open', command=OpenProject)
    file_menu.add_separator()
    file_menu.add_command(label='Save', command=SaveProject)
    file_menu.add_command(label='Save As', command=SaveAsProject)
    file_menu.add_separator()
    file_menu.add_command(label='Exit', command=ExitProgram)
    root.protocol('WM_DELETE_WINDOW', ExitProgram)

    device_menu = Menu(menu, tearoff=0)
    menu.add_cascade(label='Device', menu=device_menu)
    device_menu.add_command(label='Connect', command=ConnectToDevice)
    device_menu.add_command(label='Assign Devices',
                            command=lambda: AssignDevices.create_character_device_window(characters))

    configure_menu = Menu(menu, tearoff=0)
    menu.add_cascade(label='Characters', menu=configure_menu)
    configure_menu.add_command(label='Add Character', command=lambda: CharacterCreator.AddCharacter(root, characters))
    configure_menu.add_command(label='Edit Character', command=lambda: CharacterCreator.EditCharacter(root, characters))
    configure_menu.add_command(label='Configure Characters',
                               command=lambda: ConfigureCharacters.ConfigureCharacters(root, characters))
    configure_menu.add_command(label='Character Archive',
                               command=lambda: CharacterArchive.CharacterArchive(root, characters))
    configure_menu.add_command(label='Set Initiative',
                               command=lambda: InitiativeWindow.create_item_movement_window(characters))

    btn_last_character = Button(root, text="Last Character", command=lambda: ProgressCharacter(-1))
    btn_last_character.grid(row=0, column=0, columnspan=2, pady=10, padx=5)
    btn_next_character = Button(root, text="Next Character", command=lambda: ProgressCharacter(1))
    btn_next_character.grid(row=0, column=1, columnspan=2, pady=10, padx=5)

    no_characters_text = Label(root, text="There are currently no active characters.")
    no_characters_text.grid(row=0, column=0, columnspan=2, pady=10, padx=5)

    PopulateCharacters()
    mainloop()

characters = []
last_save = []
reset_buttons = {}

arduino = None

btn_last_character = None
btn_next_character = None
no_characters_text = None
root = None
