import tkinter as tk
from tkinter import messagebox, ttk
import os
from shutil import copyfile
from settings import SettingsDict  # Import SettingsDict from settings.py

# Dictionary to store the state of checkboxes, text input fields, and section enable/disable buttons
config_values = {}

def save_as(section):
    folder_name = "valheim_plus_profiles"
    file_name = "valheim_plus.cfg"
    current_directory = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(current_directory, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'w') as file:
        file.write(f'{section} settings saved!\n')
    messagebox.showinfo("Info", f"{section} settings saved in {file_path}")

def load_defaults(section):
    if section not in SettingsDict:
        messagebox.showerror("Error", f"No defaults found for section: {section}")
        return

    settings_list = SettingsDict[section]

    # Update the enable/disable state based on the default value
    default_enabled = settings_list[0].get("default", True)
    config_values[f"{section}_enabled"] = default_enabled
    section_frame = config_values[f"{section}_frame"]
    toggle_button = config_values[f"{section}_toggle_button"]
    toggle_section(section_frame, toggle_button, f"{section}_enabled", force_state=default_enabled)

    for setting in settings_list[1:]:
        variable_name = setting.get("variable_name", "")
        default_value = setting.get("default_value", "")

        if setting.get("type") == "checkbox":
            config_values[variable_name] = default_value
            setting['var'].set(default_value)
        else:
            config_values[variable_name] = default_value
            setting['var'].set(default_value)

def save_configuration():
    file_name = file_list_combobox.get().strip()
    if not file_name:
        messagebox.showerror("Error", "Enter new file name")
        return

    folder_name = "valheim_plus_configurations"
    current_directory = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(folder_name)
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, f"{file_name}.cfg")

    if os.path.exists(file_path):
        overwrite = messagebox.askyesno("Overwrite", "File with this name already exists. Do you want to overwrite it?")
        if not overwrite:
            return

    with open(file_path, 'w') as file:
        for section, settings_list in SettingsDict.items():
            file.write(f'[{section}]\n')
            enabled_status = config_values.get(f"{section}_enabled", True)
            file.write(f'enabled={str(enabled_status).lower()}\n')
            for setting in settings_list[1:]:
                variable_name = setting.get("variable_name", "")
                current_value = config_values.get(variable_name, "")
                if isinstance(current_value, bool):
                    current_value = str(current_value).lower()
                file.write(f'{variable_name}={current_value}\n')
            file.write('\n')

    messagebox.showinfo("Info", f"Configuration saved as {file_path}")
    refresh_file_list()

