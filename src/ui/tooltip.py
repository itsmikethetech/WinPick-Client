"""
ToolTip class
Displays tooltips for widgets
"""

import tkinter as tk
from tkinter import ttk

class ToolTip:
    """Class to create tooltips for widgets with enhanced appearance"""
    def __init__(self, widget, delay=500, wrap_length=300):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.delay = delay  # Milliseconds to wait before showing tooltip
        self.wrap_length = wrap_length
        self.schedule_id = None
        
        # Try to get colors from parent app if available
        try:
            parent = self._find_parent_app(widget)
            if hasattr(parent, 'bg_dark') and hasattr(parent, 'bg_light'):
                self.bg_color = parent.bg_dark
                self.fg_color = parent.bg_light
            else:
                self.bg_color = "#2d2d2d"
                self.fg_color = "#ffffff"
        except:
            # Default colors if parent not found
            self.bg_color = "#2d2d2d"
            self.fg_color = "#ffffff"

    def _find_parent_app(self, widget):
        """Try to find the main application widget to get its colors"""
        parent = widget
        while parent:
            if hasattr(parent, "bg_dark") and hasattr(parent, "bg_light"):
                return parent
            if hasattr(parent, "master") and parent.master:
                parent = parent.master
            else:
                break
        return None

    def showtip(self, text):
        """Display text in tooltip window with delayed appearance"""
        self.text = text
        if self.tipwindow or not self.text:
            return
            
        # Cancel any existing scheduled tooltip
        if self.schedule_id:
            self.widget.after_cancel(self.schedule_id)
            
        # Schedule the tooltip to appear after delay
        self.schedule_id = self.widget.after(self.delay, self._show_tip)
    
    def _show_tip(self):
        """Actually show the tooltip after delay"""
        # For Treeview and other widgets, use the mouse position
        x, y = self.widget.winfo_pointerxy()
        x += 25
        y += 25
        
        # Create a new toplevel window
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)  # Remove window decorations
        tw.wm_geometry(f"+{x}+{y}")
        
        # Add some modern styling to the tooltip
        frame = ttk.Frame(tw, padding=5)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Create tooltip content with wrapped text
        label = ttk.Label(frame, 
                         text=self.text, 
                         justify=tk.LEFT,
                         wraplength=self.wrap_length,
                         background=self.bg_color, 
                         foreground=self.fg_color,
                         font=("Segoe UI", 9))
        label.pack(fill=tk.BOTH, expand=True)
        
        # Add a subtle border around the tooltip
        tw.configure(background="#555555")
        
        # Add fade-in effect
        tw.attributes("-alpha", 0.0)
        self._fade_in(tw)
        
        # Auto-hide tooltip when mouse moves away from the widget
        self.widget.bind("<Leave>", self.hidetip)
        self.widget.bind("<Motion>", self._check_if_left)

    def _fade_in(self, window, alpha=0.0):
        """Create fade-in animation for tooltip"""
        if alpha < 1.0:
            alpha += 0.1
            window.attributes("-alpha", alpha)
            window.after(20, lambda: self._fade_in(window, alpha))

    def _check_if_left(self, event):
        """Check if mouse has moved away from the widget's area"""
        if not self.tipwindow:
            return
            
        x, y = self.widget.winfo_pointerxy()
        widget_x = self.widget.winfo_rootx()
        widget_y = self.widget.winfo_rooty()
        widget_width = self.widget.winfo_width()
        widget_height = self.widget.winfo_height()
        
        # If mouse is outside widget bounds, hide tooltip
        if (x < widget_x or x > widget_x + widget_width or 
            y < widget_y or y > widget_y + widget_height):
            self.hidetip()

    def hidetip(self, event=None):
        """Hide the tooltip with fade-out effect"""
        # Cancel scheduled tooltip if any
        if self.schedule_id:
            self.widget.after_cancel(self.schedule_id)
            self.schedule_id = None
            
        # If tooltip is visible, fade it out
        if self.tipwindow:
            tw = self.tipwindow
            self.tipwindow = None
            self._fade_out(tw)

    def _fade_out(self, window, alpha=1.0):
        """Create fade-out animation for tooltip"""
        if alpha > 0.1:
            alpha -= 0.1
            window.attributes("-alpha", alpha)
            window.after(20, lambda: self._fade_out(window, alpha))
        else:
            window.destroy()