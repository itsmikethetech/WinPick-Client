#!/usr/bin/env python3
"""
WinPick Setup Script
"""

from setuptools import setup, find_packages

setup(
    name="winpick",
    version="0.1.0",
    description="Windows script management and automation tool",
    author="WinPick Team",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        # Add dependencies here
        # e.g., "pywin32>=228",
    ],
    entry_points={
        "console_scripts": [
            "winpick=main:main",
        ],
    },
)