def load_selected_file(event=None):
    selected_file = file_list_combobox.get()
    if not selected_file:
        messagebox.showerror("Error", "Please select a file to load.")
        return

    if selected_file == "DEFAULT":
        for section in SettingsDict.keys():
            load_defaults(section)
        messagebox.showinfo("Info", "Default settings loaded.")
        return

    folder_name = "valheim_plus_configurations"
    current_directory = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(folder_name)
    source_path = os.path.join(folder_path, f"{selected_file}.cfg")

    if not os.path.exists(source_path):
        messagebox.showerror("Error", f"File {selected_file} does not exist.")
        return

    # Read the .cfg file and update the configuration
    section = None
    config_data = {}

    with open(source_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                section = line[1:-1]
                config_data[section] = {}
            elif section and '=' in line:
                var_name, var_value = line.split('=', 1)
                config_data[section][var_name.strip()] = var_value.strip()

    # Update config_values and UI
    for section, settings_list in SettingsDict.items():
        if section not in config_data:
            messagebox.showerror("Error", f"Section [{section}] missing in the configuration file. The file might be corrupted.")
            return

        section_data = config_data[section]
        enabled_status = section_data.get('enabled', 'true').lower() == 'true'
        config_values[f"{section}_enabled"] = enabled_status
        section_frame = config_values[f"{section}_frame"]
        toggle_button = config_values[f"{section}_toggle_button"]
        toggle_section(section_frame, toggle_button, f"{section}_enabled", force_state=enabled_status)

        for setting in settings_list[1:]:
            variable_name = setting.get("variable_name", "")
            if variable_name not in section_data:
                messagebox.showerror("Error", f"Variable {variable_name} missing in section [{section}] in the configuration file. The file might be corrupted.")
                return

            current_value = section_data[variable_name]
            if setting.get("type") == "checkbox":
                current_value = current_value.lower() == 'true'
            config_values[variable_name] = current_value
            setting['var'].set(current_value)

    messagebox.showinfo("Info", f"Configuration loaded from {source_path}")

def delete_selected_file():
    selected_file = file_list_combobox.get()
    if not selected_file:
        messagebox.showerror("Error", "Please select a file to delete.")
        return

    folder_name = "valheim_plus_configurations"
    current_directory = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(folder_name)
    file_path = os.path.join(folder_path, f"{selected_file}.cfg")

    if os.path.exists(file_path):
        os.remove(file_path)
        messagebox.showinfo("Info", f"Configuration {selected_file} deleted.")
        refresh_file_list()
    else:
        messagebox.showerror("Error", f"File {selected_file} does not exist.")

def refresh_file_list():
    folder_name = "valheim_plus_configurations"
    current_directory = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(folder_name)
    
    # Ensure the directory exists
    os.makedirs(folder_path, exist_ok=True)
    
    files = [os.path.splitext(f)[0] for f in os.listdir(folder_path) if f.endswith('.cfg')]
    file_list_combobox['values'] = ["DEFAULT"] + files
    file_list_combobox.set("DEFAULT")  # Set "DEFAULT" as the initial value

def update_config_value(variable_name, value):
    config_values[variable_name] = value

def toggle_section(section_frame, toggle_button, var_name, force_state=None):
    new_state = force_state if force_state is not None else not config_values[var_name]
    config_values[var_name] = new_state
    toggle_button.config(text="Disable" if new_state else "Enable")
    for child in section_frame.winfo_children():
        if isinstance(child, (tk.Entry, tk.Checkbutton)):
            child.configure(state="normal" if new_state else "disabled")
        elif isinstance(child, tk.Frame):  # If the child is a frame, update its children
            for subchild in child.winfo_children():
                if isinstance(subchild, (tk.Entry, tk.Checkbutton)):
                    subchild.configure(state="normal" if new_state else "disabled")

def run_valheim():
    selected_file = file_list_combobox.get()
    if not selected_file:
        messagebox.showerror("Error", "Please select a file to verify.")
        return

    if selected_file == "DEFAULT":
        for section in SettingsDict.keys():
            load_defaults(section)
        messagebox.showinfo("Info", "Default settings loaded.")
        return

    folder_name = "valheim_plus_configurations"
    current_directory = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(folder_name)
    source_path = os.path.join(folder_path, f"{selected_file}.cfg")

    if not os.path.exists(source_path):
        messagebox.showerror("Error", f"File {selected_file} does not exist.")
        return

    # Read the .cfg file and compare with current configuration
    section = None
    config_data = {}

    with open(source_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('[') and line.endswith(']'):
                section = line[1:-1]
                config_data[section] = {}
            elif section and '=' in line:
                var_name, var_value = line.split('=', 1)
                config_data[section][var_name.strip()] = var_value.strip()

    changes = False
    for section, settings_list in SettingsDict.items():
        if section not in config_data:
            messagebox.showerror("Error", f"Section [{section}] missing in the configuration file. The file might be corrupted.")
            return

        section_data = config_data[section]
        enabled_status = section_data.get('enabled', 'true').lower() == 'true'
        if enabled_status != config_values.get(f"{section}_enabled", True):
            changes = True
            break

        for setting in settings_list[1:]:
            variable_name = setting.get("variable_name", "")
            if variable_name not in section_data:
                messagebox.showerror("Error", f"Variable {variable_name} missing in section [{section}] in the configuration file. The file might be corrupted.")
                return

            current_value = section_data[variable_name]
            if setting.get("type") == "checkbox":
                current_value = current_value.lower() == 'true'
            if current_value != config_values.get(variable_name, ""):
                changes = True
                break

        if changes:
            break

    if not changes:
        # Save the configuration to \BepInEx\config\valheim_plus.cfg
        bep_path = os.path.join(current_directory, "BepInEx", "config")
        os.makedirs(bep_path, exist_ok=True)
        bep_file_path = os.path.join(bep_path, "valheim_plus.cfg")

        with open(bep_file_path, 'w') as file:
            for section, settings_list in SettingsDict.items():
                file.write(f'[{section}]\n')
                enabled_status = config_values.get(f"{section}_enabled", True)
                file.write(f'enabled={str(enabled_status).lower()}\n')
                for setting in settings_list[1:]:
                    variable_name = setting.get("variable_name", "")
                    current_value = config_values.get(variable_name, "")
                    if isinstance(current_value, bool):
                        current_value = str(current_value).lower()
                    file.write(f'{variable_name}={current_value}\n')
                file.write('\n')

        messagebox.showinfo("Info", f"Configuration saved as {bep_file_path}")
    else:
        overwrite = messagebox.askyesno("Overwrite", "Current configuration differs from the selected file. Do you want to overwrite changes?")
        if overwrite:
            save_configuration()

def populate_settings():
    for idx, (key, settings_list) in enumerate(SettingsDict.items(), start=1):
        section_frame = tk.Frame(configure_section_frame, bd=2, relief="groove", padx=5, pady=5)
        section_frame.grid(row=idx, column=0, padx=5, pady=5, sticky="nsew")

        label_button_frame = tk.Frame(section_frame)
        label_button_frame.pack(anchor="w", fill="x", expand=True)

        iter_label = tk.Label(label_button_frame, text=str(idx), font=("Arial", 10))
        iter_label.pack(side="left", padx=5, pady=5)

        section_label = tk.Label(label_button_frame, text=key, font=("Arial", 10))
        section_label.pack(side="left", padx=5, pady=5)

        toggle_button = tk.Button(label_button_frame, text="Disable" if settings_list[0].get("default", True) else "Enable")
        toggle_button.config(command=lambda sf=section_frame, tb=toggle_button, vn=f"{key}_enabled": toggle_section(sf, tb, vn))
        toggle_button.pack(side="left", padx=5, pady=5)

        default_button = tk.Button(label_button_frame, text="Default", command=lambda k=key: load_defaults(k))
        default_button.pack(side="left", padx=5, pady=5)

        description = settings_list[0].get("description", "")
        default_enabled = settings_list[0].get("default", True)
        config_values[f"{key}_enabled"] = default_enabled
        config_values[f"{key}_frame"] = section_frame
        config_values[f"{key}_toggle_button"] = toggle_button

        description_label = tk.Label(section_frame, text=description, font=("Arial", 10), anchor="w", justify="left")
        description_label.pack(fill="x", padx=5, pady=5, anchor="w")

        for setting in settings_list[1:]:
            additional_description = setting.get("description", "")
            variable_name = setting.get("variable_name", "")
            default_value = setting.get("default_value", "")

            additional_desc_frame = tk.Frame(section_frame)
            additional_desc_frame.pack(anchor="w", fill="x", padx=5, pady=5)

            additional_desc_label = tk.Label(additional_desc_frame, text=additional_description, font=("Arial", 10), anchor="w", justify="left")
            additional_desc_label.pack(anchor="w", padx=5, pady=5)

            if setting.get("type") == "checkbox":
                var = tk.BooleanVar(value=default_value)
                config_values[variable_name] = var.get()
                var.trace_add("write", lambda *args, var=var, vn=variable_name: update_config_value(vn, var.get()))
                checkbox = tk.Checkbutton(additional_desc_frame, variable=var)
                checkbox.pack(side="left", padx=5, pady=5)
                setting['var'] = var

                var_label = tk.Label(additional_desc_frame, text=variable_name, font=("Arial", 10))
                var_label.pack(side="left", padx=5, pady=5)
            else:
                var = tk.StringVar(value=default_value)
                config_values[variable_name] = var.get()
                var.trace_add("write", lambda *args, var=var, vn=variable_name: update_config_value(vn, var.get()))
                entry = tk.Entry(additional_desc_frame, textvariable=var)
                entry.pack(side="left", padx=5, pady=5)
                setting['var'] = var

                var_label = tk.Label(additional_desc_frame, text=variable_name, font=("Arial", 10))
                var_label.pack(side="left", padx=5, pady=5)

        if not default_enabled:
            for child in section_frame.winfo_children():
                if isinstance(child, (tk.Entry, tk.Checkbutton)):
                    child.configure(state="disabled")
                elif isinstance(child, tk.Frame):  # If the child is a frame, update its children
                    for subchild in child.winfo_children():
                        if isinstance(subchild, (tk.Entry, tk.Checkbutton)):
                            subchild.configure(state="disabled")

root = tk.Tk()
root.title("Valheim+ Configurator")
root.geometry("800x500")
icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon_mini.ico")
root.iconbitmap(icon_path)

main_frame = tk.Frame(root, bd=2, relief="groove", padx=0, pady=0)
main_frame.grid(row=0, column=0, sticky="nsew")
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

general_section_frame = tk.Frame(main_frame, bd=1, relief="groove", padx=0, pady=0)
general_section_frame.grid(row=0, column=0, sticky="nsew")

configure_section_canvas = tk.Canvas(main_frame, bd=1, highlightthickness=0)
configure_section_canvas.grid(row=1, column=0, sticky="nsew")

configure_section_scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=configure_section_canvas.yview)
configure_section_scrollbar.grid(row=1, column=1, sticky="ns")

configure_section_frame = tk.Frame(configure_section_canvas, padx=0, pady=0)
window_id = configure_section_canvas.create_window((0, 0), window=configure_section_frame, anchor="nw", width=root.winfo_width())

def configure_scroll_region(event):
    configure_section_canvas.configure(scrollregion=configure_section_canvas.bbox("all"))

def on_canvas_resize(event):
    canvas_width = event.width
    configure_section_canvas.itemconfig(window_id, width=canvas_width)

def on_mouse_wheel(event):
    configure_section_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def on_enter(event):
    root.bind_all("<MouseWheel>", on_mouse_wheel)

def on_leave(event):
    root.unbind_all("<MouseWheel>")

configure_section_canvas.bind("<Configure>", on_canvas_resize)
configure_section_frame.bind("<Configure>", configure_scroll_region)

main_frame.grid_rowconfigure(0, weight=0)
main_frame.grid_rowconfigure(1, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

file_list_label = tk.Label(general_section_frame, text="Saved Configurations:", font=("Arial", 10))
file_list_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

file_list_combobox = ttk.Combobox(general_section_frame)
file_list_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
file_list_combobox.bind("<<ComboboxSelected>>", load_selected_file)  # Bind the event to the combobox

save_button = tk.Button(general_section_frame, text="Save", command=save_configuration)
save_button.grid(row=0, column=2, padx=5, pady=5, sticky="w")

delete_button = tk.Button(general_section_frame, text="Delete", command=delete_selected_file)
delete_button.grid(row=0, column=3, padx=5, pady=5, sticky="w")

run_button = tk.Button(general_section_frame, text="Run Valheim.exe", command=run_valheim)
run_button.grid(row=0, column=4, padx=5, pady=5, sticky="w")

configure_section_canvas.configure(yscrollcommand=configure_section_scrollbar.set)
configure_section_frame.bind("<Enter>", on_enter)
configure_section_frame.bind("<Leave>", on_leave)

refresh_file_list()
populate_settings()

# Add hover popups
def add_hover_popup(widget, text):
    def on_enter(event):
        tooltip = tk.Toplevel()
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{widget.winfo_rootx() + 20}+{widget.winfo_rooty() + 20}")
        label = tk.Label(tooltip, text=text, background="yellow", relief="solid", borderwidth=1, font=("Arial", 10))
        label.pack()
        widget.tooltip = tooltip

    def on_leave(event):
        widget.tooltip.destroy()

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

add_hover_popup(run_button, "Click to run Valheim with the current configuration.")
add_hover_popup(save_button, "Save the current configuration.")
add_hover_popup(delete_button, "Delete the selected configuration.")
add_hover_popup(file_list_combobox, "Select a configuration to load or delete.")

root.mainloop()
