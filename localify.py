import argparse
import json
from pathlib import Path
import sys
import yt_dlp
import shutil
import re
import tempfile
from mutagen.easyid3 import EasyID3

CONFIG_FILE = Path.home().joinpath("localify.config.json")

def check_dependencies():
    """Check if required system dependencies are installed."""
    
    if shutil.which("ffmpeg") is None:
        print("Error: ffmpeg is not installed or not found in your system's PATH.")
        print("Please install ffmpeg to use this tool.")
        print("Mac: brew install ffmpeg | Windows: winget install ffmpeg")
        sys.exit(1)
        
    if shutil.which("yt-dlp") is None:
        print("Error: yt-dlp is not installed or not found in your system's PATH.")
        print("Please install yt-dlp to use this tool.")
        print("See https://github.com/yt-dlp/yt-dlp#installation")
        sys.exit(1)

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
    """Use yt-dlp to download audio from the provided YouTube link and save it to the specified destination."""
    
    print(f"Starting download for: {link}")
    print(f"Saving to: {destination}")
    
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(link, download=False)
        original_title = info.get('title', 'Unknown Title')
        video_id = info.get('id')  # e.g. 'dQw4w9WgXcQ'
                
        artist, track = clean_youtube_title(original_title)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        yt_dlp_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(temp_path.joinpath(f"{video_id}.%(ext)s")), 
            'postprocessors': [
                {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'},
                {'key': 'FFmpegMetadata'},
                {'key': 'EmbedThumbnail'}
            ],
            'writethumbnail': True,
        }
        
        with yt_dlp.YoutubeDL(yt_dlp_opts) as ydl:
            ydl.download([link])
            
        temp_filepath = temp_path.joinpath(f"{video_id}.mp3")
        tag_audio_file(temp_filepath, artist, track)
        
        clean_filename = f"{artist} - {track}.mp3"
        final_filepath = destination.joinpath(clean_filename)
        
        
        try:
            # If file with that name already exists in Spotify then remove it first
            if final_filepath.exists():
                final_filepath.unlink()
                
            shutil.move(str(temp_filepath), str(final_filepath))
            print(f"Success! Saved as: {clean_filename}")
        except Exception as e:
            print(f"Warning: Could not move file. It is saved as {video_id}.mp3")
            print(f"Error details: {e}")
        
def clean_youtube_title(raw_title):
    """
    Cleans the YouTube title and attempts to split it into Artist and Track.
    """
    
    # Strip out common YouTube music video junk inside brackets or parentheses
    # Regex looks for (text) or [text] and removes them
    junk_patterns = r'[\(\[].*?(official|video|audio|lyric|live|4k|hd|visualizer).*?[\)\]]'
    clean_title = re.sub(junk_patterns, '', raw_title, flags=re.IGNORECASE)
    
    # Remove any invalid characters for file names (Windows, macOS, Linux)
    clean_title = re.sub(r'[<>:"/\\|?*]', '', clean_title)
    
    # Remove any extra whitespace left behind
    clean_title = clean_title.strip()

    if " - " in clean_title:
        parts = clean_title.split(" - ", 1) # Split only on the first hyphen
        artist = parts[0].strip()
        track = parts[1].strip()
    else:
        # TODO: Maybe get channel name if no artist is found
        artist = "Unknown Artist"
        track = clean_title

    return artist, track

def tag_audio_file(filepath, artist, track):
    """Applies the custom formatted metadata to the downloaded mp3."""
    
    try:
        # Load the MP3's ID3 tags
        audio = EasyID3(filepath)
        
        # Overwrite the title and artist
        audio['title'] = track
        audio['artist'] = artist
        
        # Save the changes
        audio.save()
        print(f"Successfully tagged: {artist} - {track}")
        
    except Exception as e:
        print(f"Warning: Could not tag file {filepath}. Error: {e}")

def main():
    check_dependencies()
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
        
        download_audio(args.link, destination)
    
    # No arguments
    elif len(sys.argv) == 1:
        parser.print_help()

if __name__ == "__main__":
    main()
