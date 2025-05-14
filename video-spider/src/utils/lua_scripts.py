"""
Lua script utilities for the video spider.
This module provides access to the Lua scripts used by Splash.
"""

import os
from pathlib import Path

# Get the directory where the Lua scripts are located
LUA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'lua_scripts')

def load_lua_script(script_name):
    """
    Load a Lua script from file.
    
    Args:
        script_name (str): The name of the Lua script file.
        
    Returns:
        str: The content of the Lua script.
    """
    script_path = os.path.join(LUA_DIR, script_name)
    with open(script_path, 'r', encoding='utf-8') as f:
        return f.read()

# Load the main script
try:
    MAIN_SCRIPT = load_lua_script('video_scraper.lua')
except Exception as e:
    print(f"Error loading Lua script: {e}")
    MAIN_SCRIPT = """
        function main(splash, args)
            -- Basic fallback script
            splash:go(args.url)
            splash:wait(3)
            return {
                html = splash:html(),
                info = {
                    url = splash:url(),
                    title = splash:evaljs("document.title"),
                    status = 200
                }
            }
        end
        return {main=main}
    """
