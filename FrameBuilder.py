import tkinter as tk
from tkinter import ttk
import uuid

import MessageDevice
import DNDHealthTracker


def update_dm_screen(entity, stat, code):
    if len(frames.keys()) > DNDHealthTracker.initiative_count:
        if entity["UUID"] == list(frames.keys())[DNDHealthTracker.initiative_count]:
            MessageDevice.WriteMessageWithData("U99", [0, code, entity[stat]])


def update_health(entity, label, amount):
    """Update the health of the entity."""
    entity["Health"] = max(0, min(entity["Max_Health"], entity["Health"] + amount))
    label.config(text=f"{entity['Health']}/{entity['Max_Health']}")

    if entity['Device'] is not None:
        MessageDevice.WriteMessageWithData("U" + str(entity['Device']), [entity["Page"], "H", entity["Health"]])
    update_dm_screen(entity, "Health", "H")

    if entity["Health"] == 0:
        trigger_death_saving(entity)


def update_temp_health(entity, label, amount):
    """Update the health of the entity."""
    entity["TempHealth"] = max(0, entity["TempHealth"] + amount)
    label.config(text=f"{entity['TempHealth']}")
    if entity['Device'] is not None:
        MessageDevice.WriteMessageWithData("U" + str(entity['Device']), [entity["Page"], "T", entity["TempHealth"]])
    update_dm_screen(entity, "TempHealth", "T")


def adjust_health_from_input(entity, health_label, input_box):
    """Adjust the health based on the input box value."""
    try:
        delta = int(input_box.get())
        input_box.delete(0, tk.END)
        update_health(entity, health_label, delta)
    except ValueError:
        input_box.delete(0, tk.END)  # Clear invalid input


def reset_actions(entity, action_buttons, legend_label):
    """Reset all actions and legendary actions."""
    entity["Action"] = True
    entity["BonusAction"] = True
    entity["Reaction"] = True
    entity["LegendaryActionNum"] = entity["LegendaryActionMax"]
    for button in action_buttons:
        button.config(state="normal")
    if legend_label:
        legend_label.config(text=f"Remaining {entity['LegendaryActionNum']}")

    if entity['Device'] is not None:
        MessageDevice.WriteMessageWithData("U" + str(entity['Device']), [entity["Page"], "A", True])
        MessageDevice.WriteMessageWithData("U" + str(entity['Device']), [entity["Page"], "B", True])
        MessageDevice.WriteMessageWithData("U" + str(entity['Device']), [entity["Page"], "R", True])
    update_dm_screen(entity, "Action", "A")
    update_dm_screen(entity, "BonusAction", "B")
    update_dm_screen(entity, "Reaction", "R")


def reset_resistances(entity, resist_label):
    """Reset legendary resistances."""
    entity["LegendaryResistanceNum"] = entity["LegendaryResistanceMax"]
    resist_label.config(text=f"Remaining {entity['LegendaryResistanceNum']}")


def use_action(button, name, entity):
    """Disable the action button."""
    button.config(state="disabled")

    code = ""
    if name == "action":
        entity["Action"] = False
        code = "A"
        name = "Action"
    elif name == "bonusAction":
        entity["BonusAction"] = False
        code = "B"
        name = "BonusAction"
    elif name == "reaction":
        entity["Reaction"] = False
        code = "R"
        name = "Reaction"

    if entity['Device'] is not None:
        MessageDevice.WriteMessageWithData("U" + str(entity['Device']), [entity["Page"], code, False])
    update_dm_screen(entity, name, code)


def use_legendary_action(entity, label):
    """Use a legendary action if available."""
    if entity["LegendaryActionNum"] > 0:
        entity["LegendaryActionNum"] -= 1
        label.config(text=f"Remaining {entity['LegendaryActionNum']}")


def use_legendary_resistance(entity, label):
    """Use a legendary action if available."""
    if entity["LegendaryResistanceNum"] > 0:
        entity["LegendaryResistanceNum"] -= 1
        label.config(text=f"Remaining {entity['LegendaryResistanceNum']}")


