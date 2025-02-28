from tkinter import *
from tkinter import filedialog, messagebox
import uuid


def create_character(characters, edit=False):
    global name_var
    global health_var
    global ac_var
    global action_var
    global bonus_action_var
    global reaction_var
    global legendary_action_var
    global legendary_action_num_var
    global legendary_resistance_var
    global legendary_resistance_num_var
    global death_saving_var
    global new_character_window
    global u

    name = name_var.get()
    health = 0 if health_var.get() == "" else int(health_var.get())
    ac = 0 if ac_var.get() == "" else int(ac_var.get())
    action_value = action_var.get()
    bonus_action_value = bonus_action_var.get()
    reaction_value = reaction_var.get()
    legendary_action_value = legendary_action_var.get()
    legendary_action_num_value = int(legendary_action_num_var.get()) if legendary_action_value else 0
    legendary_resistance_value = legendary_resistance_var.get()
    legendary_resistance_num_value = int(legendary_resistance_num_var.get()) if legendary_resistance_value else 0
    death_saving_value = death_saving_var.get()

    # For now, print the created character's data
    print(f"Character Created: \nName: {name} \nHealth: {health} \nAC: {ac}")
    print(f"Actions: {action_value}, {bonus_action_value}, {reaction_value}")
    print(f"Legendary Actions: {legendary_action_value}, {legendary_action_num_value}")
    print(f"Legendary Resistances: {legendary_resistance_value}, {legendary_resistance_num_value}")
    print(f"Death Saving Rolls: {death_saving_value}")

    if edit:
        if u is not None:
            for c in characters:
                if c["UUID"] == u:
                    c["Max_Health"] = health
                    c["AC"] = ac
                    c["Action"] = action_value
                    c["BonusAction"] = bonus_action_value
                    c["Reaction"] = reaction_value
                    c["LegendaryActionMax"] = legendary_action_value
                    c["LegendaryActionNum"] = legendary_action_num_value
                    c["LegendaryResistanceMax"] = legendary_resistance_value
                    c["LegendaryResistanceNum"] = legendary_resistance_num_value
                    c["DeathSaving"] = death_saving_value
    else:
        characters.append({"Name":name, "UUID":str(uuid.uuid4()), "Max_Health":health, "AC":ac, "Health":health, "TempHealth":0, "Action":action_value, "BonusAction":bonus_action_value, "Reaction":reaction_value, "LegendaryActionMax":legendary_action_num_value, "LegendaryActionNum":legendary_action_num_value, "LegendaryResistanceMax":legendary_resistance_num_value, "LegendaryResistanceNum":legendary_resistance_num_value, "DeathSaving":death_saving_value, "Active":True, "Archive":False, "Device":None, "Page":None, "Initiative":None})

    new_character_window.destroy()


def ToggleLegendaryAction(field):
    if legendary_action_var.get():
        field.config(state="normal")
    else:
        field.config(state="disabled")


def ToggleLegendaryResistance(field):
    if legendary_resistance_var.get():
        field.config(state="normal")
    else:
        field.config(state="disabled")


def ValidateNum(char):
    # Allow only digits (0-9)
    if char.isdigit() or char == "":  # Allow empty input for backspace
        return True
    else:
        return False


def NameSelected(name):
    global chars
    global u

    for c in chars:
        if c["Name"] == name:
            character = c
            u = c["UUID"]

    health_var.set(character["Max_Health"])
    ac_var.set(character["AC"])
    action_var.set(character["Action"])
    bonus_action_var.set(character["BonusAction"])
    reaction_var.set(character["Reaction"])

    legendary_action_var.set(character["LegendaryActionMax"] > 0)
    legendary_action_num_var.set(character["LegendaryActionNum"])
    if character["LegendaryActionMax"]:
        legendary_action_num.config(state="normal")
    else:
        legendary_action_num.config(state="disabled")

    legendary_resistance_var.set(character["LegendaryResistanceMax"] > 0)
    legendary_resistance_num_var.set(character["LegendaryResistanceNum"])
    if character["LegendaryResistanceMax"]:
        legendary_resistance_num.config(state="normal")
    else:
        legendary_resistance_num.config(state="disabled")

    death_saving_var.set(character["DeathSaving"])


