import tkinter as tk          
from tkinter import ttk       
import json                   
import os                    
import requests 
import io 
from PIL import Image, ImageTk # Required for Pillow image processing
from CardClass import Card  
from CardClass import MusicCard
from CardClass import MovieCard
from CardClass import TVCard
from entry_manager import EntryManager


FONT = "Sigmar"
SIZE = 10
TITLE_SIZE = 18
HEADER_SIZE = 20
SECONDARY_SIZE = 15
GUI_WIDTH = 1000
GUI_HEIGHT = 600

# Load anime data from the JSON file, if path doesnt exist return None
def load_json_data(file_path):

    if not os.path.exists(file_path):
        return None  # Return None if file doesn't exist

    with open(file_path, 'r') as file:
        return json.load(file)  # Parse JSON and return as Python dictionary
    

def get_create_card(data, path, parent_frame):
    cards = []
    if path == "anime":
        for i in range(len(data['names'])):
            card = Card(
                parent=parent_frame,
                title=data['names'][i],
                score=data['scores'][i],
                genres=data['genres'][i],
                personal_score=data['personal_scores'][i],
                personal_comment=data['personal_comments'][i],
                image_url=data.get('image_url', [None])[i]
            )
            card.create_card()
            cards.append(card)
    elif path == "manga":
        for i in range(len(data['names'])):
            card = Card(
                parent=parent_frame,
                title=data['names'][i],
                score=data['scores'][i],
                genres=data['genres'][i],
                personal_score=data['personal_scores'][i],
                personal_comment=data['personal_comments'][i],
                image_url=data.get('image_url', [None])[i]
            )
            card.create_card()
            cards.append(card)
    elif path == "music":
        for i in range(len(data['name'])):
            card = MusicCard(
                parent=parent_frame,
                name=data['name'][i],
                artist=data['artist'][i],
                genres=data['genres'][i],
                personal_score=data['personal_score'][i],
                image_url=data.get('image_url', [None])[i],
                playcount=data['playcount'][i]
            )
            card.create_card()
            cards.append(card)
    elif path == "movie":
        for i in range(len(data['title'])):
            card = MovieCard(
                parent=parent_frame,
                title=data['title'][i],
                score=data['score'][i],
                genres=data['genres'][i],
                personal_score=data['personal_score'][i],
                release_date=data['release_date'][i],
                image_url=data.get('image_url', [None])[i]
            )
            card.create_card()
            cards.append(card)
    elif path == "tv":
        for i in range(len(data['title'])):
            card = TVCard(
                parent=parent_frame,
                title=data['title'][i],
                score=data['score'][i],
                genres=data['genres'][i],
                personal_score=data['personal_score'][i],
                release_date=data['release_date'][i],
                image_url=data.get('image_url', [None])[i]
            )
            card.create_card()
            cards.append(card)
    return cards

# Function to show the cards screen
def show_cards_screen(root, data_sources, view_type):

    # Remove all existing widgets from root
    for widget in root.winfo_children():
        widget.destroy()
    
    # Create main container frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)  # Fill all available space
    
    # Add back button at the top of the scree
    # The lambda function allows us to pass parameters to the callback function
    back_button = ttk.Button(
        main_frame, 
        text="Back to Menu", 
        command=lambda: show_menu_screen(root, data_sources)
    )
    back_button.pack(pady=10)
    
    # Scrollable canvas setup - this allows scrolling if content is larger than window
    canvas = tk.Canvas(main_frame, borderwidth=0, background="#f0f0f0")
    frame = ttk.Frame(canvas)  # This frame will hold all the cards
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)  # Connect scrollbar to canvas

    # Position scrollbar and canvas
    scrollbar.pack(side="right", fill="y")  # Right side, fill vertically
    canvas.pack(side="left", fill="both", expand=True)  # Left side, fill all space
    canvas.create_window((0, 0), window=frame, anchor="nw")  # Place frame inside canvas

    # Function to update the scroll region when the frame size changes
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))  # Set scroll region to all content

    frame.bind("<Configure>", on_frame_configure)  # Bind the function to resize events
    
    # Create cards for each item in the data, passing the correct parent frame
    if view_type == 'media':
        # For 'media', we combine movie and tv data
        movies_data = data_sources.get('movie')
        tv_data = data_sources.get('tv')
        
        all_cards = []
        if movies_data:
            all_cards.extend(get_create_card(movies_data, 'movie', frame))
        if tv_data:
            all_cards.extend(get_create_card(tv_data, 'tv', frame))
        
        frame.cards = all_cards
        if not all_cards:
            ttk.Label(frame, text="No data available for movies or TV shows.").pack()

    else:
        data_to_show = data_sources.get(view_type)
        if data_to_show:
            frame.cards = get_create_card(data_to_show, view_type, frame)
        else:
            ttk.Label(frame, text=f"No data available for {view_type}.").pack()


