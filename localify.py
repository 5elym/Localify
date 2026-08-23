import argparse
import json
from pathlib import Path
import sys

CONFIG_FILE = Path.home().joinpath("localify.config.json")

def load_config():
    """Loads the default path from the config file if it exists."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"default_path": None}

def save_config(path_str):
    """Saves the default path to the config file."""
    absolute_path = str(Path(path_str).resolve())
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"default_path": absolute_path}, f)
    print(f"Default path set to: {absolute_path}")

def download_audio(link, destination):
    """Placeholder for your yt-dlp logic."""
    print(f"Starting download for: {link}")
    print(f"Saving to: {destination}")
    # TODO: Implement yt-dlp download logic here

def main():
    config = load_config()
    
    parser = argparse.ArgumentParser(
        description="Download YouTube audio with metadata for Spotify Local Files."
    )
    
    # Positional argument for the YouTube link
    parser.add_argument("link", nargs="?", help="The YouTube URL to download")
    
    # Optional flags
    parser.add_argument("-s", "--specify", help="Specify a custom folder path for this download")
    parser.add_argument("-d", "--default", help="Set the default download folder path")
    parser.add_argument("-f", "--folder", action="store_true", help="Print the current default folder path")

    args = parser.parse_args()

    # Handle the commands
    if args.default:
        save_config(args.default)
        sys.exit(0)

    if args.folder:
        current_default = config.get("default_path")
        if current_default:
            print(f"Current default folder: {current_default}")
        else:
            print("No default folder set. Use python localify -d to set one.")
        sys.exit(0)

    if args.link:
        # Determine the save destination
        if args.specify:
            destination = Path(args.specify).resolve()
        elif config.get("default_path"):
            destination = Path(config.get("default_path"))
        else:
            print("Error: No default path set and no custom path provided.")
            print("Set a default path using: python localify -d [FILEPATH]")
            sys.exit(1)
            
        # Ensure the destination folder exists
        destination.mkdir(parents=True, exist_ok=True)
        
        # Trigger the download
        download_audio(args.link, destination)
    
    # If the user ran the script with no arguments at all
    elif len(sys.argv) == 1:
        parser.print_help()

if __name__ == "__main__":
    main()
