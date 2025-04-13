# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Run Commands
- Run app: `python main.py`
- Install dependencies: `pip install -r requirements.txt`
- Package app: `python setup.py install`
- Clear cache: `python clearcache.py`

## Code Style Guidelines
- **Imports**: stdlib first, third-party second, local modules last
- **Formatting**: 4-space indentation, docstrings in triple quotes
- **Naming**: snake_case for functions/variables, CamelCase for classes
- **Structure**: Follow MVC pattern (controllers/, ui/, utils/)
- **Error Handling**: Use specific try/except blocks with clear error messages
- **UI Components**: Extend tkinter widgets with consistent styling
- **Logging**: Use MessageHandler class for user-facing messages

## Architecture Notes
- Tkinter-based GUI application for Windows script management
- Main entry point: ScriptExplorer class in src/ui/app.py
- Controllers handle business logic and data management