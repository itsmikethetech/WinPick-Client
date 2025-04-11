"""
Script Metadata Parser
Functions for parsing script metadata from files
"""

import os
import re

def get_exe_metadata(exe_path):
    """Extract metadata from an EXE file"""
    try:
        name = os.path.basename(exe_path)
        description = "Executable file"
        
        try:
            import win32api
            try:
                info = win32api.GetFileVersionInfo(exe_path, '\\')
                ms = info['FileVersionMS']
                ls = info['FileVersionLS']
                version = f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
                lang, codepage = win32api.GetFileVersionInfo(exe_path, '\\VarFileInfo\\Translation')[0]
                str_info_path = f'\\StringFileInfo\\{lang:04x}{codepage:04x}\\FileDescription'
                description_info = win32api.GetFileVersionInfo(exe_path, str_info_path)
                if description_info:
                    description = description_info
                str_info_path = f'\\StringFileInfo\\{lang:04x}{codepage:04x}\\ProductName'
                name_info = win32api.GetFileVersionInfo(exe_path, str_info_path)
                if name_info:
                    name = name_info
            except:
                pass
        except ImportError:
            name = os.path.splitext(os.path.basename(exe_path))[0]
            description = "Windows Executable"
        
        return name, description, "No", "", "", ""
        
    except Exception as e:
        return os.path.basename(exe_path), f"Error reading metadata: {str(e)}", "No", "", "", ""

def parse_script_metadata(script_path):
    """
    Parse script metadata from file comments.
    Expected format for Python/PowerShell:
      # NAME: Friendly Script Name
      # DEVELOPER: Developer Name
      # DESCRIPTION: This script does something useful
      # UNDOABLE: Yes/No
      # UNDO_DESC: Description of what undo will do
      # LINK: https://example.com/developer-profile
      
    And similarly for batch files using "::" prefixes.
    """
    default_name = os.path.basename(script_path)
    default_description = ""
    default_undoable = "No"
    default_undo_desc = ""
    default_developer = ""
    default_link = ""
    
    try:
        _, ext = os.path.splitext(script_path)
        ext = ext.lower()
        
        if ext == '.exe':
            return get_exe_metadata(script_path)
        
        with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(2000)
        
        if ext in ['.bat', '.cmd']:
            name_pattern = r'(?i)::[ \t]*NAME:[ \t]*(.*?)[\r\n]'
            desc_pattern = r'(?i)::[ \t]*DESCRIPTION:[ \t]*(.*?)[\r\n]'
            undoable_pattern = r'(?i)::[ \t]*UNDOABLE:[ \t]*(.*?)[\r\n]'
            undo_desc_pattern = r'(?i)::[ \t]*UNDO_DESC:[ \t]*(.*?)[\r\n]'
            developer_pattern = r'(?i)::[ \t]*DEVELOPER:[ \t]*(.*?)[\r\n]'
            link_pattern = r'(?i)::[ \t]*LINK:[ \t]*(.*?)[\r\n]'
        else:
            name_pattern = r'(?i)#[ \t]*NAME:[ \t]*(.*?)[\r\n]'
            desc_pattern = r'(?i)#[ \t]*DESCRIPTION:[ \t]*(.*?)[\r\n]'
            undoable_pattern = r'(?i)#[ \t]*UNDOABLE:[ \t]*(.*?)[\r\n]'
            undo_desc_pattern = r'(?i)#[ \t]*UNDO_DESC:[ \t]*(.*?)[\r\n]'
            developer_pattern = r'(?i)#[ \t]*DEVELOPER:[ \t]*(.*?)[\r\n]'
            link_pattern = r'(?i)#[ \t]*LINK:[ \t]*(.*?)[\r\n]'
        
        name_match = re.search(name_pattern, content)
        friendly_name = name_match.group(1).strip() if name_match else default_name
        
        desc_match = re.search(desc_pattern, content)
        description = desc_match.group(1).strip() if desc_match else default_description
        
        undoable_match = re.search(undoable_pattern, content)
        if undoable_match:
            undoable_value = undoable_match.group(1).strip().lower()
            undoable = "Yes" if undoable_value in ['yes', 'true', '1'] else "No"
        else:
            undoable = default_undoable
        
        undo_desc_match = re.search(undo_desc_pattern, content)
        undo_desc = undo_desc_match.group(1).strip() if undo_desc_match else default_undo_desc
        
        developer_match = re.search(developer_pattern, content)
        developer = developer_match.group(1).strip() if developer_match else default_developer
        
        link_match = re.search(link_pattern, content)
        link = link_match.group(1).strip() if link_match else default_link
        
        return friendly_name, description, undoable, undo_desc, developer, link
    except Exception as e:
        print(f"Error parsing metadata for {script_path}: {str(e)}")
        return default_name, f"Error reading metadata: {str(e)}", default_undoable, default_undo_desc, default_developer, default_link