def AddCharacter(root, characters, edit=False):
    global chars
    global name_var
    global health_var
    global ac_var
    global action_var
    global bonus_action_var
    global reaction_var
    global legendary_action_var
    global legendary_action_num
    global legendary_action_num_var
    global legendary_resistance_var
    global legendary_resistance_num
    global legendary_resistance_num_var
    global death_saving_var
    global new_character_window

    chars = characters

    name_var = StringVar()
    health_var = StringVar()
    ac_var = StringVar()
    action_var = BooleanVar()
    bonus_action_var = BooleanVar()
    reaction_var = BooleanVar()
    legendary_action_var = BooleanVar()
    legendary_action_num_var = StringVar()
    legendary_resistance_var = BooleanVar()
    legendary_resistance_num_var = StringVar()
    death_saving_var = BooleanVar()

    new_character_window = Toplevel(root)
    new_character_window.title("New Character")
    new_character_window.resizable(False, False)

    validate_num = (root.register(ValidateNum), "%S")

    name_label = Label(new_character_window, text="Name:")
    name_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
    if edit:
        options = []
        for c in characters:
            options.append(c["Name"])
        name_entry = OptionMenu(new_character_window, name_var, *options, command=NameSelected)
        name_entry.config(width=20)
    else:
        name_entry = Entry(new_character_window, textvariable=name_var)

    name_entry.grid(row=0, column=1, padx=10, pady=10, stick="w")

    # Add a label and entry for the health
    health_label = Label(new_character_window, text="Health:")
    health_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
    health_entry = Entry(new_character_window, validate="key", validatecommand=validate_num, textvariable=health_var)
    health_entry.grid(row=1, column=1, padx=10, pady=10)

    ac_label = Label(new_character_window, text="AC:")
    ac_label.grid(row=2, column=0, padx=10, pady=10, sticky="w")
    ac_entry = Entry(new_character_window, validate="key", validatecommand=validate_num, textvariable=ac_var)
    ac_entry.grid(row=2, column=1, padx=10, pady=10)

    # Add 3 checkboxes in a row
    action = Checkbutton(new_character_window, text="Has Action", variable=action_var)
    action.grid(row=3, column=0, padx=10, pady=10, sticky="w")

    bonus_action = Checkbutton(new_character_window, text="Has Bonus Action", variable=bonus_action_var)
    bonus_action.grid(row=3, column=1, padx=10, pady=10, sticky="w")

    reaction = Checkbutton(new_character_window, text="Has Reaction", variable=reaction_var)
    reaction.grid(row=3, column=2, padx=10, pady=10, sticky="w")

    # Legendary Actions
    legendary_action_num = Entry(new_character_window, width=15, validate="key", validatecommand=validate_num, textvariable=legendary_action_num_var)
    legendary_action_num.config(state="disabled")

    legendary_action = Checkbutton(new_character_window, text="Has Legendary Actions", variable=legendary_action_var, command=lambda: ToggleLegendaryAction(legendary_action_num))
    legendary_action.grid(row=4, column=0, padx=10, pady=10, sticky="w")

    legendary_action_num.grid(row=4, column=1, padx=10, pady=10, sticky="w")

    # Legendary Resistance
    legendary_resistance_num = Entry(new_character_window, width=15, validate="key", validatecommand=validate_num, textvariable=legendary_resistance_num_var)
    legendary_resistance_num.config(state="disabled")

    legendary_resistance = Checkbutton(new_character_window, text="Has Legendary Resistances", variable=legendary_resistance_var, command=lambda: ToggleLegendaryResistance(legendary_resistance_num))
    legendary_resistance.grid(row=5, column=0, padx=10, pady=10, sticky="w")

    legendary_resistance_num.grid(row=5, column=1, padx=10, pady=10, sticky="w")

    # Add a single checkbox below
    death_saving = Checkbutton(new_character_window, text="Has Death Saving Rolls", variable=death_saving_var)
    death_saving.grid(row=6, column=0, padx=10, pady=10)

    # Add the button to create the character
    if edit:
        create_button = Button(new_character_window, text="Edit Character",
                               command=lambda: create_character(characters, True))
    else:
        create_button = Button(new_character_window, text="Create Character", command=lambda: create_character(characters))
    create_button.grid(row=6, column=0, columnspan=3, pady=20)


def EditCharacter(root, characters):
    if len(characters) == 0:
        messagebox.showerror("Error", "There are no characters to edit")
        return

    AddCharacter(root, characters, True)


chars = None
u = None

new_character_window = None

# Create variables for creator
name_var = None
health_var = None
ac_var = None
action_var = None
bonus_action_var = None
reaction_var = None
legendary_action_var = None
legendary_action_num = None
legendary_action_num_var = None
legendary_resistance_var = None
legendary_resistance_num = None
legendary_resistance_num_var = None
death_saving_var = None
