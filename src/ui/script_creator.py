"""
Script Creator module
Dialog for creating new scripts with templates
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

def create_new_script_dialog(parent, category, category_dir, refresh_callback):
    """Create a new script in the selected category"""
    
    # Get parent's color scheme
    primary_color = parent.primary_color
    secondary_color = parent.secondary_color
    accent_color = parent.accent_color
    text_color = parent.text_color
    bg_light = parent.bg_light
    
    dialog = tk.Toplevel(parent)
    dialog.title("Create New Script")
    dialog.geometry("650x580")  # Larger size for better spacing
    dialog.transient(parent)  # Make dialog modal
    dialog.grab_set()
    dialog.configure(bg=secondary_color)
    
    # Center the dialog on the parent window
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (650 // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (580 // 2)
    dialog.geometry(f"+{x}+{y}")
    
    # Create a frame with padding
    form_frame = ttk.Frame(dialog, padding=20)
    form_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title with category info
    header_frame = ttk.Frame(form_frame)
    header_frame.pack(fill=tk.X, pady=(0, 20))
    
    ttk.Label(header_frame, 
             text="Create New Script", 
             font=("Segoe UI", 16, "bold"),
             foreground=primary_color).pack(side=tk.LEFT)
    
    ttk.Label(header_frame,
             text=f"Category: {category}",
             font=("Segoe UI", 12)).pack(side=tk.RIGHT)
    
    # Input fields in a grid
    input_frame = ttk.Frame(form_frame)
    input_frame.pack(fill=tk.X, pady=(0, 15))
    
    # Script Name
    ttk.Label(input_frame, 
             text="Script Name:", 
             font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=10)
    script_name_var = tk.StringVar()
    script_name_entry = ttk.Entry(input_frame, textvariable=script_name_var, width=40, font=("Segoe UI", 10))
    script_name_entry.grid(row=0, column=1, sticky=tk.W, pady=10, padx=(10, 0))
    
    # Developer
    ttk.Label(input_frame, 
             text="Developer:", 
             font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=10)
    developer_var = tk.StringVar(value="MikeTheTech")  # Default value
    developer_entry = ttk.Entry(input_frame, textvariable=developer_var, width=40, font=("Segoe UI", 10))
    developer_entry.grid(row=1, column=1, sticky=tk.W, pady=10, padx=(10, 0))
    
    # Developer Link
    ttk.Label(input_frame, 
             text="Developer Link:", 
             font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=10)
    link_var = tk.StringVar(value="https://github.com/itsmikethetech")  # Default value
    link_entry = ttk.Entry(input_frame, textvariable=link_var, width=50, font=("Segoe UI", 10))
    link_entry.grid(row=2, column=1, sticky=tk.W, pady=10, padx=(10, 0))
    
    # Script Type
    ttk.Label(input_frame, 
             text="Script Type:", 
             font=("Segoe UI", 10, "bold")).grid(row=3, column=0, sticky=tk.W, pady=10)
    script_type_var = tk.StringVar(value=".py")
    script_type_combo = ttk.Combobox(input_frame, 
                                    textvariable=script_type_var, 
                                    values=[".py", ".ps1", ".bat", ".cmd", ".exe"], 
                                    width=15,
                                    font=("Segoe UI", 10),
                                    state="readonly")
    script_type_combo.grid(row=3, column=1, sticky=tk.W, pady=10, padx=(10, 0))
    
    # Description
    ttk.Label(input_frame, 
             text="Description:", 
             font=("Segoe UI", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=10)
    description_var = tk.StringVar()
    description_entry = ttk.Entry(input_frame, textvariable=description_var, width=50, font=("Segoe UI", 10))
    description_entry.grid(row=4, column=1, sticky=tk.W, pady=10, padx=(10, 0))
    
    # Undoable with tooltip
    undoable_frame = ttk.Frame(input_frame)
    undoable_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=10)
    
    undoable_var = tk.BooleanVar(value=False)
    undoable_check = ttk.Checkbutton(undoable_frame, 
                                    text="Script is undoable", 
                                    variable=undoable_var,
                                    style="TCheckbutton")
    undoable_check.pack(side=tk.LEFT)
    
    # Info icon with tooltip
    info_label = ttk.Label(undoable_frame, text="ℹ️", cursor="hand2")
    info_label.pack(side=tk.LEFT, padx=5)
    
    # Create tooltip for the info icon
    from src.ui.tooltip import ToolTip
    undo_tooltip = ToolTip(info_label)
    info_label.bind("<Enter>", lambda e: undo_tooltip.showtip(
        "Undoable scripts can be reverted after execution. This requires implementing the undo logic in your script."))
    info_label.bind("<Leave>", lambda e: undo_tooltip.hidetip())
    
    # Undo Description
    ttk.Label(input_frame, 
             text="Undo Description:", 
             font=("Segoe UI", 10, "bold")).grid(row=6, column=0, sticky=tk.W, pady=10)
    undo_desc_var = tk.StringVar()
    undo_desc_entry = ttk.Entry(input_frame, textvariable=undo_desc_var, width=50, font=("Segoe UI", 10))
    undo_desc_entry.grid(row=6, column=1, sticky=tk.W, pady=10, padx=(10, 0))
    
    # Template Content
    template_frame = ttk.Frame(form_frame)
    template_frame.pack(fill=tk.BOTH, expand=True, pady=5)
    
    ttk.Label(template_frame, 
             text="Template:", 
             font=("Segoe UI", 12, "bold"),
             foreground=primary_color).pack(anchor=tk.W, pady=(0, 5))
    
    template_text = scrolledtext.ScrolledText(template_frame, 
                                            width=78, 
                                            height=15,
                                            wrap=tk.NONE,
                                            background=bg_light,
                                            foreground=text_color,
                                            insertbackground=text_color,
                                            selectbackground=primary_color,
                                            font=("Consolas", 10))
    template_text.pack(fill=tk.BOTH, expand=True)
    
    # Update template based on user input
    def update_template(*args):
        script_type = script_type_var.get()
        name = script_name_var.get() or "Script Name"
        developer = developer_var.get() or "Unknown Developer"
        link = link_var.get() or ""
        desc = description_var.get() or "Script Description"
        undoable = "Yes" if undoable_var.get() else "No"
        undo_desc = undo_desc_var.get() or "Reverts the changes made by this script"
        
        if script_type == ".exe":
            template_text.delete(1.0, tk.END)
            template_text.insert(tk.END, "EXE files cannot be created or modified through this interface.\nPlease select a different script type.")
            template_text.config(state="disabled")
            undoable_check.config(state="disabled")
            undoable_var.set(False)
            undo_desc_entry.config(state="disabled")
            return
        else:
            template_text.config(state="normal")
            undoable_check.config(state="normal")
        
        if script_type == ".py":
            template_text.delete(1.0, tk.END)
            template_text.insert(tk.END, f"""# NAME: {name}