def trigger_death_saving(entity):
    """Trigger the death saving UI."""
    entity_frame = frames[entity["UUID"]]
    for widget in entity_frame.winfo_children():
        widget.destroy()

    if not entity["DeathSaving"]:
        show_revive_button(entity, entity_frame)
        return

    tk.Label(entity_frame, text=f"Name: {entity['Name']}", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=3)

    dots_success = [tk.Label(entity_frame, text="○", font=("Arial", 14)) for _ in range(3)]
    dots_failure = [tk.Label(entity_frame, text="○", font=("Arial", 14)) for _ in range(3)]
    deathDots[entity["UUID"]] = (dots_success, dots_failure)

    btn_success = tk.Button(entity_frame, text="Success", command=lambda: handle_save(entity, "success"))
    btn_failure = tk.Button(entity_frame, text="Failure", command=lambda: handle_save(entity, "failure"))

    for i, dot in enumerate(dots_success):
        dot.grid(row=1, column=i, padx=30)

    btn_success.grid(row=2, column=0, columnspan=2, pady=5)
    btn_failure.grid(row=2, column=1, columnspan=2, pady=5)

    for i, dot in enumerate(dots_failure):
        dot.grid(row=3, column=i, padx=5)

    update_dots(dots_success, entity["DeathSuccess"], "green")
    update_dots(dots_failure, entity["DeathFail"], "red")


def handle_save(entity, save_type):
    if save_type == "success":
        entity["DeathSuccess"] += 1
    elif save_type == "failure":
        entity["DeathFail"] += 1

    if deathDots[entity["UUID"]] is not None:
        update_dots(deathDots[entity["UUID"]][0], entity["DeathSuccess"], "green")
        update_dots(deathDots[entity["UUID"]][1], entity["DeathFail"], "red")

    if entity["DeathSuccess"] == 3:
        entity["Health"] = 1
        entity["DeathSuccess"] = 0
        entity["DeathFail"] = 0
        reset_to_normal(entity, frames[entity["UUID"]])
    elif entity["DeathFail"] == 3:
        entity["DeathSuccess"] = 0
        entity["DeathFail"] = 0
        show_revive_button(entity, frames[entity["UUID"]])

    if entity['Device'] is not None:
        if save_type == "success":
            MessageDevice.WriteMessageWithData("U" + str(entity['Device']), [entity["Page"], 'S', False])
        elif save_type == "failure":
            MessageDevice.WriteMessageWithData("U" + str(entity['Device']), [entity["Page"], 'F', False])
    if save_type == "success":
        update_dm_screen(entity, "DeathSuccess", 'S')
    elif save_type == "failure":
        update_dm_screen(entity, "DeathFail", 'F')


def update_dots(dots, count, color):
    for i in range(3):
        dots[i].config(text="●" if i < count else "○", fg=color)


def show_revive_button(entity, entity_frame):
    deathDots[entity["UUID"]] = None

    """Display a revive button after failures are filled."""
    for widget in entity_frame.winfo_children():
        widget.destroy()

    def revive():
        entity["Health"] = entity["Max_Health"]  # Restore full health
        reset_to_normal(entity, entity_frame)

    tk.Label(entity_frame, text=f"Name: {entity['Name']}", font=("Arial", 12, "bold")).pack(pady=10)
    tk.Button(entity_frame, text="Revive", command=revive, font=("Arial", 14)).pack(pady=20, padx=80)


def reset_to_normal(entity, entity_frame):
    deathDots[entity["UUID"]] = None

    """Reset the widget to its normal state."""
    idx = entity_frame.grid_info()['column'] + (entity_frame.grid_info()['row'] - 1) * 4

    for widget in entity_frame.winfo_children():
        widget.destroy()
    create_entity_widget(entity, entity_frame.master, idx)
    entity_frame.destroy()


def update_entity_widget(entity):
    ac_labels[entity["UUID"]]["text"] = f"AC: {entity['AC']}"
    health_labels[entity["UUID"]]["text"] = f"{entity['Health']}/{entity['Max_Health']}"
    temp_labels[entity["UUID"]]["text"] = f"{entity['TempHealth']}"

    action_buttons = action_buttons_list[entity["UUID"]]
    action_buttons[0].config(state="normal" if entity["Action"] else "disabled")
    action_buttons[1].config(state="normal" if entity["BonusAction"] else "disabled")
    action_buttons[2].config(state="normal" if entity["Reaction"] else "disabled")

