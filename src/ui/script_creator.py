"""
Script Creator module
Modern responsive dialog for creating new scripts with templates
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter.ttk import Scrollbar

def create_new_script_dialog(parent, category, category_dir, refresh_callback):
    """Create a new script in the selected category with a modern responsive UI"""
    
    try:
        # Try to get modern styling from parent app
        primary_color = parent.primary_color
        primary_light = parent.primary_light
        primary_dark = parent.primary_dark
        secondary_color = parent.secondary_color
        accent_color = parent.accent_color
        text_color = parent.text_color
        text_secondary = parent.text_secondary
        bg_light = parent.bg_light
        card_bg = parent.card_bg
        border_color = parent.border_color
        success_color = parent.success_color
        warning_color = parent.warning_color
        error_color = parent.error_color
        font_family = parent.font_family
        font_size_small = parent.font_size_small
        font_size_normal = parent.font_size_normal
        font_size_large = parent.font_size_large
        font_size_xlarge = parent.font_size_xlarge
    except AttributeError:
        # Fallbacks if we can't get parent styling
        primary_color = "#3F51B5"
        primary_light = "#7986CB"
        primary_dark = "#303F9F"
        secondary_color = "#F5F5F5"
        accent_color = "#FF4081"
        text_color = "#212121"
        text_secondary = "#757575"
        bg_light = "#FFFFFF"
        card_bg = "#FFFFFF"
        border_color = "#E0E0E0"
        success_color = "#4CAF50"
        warning_color = "#FF9800"
        error_color = "#F44336"
        font_family = _get_system_font()
        font_size_small = 9
        font_size_normal = 10
        font_size_large = 12
        font_size_xlarge = 14
    
    # Create a responsive dialog
    dialog = tk.Toplevel(parent)
    dialog.title("Create New Script")
    dialog.geometry("650x680") 
    dialog.minsize(400, 500)  # Set minimum size for better UX
    dialog.transient(parent)  # Make dialog modal
    dialog.grab_set()
    dialog.configure(bg=secondary_color)
    
    # Center the dialog on the parent window
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (650 // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (680 // 2)
    dialog.geometry(f"+{x}+{y}")
    
    # Create scrollable main container for smaller screens
    main_container = ttk.Frame(dialog)
    main_container.pack(fill=tk.BOTH, expand=True)
    
    # Main canvas with scrollbar for content
    main_canvas = tk.Canvas(main_container, bg=secondary_color, highlightthickness=0)
    main_scrollbar = ttk.Scrollbar(main_container, orient=tk.VERTICAL, command=main_canvas.yview)
    main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    main_canvas.configure(yscrollcommand=main_scrollbar.set)
    
    # Create scrollable form container
    form_container = ttk.Frame(main_canvas, style="Card.TFrame", padding=16)
    form_window = main_canvas.create_window((0, 0), window=form_container, anchor=tk.NW, width=dialog.winfo_width()-30)
    
    # Set up scrollable region
    def configure_scroll_region(event):
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        
    form_container.bind("<Configure>", configure_scroll_region)
    
    # Handle window resize for responsive behavior
    def on_dialog_resize(event):
        canvas_width = event.width - 20
        main_canvas.itemconfig(form_window, width=canvas_width)
        
    dialog.bind("<Configure>", on_dialog_resize)
    
    # Bind mousewheel for scrolling
    def on_mousewheel(event):
        main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
    main_canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    # Modern header with card style
    header_card = ttk.Frame(form_container, style="Card.TFrame", padding=12)
    header_card.pack(fill=tk.X, pady=(0, 16))
    
    # Title with category info and modern styling
    ttk.Label(header_card, 
             text="✨ Create New Script", 
             font=(font_family, font_size_xlarge, "bold"),
             foreground=primary_color,
             background=card_bg,
             style="Heading.TLabel").pack(side=tk.LEFT)
    
    ttk.Label(header_card,
             text=f"Category: {category}",
             font=(font_family, font_size_normal, "bold"),
             foreground=text_secondary,
             background=card_bg).pack(side=tk.RIGHT)
    
    # Form card
    form_card = ttk.Frame(form_container, style="Card.TFrame", padding=16)
    form_card.pack(fill=tk.X, pady=(0, 16))
    
    # Grid container for form fields with responsive layout
    field_grid = ttk.Frame(form_card, style="Card.TFrame")
    field_grid.pack(fill=tk.X, expand=True)
    
    row = 0
    # Script Name with modern label and input
    ttk.Label(field_grid, 
             text="Script Name", 
             font=(font_family, font_size_normal, "bold"),
             foreground=text_color,
             background=card_bg).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
    
    script_name_var = tk.StringVar()
    script_name_entry = ttk.Entry(field_grid, 
                               textvariable=script_name_var, 
                               width=40, 
                               font=(font_family, font_size_normal),
                               style="Search.TEntry")
    script_name_entry.grid(row=row+1, column=0, sticky=tk.EW, pady=(0, 12), padx=(0, 8))
    
    # Script Type with modern dropdown
    ttk.Label(field_grid, 
             text="Script Type", 
             font=(font_family, font_size_normal, "bold"),
             foreground=text_color,
             background=card_bg).grid(row=row, column=1, sticky=tk.W, pady=(0, 4))
    
    script_type_var = tk.StringVar(value=".py")
    script_type_combo = ttk.Combobox(field_grid, 
                                    textvariable=script_type_var, 
                                    values=[".py", ".ps1", ".bat", ".cmd", ".exe"], 
                                    width=15,
                                    font=(font_family, font_size_normal),
                                    state="readonly")
    script_type_combo.grid(row=row+1, column=1, sticky=tk.W, pady=(0, 12))
    
    row += 2
    # Developer
    ttk.Label(field_grid, 
             text="Developer", 
             font=(font_family, font_size_normal, "bold"),
             foreground=text_color,
             background=card_bg).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
    
    developer_var = tk.StringVar(value="MikeTheTech")  # Default value
    developer_entry = ttk.Entry(field_grid, 
                             textvariable=developer_var, 
                             width=40, 
                             font=(font_family, font_size_normal),
                             style="Search.TEntry")
    developer_entry.grid(row=row+1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 12))
    
    row += 2
    # Developer Link
    ttk.Label(field_grid, 
             text="Developer Link", 
             font=(font_family, font_size_normal, "bold"),
             foreground=text_color,
             background=card_bg).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
    
    link_var = tk.StringVar(value="https://github.com/itsmikethetech")  # Default value
    link_entry = ttk.Entry(field_grid, 
                        textvariable=link_var, 
                        width=50, 
                        font=(font_family, font_size_normal),
                        style="Search.TEntry")
    link_entry.grid(row=row+1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 12))
    
    row += 2
    # Description
    ttk.Label(field_grid, 
             text="Description", 
             font=(font_family, font_size_normal, "bold"),
             foreground=text_color,
             background=card_bg).grid(row=row, column=0, sticky=tk.W, pady=(0, 4))
    
    description_var = tk.StringVar()
    description_entry = ttk.Entry(field_grid, 
                               textvariable=description_var, 
                               width=50, 
                               font=(font_family, font_size_normal),
                               style="Search.TEntry")
    description_entry.grid(row=row+1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 12))
    
    row += 2
    # Undoable option with improved UI
    undoable_row = ttk.Frame(field_grid, style="Card.TFrame")
    undoable_row.grid(row=row, column=0, columnspan=2, sticky=tk.EW, pady=(0, 6))
    
    undoable_var = tk.BooleanVar(value=False)
    undoable_check = ttk.Checkbutton(undoable_row, 
                                    text="Script is undoable", 
                                    variable=undoable_var,
                                    style="TCheckbutton")
    undoable_check.pack(side=tk.LEFT)
    
    # Info icon with tooltip for better UX
    from src.ui.tooltip import ToolTip
    info_icon = ttk.Label(undoable_row, 
                        text="ℹ️", 
                        cursor="hand2",
                        background=card_bg)
    info_icon.pack(side=tk.LEFT, padx=5)
    
    # Enhanced tooltip with clearer text
    undo_tooltip = ToolTip(info_icon, wrap_length=350)
    info_icon.bind("<Enter>", lambda e: undo_tooltip.showtip(
        "Undoable scripts can be reverted after execution. This requires implementing the undo logic in your script. Check this option if your script will support being undone."))
    info_icon.bind("<Leave>", lambda e: undo_tooltip.hidetip())
    
    row += 1
    # Undo Description
    undo_desc_label = ttk.Label(field_grid, 
                              text="Undo Description", 
                              font=(font_family, font_size_normal, "bold"),
                              foreground=text_color,
                              background=card_bg)
    undo_desc_label.grid(row=row, column=0, sticky=tk.W, pady=(6, 4))
    
    undo_desc_var = tk.StringVar()
    undo_desc_entry = ttk.Entry(field_grid, 
                             textvariable=undo_desc_var, 
                             width=50, 
                             font=(font_family, font_size_normal),
                             style="Search.TEntry")
    undo_desc_entry.grid(row=row+1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 12))
    
    # Set column weight for responsive layout
    field_grid.columnconfigure(0, weight=3)
    field_grid.columnconfigure(1, weight=1)
    
    # Template card
    template_card = ttk.Frame(form_container, style="Card.TFrame", padding=16)
    template_card.pack(fill=tk.BOTH, expand=True, pady=(0, 16))
    
    # Template header with better visual hierarchy
    ttk.Label(template_card, 
             text="🧩 Template", 
             font=(font_family, font_size_large, "bold"),
             foreground=primary_color,
             background=card_bg,
             style="Heading.TLabel").pack(anchor=tk.W, pady=(0, 8))
    
    # Create a container for the template with improved scrollbar styling
    template_container = ttk.Frame(template_card, style="Card.TFrame")
    template_container.pack(fill=tk.BOTH, expand=True)
    
    # Add horizontal scrollbar with modern styling
    h_scrollbar = Scrollbar(template_container, orient=tk.HORIZONTAL)
    h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    # Add vertical scrollbar with modern styling
    v_scrollbar = Scrollbar(template_container, orient=tk.VERTICAL)
    v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Try to find a good monospace font
    def is_font_available(font_name):
        """Check if a font is available on the system"""
        try:
            from tkinter import font
            return font_name in font.families()
        except:
            return False
            
    preferred_fonts = ["Cascadia Code", "Consolas", "Courier New"]
    code_font = "Consolas"  # Default fallback
    
    for font in preferred_fonts:
        if is_font_available(font):
            code_font = font
            break
    
    # Enhanced template text area with modern styling and syntax highlighting support
    template_text = tk.Text(template_container, 
                          width=70, 
                          height=14,
                          wrap=tk.NONE,
                          background=bg_light,
                          foreground=text_color,
                          insertbackground=primary_color,
                          selectbackground=primary_light,
                          padx=8, 
                          pady=8,
                          borderwidth=1,
                          relief="solid",
                          font=(code_font, font_size_normal),
                          xscrollcommand=h_scrollbar.set,
                          yscrollcommand=v_scrollbar.set)
    template_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Connect scrollbars to the text widget
    h_scrollbar.config(command=template_text.xview)
    v_scrollbar.config(command=template_text.yview)
    
    # Update template based on user input with syntax highlighting
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
        
        # Clear the current template
        template_text.delete(1.0, tk.END)
        
        if script_type == ".py":
            template = f"""# NAME: {name}
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
"""
            template_text.insert(tk.END, template)
            
            # Apply syntax highlighting
            template_text.tag_configure("comment", foreground="#888888")
            template_text.tag_configure("keyword", foreground="#7986CB")
            template_text.tag_configure("function", foreground="#4CAF50")
            template_text.tag_configure("string", foreground="#FF8A65")
            
            # Apply highlighting
            for pattern, tag in [
                (r"^#.*$", "comment"),
                (r"\bimport\b|\bif\b|\belse\b|\bdef\b|\breturn\b|\bfor\b|\bin\b|\bwhile\b", "keyword"),
                (r"\bTrue\b|\bFalse\b|\bNone\b", "keyword"),
                (r"print\b|argparse\b|ArgumentParser\b|add_argument\b|action\b|parse_args\b", "function"),
                (r'".*?"', "string"),
                (r"'.*?'", "string")
            ]:
                start_idx = "1.0"
                while True:
                    import re
                    pos = template_text.search(pattern, start_idx, tk.END, regexp=True)
                    if not pos:
                        break
                    
                    # Find end of match
                    line, col = pos.split('.')
                    line_text = template_text.get(f"{line}.0", f"{line}.end")
                    match = re.search(pattern[1:] if pattern.startswith("^") else pattern, line_text[int(col):])
                    if match:
                        end_pos = f"{line}.{int(col) + match.end()}"
                        template_text.tag_add(tag, pos, end_pos)
                        start_idx = end_pos
                    else:
                        # If no match found, move to next line to avoid infinite loop
                        start_idx = f"{int(line) + 1}.0"
                        
        elif script_type == ".ps1":
            template = f"""# NAME: {name}
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
"""
            template_text.insert(tk.END, template)
            
        elif script_type in [".bat", ".cmd"]:
            template = f""":: NAME: {name}
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
"""
            template_text.insert(tk.END, template)
            
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
    
    # Action buttons card
    buttons_card = ttk.Frame(form_container, style="Card.TFrame", padding=16)
    buttons_card.pack(fill=tk.X, pady=(0, 16))
    
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
    
    # Button container for better layout
    button_container = ttk.Frame(buttons_card)
    button_container.pack(fill=tk.X)
    
    # Left side - cancel
    ttk.Button(button_container, 
              text="Cancel", 
              width=12,
              style="Secondary.TButton",
              command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    # Right side - create
    create_btn = ttk.Button(button_container, 
                          text="✨ Create Script", 
                          width=15,
                          style="Success.TButton",
                          command=create_script)
    create_btn.pack(side=tk.RIGHT, padx=5)
    
    # When dialog is about to close, cleanup event bindings
    def on_close():
        main_canvas.unbind_all("<MouseWheel>")
        dialog.destroy()
    
    dialog.protocol("WM_DELETE_WINDOW", on_close)
    
    # Set focus to the script name entry for immediate typing
    script_name_entry.focus_set()
    
    # Helper function for system font
    def _get_system_font():
        """Get the best font for the current system"""
        if sys.platform == "win32":
            return "Segoe UI"
        elif sys.platform == "darwin":
            return "San Francisco"
        else:
            return "Roboto"
    
    # Keep dialog modal
    dialog.wait_window()