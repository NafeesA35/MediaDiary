"""
Entry Manager Module
Handles all entry-related functionality for adding new media items.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
import copy
import api_keys

# Configuration for different media types
CONFIG = {
    "music": {
        "file_path": "../statistics/music_stats.txt",
        "data_structure": {
            "name": [], "artist": [], "genres": [], "image_url": [],
            "personal_score": [], "playcount": []
        },
        "id_fields": ["artist", "name"]
    },
    "anime": {
        "file_path": "../statistics/anime_stats.txt",
        "data_structure": {
            "names": [], "scores": [], "genres": [], "personal_scores": [],
            "personal_comments": [], "image_url": []
        },
        "id_fields": ["names"]
    },
    "manga": {
        "file_path": "../statistics/manga_stats.txt",
        "data_structure": {
            "names": [], "scores": [], "genres": [], "personal_scores": [],
            "personal_comments": [], "image_url": []
        },
        "id_fields": ["names"]
    },
    "movie": {
        "file_path": "../statistics/movie_stats.txt",
        "data_structure": {
            "title": [], "personal_score": [], "score": [], "genres": [],
            "release_date": [], "image_url": []
        },
        "id_fields": ["title", "release_date"]
    },
    "tv": {
        "file_path": "../statistics/tv_stats.txt",
        "data_structure": {
            "title": [], "personal_score": [], "score": [], "genres": [],
            "release_date": [], "image_url": []
        },
        "id_fields": ["title", "release_date"]
    }
}

class EntryManager:
    def __init__(self, root, font="Sigmar", size=15):
        self.root = root
        self.font = font
        self.size = size
        
        # State variables
        self.search_results = []
        self.selected_item = None
        self.current_media_type = ""
        self.current_personal_score = ""
        self.back_callback = None
        
        # UI elements
        self.selected_et = None
        self.name_inp = None
        self.score_inp = None
        self.results_listbox = None

    def set_back_callback(self, callback):
        """Set the callback function for the back button"""
        self.back_callback = callback

    # Data handling functions
    def load_json_data(self, file_path, default_structure):
        """Return persisted stats or a fresh copy of the configured structure."""
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            return copy.deepcopy(default_structure)

        try:
            with open(file_path, 'r') as file:
                return json.load(file)
        except (json.JSONDecodeError, FileNotFoundError):
            # Fall back to a clean template if the file is corrupt or missing mid-read.
            return copy.deepcopy(default_structure)

    def store_json_data(self, data, file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Data successfully stored in {file_path}")

    # API search functions
    def search_anime(self, query):
        url = "https://api.jikan.moe/v4/anime"
        params = {'q': query, 'limit': 10}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('data', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching anime data: {e}")
            return []

    def search_manga(self, query):
        url = "https://api.jikan.moe/v4/manga"
        params = {'q': query, 'limit': 10}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('data', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching manga data: {e}")
            return []

    def search_music(self, query):
        params = {
            'method': 'album.search', 'album': query, 'api_key': api_keys.MUSIC_API,
            'format': 'json', 'limit': 10
        }
        try:
            response = requests.get('http://ws.audioscrobbler.com/2.0/', params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('results', {}).get('albummatches', {}).get('album', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching music data: {e}")
            return []

    def search_media(self, query, media_type):
        headers = {"Authorization": api_keys.MOVIE_API}
        url = f"https://api.themoviedb.org/3/search/{media_type}"
        params = {'query': query, 'language': 'en-US', 'page': 1}
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get('results', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {media_type} data: {e}")
            return []

    # API detail functions
    def get_anime_details(self, anime_id):
        url = f"https://api.jikan.moe/v4/anime/{anime_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get('data')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching anime details: {e}")
            return None

    def get_manga_details(self, manga_id):
        url = f"https://api.jikan.moe/v4/manga/{manga_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data.get('data')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching manga details: {e}")
            return None

    def get_music_details(self, artist, album):
        params = {
            'method': 'album.getinfo', 'artist': artist, 'album': album,
            'api_key': api_keys.MUSIC_API, 'format': 'json'
        }
        try:
            response = requests.get('http://ws.audioscrobbler.com/2.0/', params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('album')
        except requests.exceptions.RequestException as e:
            print(f"Error fetching music details: {e}")
            return None

    def get_media_details(self, media_id, media_type):
        headers = {"Authorization": api_keys.MOVIE_API}
        url = f"https://api.themoviedb.org/3/{media_type}/{media_id}"
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {media_type} details: {e}")
            return None

    # UI event handlers
    def on_item_selected(self):
        selection = self.results_listbox.curselection()
        if selection:
            self.selected_item = self.search_results[selection[0]]
            self.process_selected_item()

    def process_selected_item(self):
        # Resolve detailed payloads before we persist anything.
        details = None
        if self.current_media_type == 'anime':
            details = self.get_anime_details(self.selected_item['mal_id'])
        elif self.current_media_type == 'manga':
            details = self.get_manga_details(self.selected_item['mal_id'])
        elif self.current_media_type == 'music':
            details = self.get_music_details(self.selected_item['artist'], self.selected_item['name'])
        elif self.current_media_type == 'movie':
            details = self.get_media_details(self.selected_item['id'], 'movie')
        elif self.current_media_type == 'tv':
            details = self.get_media_details(self.selected_item['id'], 'tv')
        
        if not details:
            messagebox.showerror("Error", "Could not retrieve details for the selected item")
            return
        
        # Load existing data and append new data
        conf = CONFIG[self.current_media_type]
        data = self.load_json_data(conf['file_path'], conf['data_structure'])
        
        if self.current_media_type == 'anime':
            data['names'].append(details.get('title', 'N/A'))
            data['scores'].append(details.get('score', 'N/A'))
            data['genres'].append([g['name'] for g in details.get('genres', [])])
            data['personal_scores'].append(self.current_personal_score)
            data['personal_comments'].append(details.get('year' , 'N/A'))
            data['image_url'].append(details.get('images', {}).get('jpg', {}).get('image_url', ''))
        
        elif self.current_media_type == 'manga':
            data['names'].append(details.get('title', 'N/A'))
            data['scores'].append(details.get('score', 'N/A'))
            data['genres'].append([g['name'] for g in details.get('genres', [])])
            data['personal_scores'].append(self.current_personal_score)
            data['personal_comments'].append(details['published'].get('from' , 'N/A')[:4])
            data['image_url'].append(details.get('images', {}).get('jpg', {}).get('image_url', ''))
        
        elif self.current_media_type == 'music':
            data['name'].append(details.get('name', 'N/A'))
            data['artist'].append(details.get('artist', 'N/A'))
            data['genres'].append([t['name'] for t in details.get('tags', {}).get('tag', [])])
            image = next((img['#text'] for img in reversed(details.get('image', [])) if img.get('#text')), '')
            data['image_url'].append(image)
            data['personal_score'].append(self.current_personal_score)
            data['playcount'].append(details.get('playcount', '0'))
        
        elif self.current_media_type == 'movie':
            data['title'].append(details.get('title', 'N/A'))
            data['personal_score'].append(self.current_personal_score)
            data['score'].append(details.get('vote_average', 'N/A'))
            data['genres'].append([g['name'] for g in details.get('genres', [])])
            data['release_date'].append(details.get('release_date', 'N/A'))
            poster_path = details.get('poster_path', '')
            data['image_url'].append(f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else '')

        elif self.current_media_type == 'tv':
            title = details.get('name') or details.get('title', 'N/A')
            data['title'].append(title)
            data['personal_score'].append(self.current_personal_score)
            data['score'].append(details.get('vote_average', 'N/A'))
            data['genres'].append([g['name'] for g in details.get('genres', [])])
            data['release_date'].append(details.get('first_air_date', 'N/A'))
            poster_path = details.get('poster_path', '')
            data['image_url'].append(f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else '')
        
        # Store the updated data
        self.store_json_data(data, conf['file_path'])
        media_label = "TV Show" if self.current_media_type == 'tv' else self.current_media_type.capitalize()
        messagebox.showinfo("Success", f"{media_label} added successfully!")
        
        # Go back to previous screen
        if self.back_callback:
            self.back_callback()

    def get_selected(self):
        self.current_media_type = self.selected_et.get()
        search_term = self.name_inp.get()
        self.current_personal_score = self.score_inp.get()
        
        if not search_term:
            messagebox.showerror("Error", "Please enter a name to search")
            return
        
        if not self.current_personal_score:
            messagebox.showerror("Error", "Please enter a personal score")
            return
        
        # Search based on media type
        results = []
        display_results = []
        
        if self.current_media_type == 'anime':
            results = self.search_anime(search_term)
            display_results = [f"{r.get('title', 'N/A')} ({r.get('type', 'N/A')}, {r.get('year', 'N/A')})" for r in results]
        elif self.current_media_type == 'manga':
            results = self.search_manga(search_term)
            display_results = [f"{r.get('title', 'N/A')} ({r.get('type', 'N/A')}, {r.get('year', 'N/A')})" for r in results]
        elif self.current_media_type == 'music':
            results = self.search_music(search_term)
            display_results = [f"{r.get('name', 'N/A')} by {r.get('artist', 'N/A')}" for r in results]
        elif self.current_media_type == 'movie':
            results = self.search_media(search_term, 'movie')
            display_results = [
                f"{r.get('title', 'N/A')} ({(r.get('release_date') or 'N/A')[:4]})"
                for r in results
            ]
        elif self.current_media_type == 'tv':
            results = self.search_media(search_term, 'tv')
            display_results = [
                f"{r.get('name', r.get('title', 'N/A'))} ({(r.get('first_air_date') or 'N/A')[:4]})"
                for r in results
            ]
        
        if not results:
            messagebox.showinfo("No Results", f"No results found for '{search_term}'")
            return
        
        # Show selection screen
        self.show_selection_screen(results, display_results)

    # UI screens
    def show_main_screen(self):
        # Clear current content
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main frame
        frm = ttk.Frame(self.root, padding=10)
        frm.pack()
        
        # Media type toggles; movies and TV live under the shared "Media" umbrella in the UI.
        self.selected_et = tk.StringVar()
        self.selected_et.set("music")

        media_choices = [
            ("Anime", "anime"),
            ("Manga", "manga"),
            ("Music", "music"),
            ("Movie", "movie"),
            ("TV Show", "tv")
        ]

        for idx, (label, value) in enumerate(media_choices):
            ttk.Radiobutton(frm, text=label, variable=self.selected_et, value=value).grid(
                column=0, row=idx, sticky=tk.W
            )

        next_row = len(media_choices)

        # Name input
        namel = tk.Label(frm, text="Name", font=(self.font, self.size))
        namel.grid(column=0, row=next_row, sticky=tk.W)
        self.name_inp = tk.Entry(frm, font=(self.font, self.size), width=30, relief="solid", bd=2)
        self.name_inp.grid(column=0, row=next_row + 1, sticky=tk.W)

        # Score input
        scorel = tk.Label(frm, text="Personal Score", font=(self.font, self.size))
        scorel.grid(column=0, row=next_row + 3, sticky=tk.W, pady=(20, 0))
        self.score_inp = tk.Entry(frm, font=(self.font, self.size), width=30, relief="solid", bd=2)
        self.score_inp.grid(column=0, row=next_row + 4, sticky=tk.W)

        # Buttons
        button_frame = tk.Frame(frm)
        button_frame.grid(column=0, row=next_row + 5, sticky=tk.W, pady=(20, 0))
        
        # Back button
        back_btn = tk.Button(button_frame, text="Back", font=(self.font, self.size), 
                            command=self.back_callback if self.back_callback else lambda: None)
        back_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Search button
        submit_button = tk.Button(button_frame, text="Search & Add", font=(self.font, self.size), 
                                 command=self.get_selected)
        submit_button.pack(side=tk.LEFT)

    def show_selection_screen(self, results, display_results):
        self.search_results = results
        
        # Clear current content
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Create main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Select the correct item:", font=(self.font, self.size))
        title_label.pack(pady=10)
        
        # Create listbox with scrollbar
        frame = tk.Frame(main_frame)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, font=(self.font, self.size-2))
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_listbox.yview)
        
        # Populate listbox
        for item in display_results:
            self.results_listbox.insert(tk.END, item)
        
        # Button frame
        button_frame = tk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        # Back button
        back_btn = tk.Button(button_frame, text="Back", command=self.show_main_screen, font=(self.font, self.size))
        back_btn.pack(side=tk.LEFT, padx=10)
        
        # Select button
        select_btn = tk.Button(button_frame, text="Select", command=self.on_item_selected, font=(self.font, self.size))
        select_btn.pack(side=tk.LEFT, padx=10)