def create_entity_widget(entity, parent, idx):
    """Create a widget for the entity."""
    frame = tk.Frame(parent, bd=1, highlightbackground=("#606060" if DNDHealthTracker.initiative_count == idx else "#A0A0A0"), highlightthickness=3, relief="groove", padx=14, pady=15)
    frame.grid(row=1 + int(idx / 4), column=idx % 4, padx=4, pady=4)
    frames[entity["UUID"]] = frame

    # Configure grid for equal column widths
    for i in range(3):
        frame.grid_columnconfigure(i, weight=1, uniform="equal")

    # Name
    tk.Label(frame, text=f"{entity['Name']}", font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=4)
    ac_label = tk.Label(frame, text=f"AC: {entity['AC']}", name="ac")
    ac_label.grid(row=1, column=0, columnspan=4)
    ac_labels[entity["UUID"]] = ac_label


    # Health Buttons
    tk.Label(frame, text="Health: ").grid(row=2, column=0)

    btn_health_minus = tk.Button(frame, text="-", command=lambda: update_health(entity, health_label, -1))
    btn_health_minus.grid(row=2, column=0, columnspan=2)

    health_label = tk.Label(frame, text=f"{entity['Health']}/{entity['Max_Health']}", font=("Arial", 10), name="health")
    health_label.grid(row=2, column=1)
    health_labels[entity["UUID"]] = health_label

    btn_health_plus = tk.Button(frame, text="+", command=lambda: update_health(entity, health_label, 1))
    btn_health_plus.grid(row=2, column=1, columnspan=2)

    # Health Text Input
    health_input = tk.Entry(frame, width=5)
    health_input.grid(row=2, column=2, padx=5)
    health_input.bind(
        "<Return>", lambda event: adjust_health_from_input(entity, health_label, health_input)
    )

    # Temp Health Buttons
    tk.Label(frame, text="Temp Health: ", font=("Arial", 8)).grid(row=3, column=0)

    btn_temp_health_minus = tk.Button(frame, text="-", command=lambda: update_temp_health(entity, temp_health_label, -1))
    btn_temp_health_minus.grid(row=3, column=0, columnspan=2)

    temp_health_label = tk.Label(frame, text=f"{entity['TempHealth']}", font=("Arial", 10), name="tempHealth")
    temp_health_label.grid(row=3, column=1)
    temp_labels[entity["UUID"]] = temp_health_label

    btn_temp_health_plus = tk.Button(frame, text="+", command=lambda: update_temp_health(entity, temp_health_label, 1))
    btn_temp_health_plus.grid(row=3, column=1, columnspan=2)

    # Actions
    action_buttons = [
        tk.Button(frame, text="Action", command=lambda: use_action(action_buttons[0], 'action', entity),
                  state="normal" if entity["Action"] else "disabled"),
        tk.Button(frame, text="Bonus Action", command=lambda: use_action(action_buttons[1], 'bonusAction', entity),
                  state="normal" if entity["BonusAction"] else "disabled"),
        tk.Button(frame, text="Reaction", command=lambda: use_action(action_buttons[2], 'reaction', entity),
                  state="normal" if entity["Reaction"] else "disabled"),
    ]
    for i, btn in enumerate(action_buttons):
        btn.grid(row=4, column=i)
    action_buttons_list[entity["UUID"]] = action_buttons

    # Legendary Actions
    legend_label = None
    if entity['LegendaryActionMax'] > 0:
        btn_legend = tk.Button(frame, text="Use Legendary", command=lambda: use_legendary_action(entity, legend_label))
        btn_legend.grid(row=5, column=0, columnspan=2)

        legend_label = tk.Label(frame, text=f"Remaining {entity['LegendaryActionNum']}")
        legend_label.grid(row=5, column=1, columnspan=2)

    # Legendary Resistances
    if entity['LegendaryResistanceMax'] > 0:
        btn_resist = tk.Button(frame, text="Use Resistance", command=lambda: use_legendary_resistance(entity, resist_label))
        btn_resist.grid(row=6, column=0)

        resist_label = tk.Label(frame, text=f"Remaining {entity['LegendaryResistanceNum']}")
        resist_label.grid(row=6, column=1)

        btn_resist_reset = tk.Button(frame, text="Reset", command=lambda: reset_resistances(entity, resist_label))
        btn_resist_reset.grid(row=6, column=2)

    # Reset Button
    btn_reset = tk.Button(frame, text="Reset", command=lambda: reset_actions(entity, action_buttons, legend_label))
    #btn_reset.grid(row=7, column=0, columnspan=3, pady=5)

    update_health(entity, health_label, 0)

    return [frame, btn_reset]

frames = {}
ac_labels = {}
health_labels = {}
temp_labels = {}
action_buttons_list = {}
deathDots = {}