# DEVELOPER: {developer}
# LINK: {link}
# DESCRIPTION: {desc}
# UNDOABLE: {undoable}
# UNDO_DESC: {undo_desc}
#
# This is a Python script template with undo capability

import os
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description='{desc}')
    parser.add_argument('--undo', action='store_true', help='Undo the changes made by this script')
    args = parser.parse_args()
    
    if args.undo:
        perform_undo()
    else:
        perform_action()

def perform_action():
    print("Performing main action...")
    # Your main code here
    
def perform_undo():
    print("Performing undo action...")
    # Your undo code here

if __name__ == "__main__":
    main()
""")
        elif script_type == ".ps1":
            template_text.delete(1.0, tk.END)
            template_text.insert(tk.END, f"""# NAME: {name}
# DEVELOPER: {developer}
# LINK: {link}
# DESCRIPTION: {desc}
# UNDOABLE: {undoable}
# UNDO_DESC: {undo_desc}
#
# This is a PowerShell script template with undo capability

param (
    [switch]$Undo
)

function Perform-Action {{
    Write-Host "Performing main action..."
    # Your main code here
}}

function Perform-Undo {{
    Write-Host "Performing undo action..."
    # Your undo code here
}}

if ($Undo) {{
    Perform-Undo
}} else {{
    Perform-Action
}}
""")
        elif script_type in [".bat", ".cmd"]:
            template_text.delete(1.0, tk.END)
            template_text.insert(tk.END, f""":: NAME: {name}
:: DEVELOPER: {developer}
:: LINK: {link}
:: DESCRIPTION: {desc}
:: UNDOABLE: {undoable}
:: UNDO_DESC: {undo_desc}
::
:: This is a Batch script template with undo capability

@echo off

if "%1"=="undo" goto :undo

:main
echo Performing main action...
:: Your main code here
goto :end

:undo
echo Performing undo action...
:: Your undo code here
goto :end

:end
pause
""")
            
        if undoable_var.get():
            undo_desc_entry.config(state="normal")
        else:
            undo_desc_entry.config(state="disabled")
    
    # Bind updates
    script_type_var.trace("w", update_template)
    script_name_var.trace("w", update_template)
    developer_var.trace("w", update_template)
    link_var.trace("w", update_template)
    description_var.trace("w", update_template)
    undoable_var.trace("w", update_template)
    undo_desc_var.trace("w", update_template)
    
    update_template()
    
    # Buttons
    button_frame = ttk.Frame(form_frame)
    button_frame.pack(fill=tk.X, pady=(20, 0))
    
    def create_script():
        name = script_name_var.get().strip()
        script_type = script_type_var.get()
        if not name:
            messagebox.showerror("Error", "Script name cannot be empty")
            return
        
        if script_type == ".exe":
            messagebox.showerror("Error", "Cannot create EXE files. Please select a different script type.")
            return
        
        file_name = f"{name}{script_type}" if not name.endswith(script_type) else name
        template = template_text.get(1.0, tk.END)
        script_path = os.path.join(category_dir, file_name)
        
        if os.path.exists(script_path):
            if not messagebox.askyesno("File Exists", f"File '{file_name}' already exists. Overwrite?"):
                return
        
        try:
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(template)
            
            print(f"Created new script: {file_name} in {category}")
            if refresh_callback:
                refresh_callback(None)
            dialog.destroy()
        except Exception as e:
            error_msg = f"Failed to create script: {str(e)}"
            messagebox.showerror("Error", error_msg)
            print(error_msg)
    
    ttk.Button(button_frame, 
              text="Cancel", 
              width=15,
              command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    create_btn = ttk.Button(button_frame, 
                           text="Create", 
                           width=15,
                           command=create_script)
    create_btn.pack(side=tk.RIGHT, padx=5)
    
    script_name_entry.focus_set()