def show_menu_screen(root, data_sources):
    """
    Displays the main menu screen with options.
    """
    # Clear current content - remove all existing widgets
    for widget in root.winfo_children():
        widget.destroy()
    
    # Create menu frame with padding
    menu_frame = ttk.Frame(root, padding=50)
    menu_frame.pack(fill='both', anchor='n')  # Anchor to top instead of centering
    
    # Add title at the top of menu using pack
    title_label = ttk.Label(menu_frame, text="Tracker", style='Title.TLabel', font=(FONT, TITLE_SIZE))
    title_label.pack(pady=(0, 30))  # Add padding below the title
    
    # Create a frame for the main buttons to center them
    button_frame = ttk.Frame(root)
    button_frame.pack()

    # --- Load and resize images for buttons ---
    try:
        # Store image references on the frame itself to prevent garbage collection
        button_frame.image_refs = []

        # Define button configurations
        button_configs = [
            {"text": "Anime", "image_path": "../assets/anime.png", "view_type": "anime"},
            {"text": "Manga", "image_path": "../assets/manga.png", "view_type": "manga"},
            {"text": "Music", "image_path": "../assets/music.png", "view_type": "music"},
            {"text": "Media", "image_path": "../assets/movies.png", "view_type": "media"}
        ]

        for config in button_configs:
            img = Image.open(config["image_path"]).resize((200, 250), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            button_frame.image_refs.append(photo)  # Keep a reference

            ttk.Button(
                button_frame,
                text=config["text"],
                image=photo,
                compound=tk.TOP,
                command=lambda vt=config["view_type"]: show_cards_screen(root, data_sources, vt)
            ).pack(side=tk.LEFT, padx=10, pady=10)

    except FileNotFoundError as e:
        print(f"Error loading button images: {e}. Falling back to text buttons.")
        # Fallback to text-only buttons if images are missing
        ttk.Button(button_frame, text="Anime", command=lambda: show_cards_screen(root, data_sources, "anime")).pack(pady=10)
        ttk.Button(button_frame, text="Manga", command=lambda: show_cards_screen(root, data_sources, "manga")).pack(pady=10)
        ttk.Button(button_frame, text="Music", command=lambda: show_cards_screen(root, data_sources, "music")).pack(pady=10)
        ttk.Button(button_frame, text="Media", command=lambda: show_cards_screen(root, data_sources, "media")).pack(pady=10)

    # Add the "Add" button below the main buttons
    add_button = ttk.Button(
        root,
        text="Add New Entry",
        command=lambda: show_entry_screen(root, data_sources)
    )
    add_button.pack(pady=20)


def show_entry_screen(root, data_sources):
    """
    Render the add-entry flow; movies and TV share the same media bucket here.
    """
    # Create entry manager instance
    entry_manager = EntryManager(root, FONT, SECONDARY_SIZE)
    
    # Set up back callback to return to menu and refresh data
    def back_to_menu():
        # Reload data sources to reflect any new additions
        updated_data_sources = {
            "anime": load_json_data("../statistics/anime_stats.txt"),
            "manga": load_json_data("../statistics/manga_stats.txt"),
            "music": load_json_data("../statistics/music_stats.txt"),
            "movie": load_json_data("../statistics/movie_stats.txt"),
            "tv": load_json_data("../statistics/tv_stats.txt")
        }
        show_menu_screen(root, updated_data_sources)
    
    entry_manager.set_back_callback(back_to_menu)
    
    # Show the main entry screen
    entry_manager.show_main_screen()


# Main GUI function
def show_gui():

    # Create the main window
    root = tk.Tk()
    root.title("Anime Tracker")
    root.geometry(f"{GUI_WIDTH}x{GUI_HEIGHT}")  # Window size

    # Style Configuration
    style = ttk.Style()

    # General widget styles
    style.configure("TLabel", font=(FONT, SIZE))
    style.configure("TButton", font=(FONT, SIZE))
    style.configure("TRadiobutton", font=(FONT, SECONDARY_SIZE))
    
    # Custom styles for the application
    style.configure("Title.TLabel", font=(FONT, TITLE_SIZE))
    style.configure("Card.TFrame", background="white", relief="raised", borderwidth=1)
    style.configure("CardTitle.TLabel", font=(FONT, 14, "bold"))
    
    # Load all data sources into a single dictionary
    data_sources = {
        "anime": load_json_data("../statistics/anime_stats.txt"),
        "manga": load_json_data("../statistics/manga_stats.txt"),
        "music": load_json_data("../statistics/music_stats.txt"),
        "movie": load_json_data("../statistics/movie_stats.txt"),
        "tv": load_json_data("../statistics/tv_stats.txt")
    }
    
    # Start with the menu screen
    show_menu_screen(root, data_sources)
    
    # Start the Tkinter event loop
    root.mainloop()  


if __name__ == "__main__":
    show_gui()