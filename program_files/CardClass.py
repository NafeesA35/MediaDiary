import tkinter as tk
from tkinter import ttk
import requests
import io
from PIL import Image, ImageTk

def truncate_text(text, max_length=80):
    """Truncate text to max_length characters and add ellipsis if needed."""
    if text is None:
        return "N/A"
    text = str(text)
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

class Card:
    def __init__(self, parent, title, score, genres, personal_score, personal_comment, image_url):
        self.parent = parent
        self.title = title
        self.score = score
        self.genres = genres
        self.personal_score = personal_score
        self.personal_comment = personal_comment
        self.image_url = image_url
        self.card_frame = None
        self.img_label = None
        self.tk_image = None  # Keep reference to prevent garbage collection
        
    def create_card(self):

        # Create a frame for the card with padding and a specific style
        self.card_frame = ttk.Frame(self.parent, padding=10, style='Card.TFrame', width=900, height=180)
        self.card_frame.pack(pady=5)  # Fixed size card with padding
        self.card_frame.pack_propagate(False)  # Prevent frame from shrinking to fit contents

        # Placeholder for image
        self.img_label = ttk.Label(self.card_frame, anchor='center')
        self.img_label.pack(side=tk.LEFT, padx=10)  # Position on left side with padding

        if self.image_url:
            try:
                # Fetch image from URL
                response = requests.get(self.image_url, stream=True, timeout=10)
                response.raise_for_status()  # Raise an exception for HTTP errors
                
                # Open image using Pillow
                pil_image = Image.open(io.BytesIO(response.content))
                
                # Resize image (e.g., to a fixed height, maintaining aspect ratio)
                target_height = 150 
                aspect_ratio = pil_image.width / pil_image.height
                target_width = int(target_height * aspect_ratio)
                pil_image = pil_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                # Convert to Tkinter PhotoImage
                self.tk_image = ImageTk.PhotoImage(pil_image)
                
                self.img_label.configure(image=self.tk_image)
                # Keep a reference to prevent garbage collection
                self.img_label.image = self.tk_image
            except requests.exceptions.RequestException as e:
                # Network-related errors
                print(f"Network error loading image for {self.title}: {e}")
                self.img_label.configure(text="Network\nError", background="#ffcccc", width=20)
            except Exception as e:
                # If image loading fails, show placeholder text
                print(f"Error loading image for {self.title}: {e}")
                self.img_label.configure(text="Image\nNot Available", background="#ccc", width=20)
        else:
            # No image URL provided, show placeholder
            self.img_label.configure(text="No Image", background="#ccc", width=20)

        # Info frame contains all text information (positioned to right of image)
        info_frame = ttk.Frame(self.card_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Join the list of genres into a string for display and truncate long text
        genre_text = ', '.join(self.genres) if isinstance(self.genres, list) else self.genres
        truncated_title = truncate_text(self.title, 65)
        truncated_genres = truncate_text(genre_text, 65)
        truncated_comment = truncate_text(self.personal_comment, 65)

        # Add all information labels with controlled text lengths to fit in fixed height
        title_label = ttk.Label(info_frame, text=f"Title: {truncated_title}", style='CardTitle.TLabel')
        title_label.pack(anchor='w', pady=(0, 1))
        
        score_label = ttk.Label(info_frame, text=f"Score: {self.score}")
        score_label.pack(anchor='w', pady=(0, 1))
        
        genres_label = ttk.Label(info_frame, text=f"Genres: {truncated_genres}")
        genres_label.pack(anchor='w', pady=(0, 1))
        
        personal_score_label = ttk.Label(info_frame, text=f"Your Score: {self.personal_score}")
        personal_score_label.pack(anchor='w', pady=(0, 1))
        
        comment_label = ttk.Label(info_frame, text=f"Comment: {truncated_comment}")
        comment_label.pack(anchor='w', pady=(0, 1))
        # Note: anchor='w' aligns text to the west (left)
        
        return self.card_frame
    
    def destroy(self):
        # Destroy the card widget
        if self.card_frame:
            self.card_frame.destroy()


class MusicCard:

    def __init__(self, parent, name, artist, genres, image_url, personal_score, playcount):
        self.parent = parent
        self.name = name
        self.artist = artist
        self.genres = genres
        self.image_url = image_url
        self.personal_score = personal_score
        self.playcount = playcount
        self.card_frame = None
        self.img_label = None
        self.tk_image = None

    def create_card(self):
        # Create a frame for the card with padding and a specific style
        self.card_frame = ttk.Frame(self.parent, padding=10, style='Card.TFrame', width=900, height=180)
        self.card_frame.pack(pady=5)  # Fixed size card with padding
        self.card_frame.pack_propagate(False)  # Prevent frame from shrinking to fit contents

        # Placeholder for image
        self.img_label = ttk.Label(self.card_frame, anchor='center')
        self.img_label.pack(side=tk.LEFT, padx=10)

        if self.image_url:
            try:
                # Fetch image from URL
                response = requests.get(self.image_url, stream=True, timeout=10)
                response.raise_for_status()  # Raise an exception for HTTP errors
                
                # Open image using Pillow
                pil_image = Image.open(io.BytesIO(response.content))
                
                # Resize image (e.g., to a fixed height, maintaining aspect ratio)
                target_height = 150 
                aspect_ratio = pil_image.width / pil_image.height
                target_width = int(target_height * aspect_ratio)
                pil_image = pil_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                
                # Convert to Tkinter PhotoImage
                self.tk_image = ImageTk.PhotoImage(pil_image)
                
                self.img_label.configure(image=self.tk_image)
                # Keep a reference to prevent garbage collection
                self.img_label.image = self.tk_image
            except requests.exceptions.RequestException as e:
                print(f"Network error loading image for {self.name}: {e}")
                self.img_label.configure(text="Network\nError", background="#ffcccc", width=20)
            except Exception as e:
                print(f"Error loading image for {self.name}: {e}")
                self.img_label.configure(text="Image\nNot Available", background="#ccc", width=20)
        else:
            # No image URL provided, show placeholder
            self.img_label.configure(text="No Image", background="#ccc", width=20)
        # Info frame contains all text information (positioned to right of image)
        info_frame = ttk.Frame(self.card_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        # Join the list of genres into a string for display and truncate long text
        genre_text = ', '.join(self.genres) if isinstance(self.genres, list) else self.genres
        truncated_name = truncate_text(self.name, 65)
        truncated_artist = truncate_text(self.artist, 65)
        truncated_genres = truncate_text(genre_text, 65)
        
        # Add all information labels with controlled text lengths to fit in fixed height
        name_label = ttk.Label(info_frame, text=f"Name: {truncated_name}", style='CardTitle.TLabel')
        name_label.pack(anchor='w', pady=(0, 1))
        
        artist_label = ttk.Label(info_frame, text=f"Artist: {truncated_artist}")
        artist_label.pack(anchor='w', pady=(0, 1))
        
        genres_label = ttk.Label(info_frame, text=f"Genres: {truncated_genres}")
        genres_label.pack(anchor='w', pady=(0, 1))
        
        personal_score_label = ttk.Label(info_frame, text=f"Your Score: {self.personal_score}")
        personal_score_label.pack(anchor='w', pady=(0, 1))
        
        playcount_label = ttk.Label(info_frame, text=f"Playcount: {self.playcount}")
        playcount_label.pack(anchor='w', pady=(0, 1))
        # Note: anchor='w' aligns text to the west (left)
        return self.card_frame
    def destroy(self):
        # Destroy the card widget
        if self.card_frame:
            self.card_frame.destroy()


class MovieCard:
    def __init__(self, parent, title, score, genres, personal_score, release_date, image_url):
        self.parent = parent
        self.title = title
        self.score = score
        self.genres = genres
        self.personal_score = personal_score
        self.release_date = release_date
        self.image_url = image_url
        self.card_frame = None
        self.img_label = None
        self.tk_image = None

    def create_card(self):
        self.card_frame = ttk.Frame(self.parent, padding=10, style='Card.TFrame', width=900, height=180)
        self.card_frame.pack(pady=5) 
        self.card_frame.pack_propagate(False)  # Prevent frame from shrinking to fit contents

        self.img_label = ttk.Label(self.card_frame, anchor='center')
        self.img_label.pack(side=tk.LEFT, padx=10)

        if self.image_url:
            try:
                response = requests.get(self.image_url, stream=True, timeout=10)
                response.raise_for_status()
                pil_image = Image.open(io.BytesIO(response.content))
                target_height = 150
                aspect_ratio = pil_image.width / pil_image.height
                target_width = int(target_height * aspect_ratio)
                pil_image = pil_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
                self.tk_image = ImageTk.PhotoImage(pil_image)
                self.img_label.configure(image=self.tk_image)
                self.img_label.image = self.tk_image
            except requests.exceptions.RequestException as e:
                print(f"Network error loading image for {self.title}: {e}")
                self.img_label.configure(text="Network\nError", background="#ffcccc", width=20)
            except Exception as e:
                print(f"Error loading image for {self.title}: {e}")
                self.img_label.configure(text="Image\nNot Available", background="#ccc", width=20)
        else:
            self.img_label.configure(text="No Image", background="#ccc", width=20)

        info_frame = ttk.Frame(self.card_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        genre_text = ', '.join(self.genres) if isinstance(self.genres, list) else self.genres
        
        # Truncate text to ensure all metadata fits within the fixed card height
        truncated_title = truncate_text(self.title, 65)
        truncated_genres = truncate_text(genre_text, 65)
        
        title_label = ttk.Label(info_frame, text=f"Title: {truncated_title}", style='CardTitle.TLabel')
        title_label.pack(anchor='w', pady=(0, 1))
        
        release_date_label = ttk.Label(info_frame, text=f"Release Date: {self.release_date}")
        release_date_label.pack(anchor='w', pady=(0, 1))
        
        score_label = ttk.Label(info_frame, text=f"Score: {self.score}")
        score_label.pack(anchor='w', pady=(0, 1))
        
        genres_label = ttk.Label(info_frame, text=f"Genres: {truncated_genres}")
        genres_label.pack(anchor='w', pady=(0, 1))
        
        personal_score_label = ttk.Label(info_frame, text=f"Your Score: {self.personal_score}")
        personal_score_label.pack(anchor='w', pady=(0, 1))
        
        return self.card_frame

    def destroy(self):
        if self.card_frame:
            self.card_frame.destroy()

class TVCard(MovieCard): # Inherits from MovieCard as they are identical
    pass

