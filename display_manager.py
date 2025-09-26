import pygame
import json
import os


class DisplayManager:
    def __init__(self):
        self.config = self.load_config()

        self.resolutions = [
            {"name": "1280x720 (720p)", "size": (1280, 720)},
            {"name": "1920x1080 (1080p)", "size": (1920, 1080)},
            {"name": "2048x1080 (2K Cinema)", "size": (2048, 1080)},
            {"name": "2560x1440 (2K QHD)", "size": (2560, 1440)},
            {"name": "3840x2160 (4K UHD)", "size": (3840, 2160)}
        ]

        self.current_res_index = 1
        current_res = tuple(self.config["resolution"])
        for i, res in enumerate(self.resolutions):
            if res["size"] == current_res:
                self.current_res_index = i
                break

        self.current_resolution = self.resolutions[self.current_res_index]["size"]
        self.fullscreen = self.config["fullscreen"]
        self.borderless = self.config["borderless"]
        self.setup_display()

    def load_config(self):
        CONFIG_FILE = "game_config.json"
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {
                    "resolution": [1920, 1080],
                    "fullscreen": False,
                    "borderless": False,
                    "music_volume": 0.7,
                    "sfx_volume": 0.8
                }
        else:
            default_config = {
                "resolution": [1920, 1080],
                "fullscreen": False,
                "borderless": False,
                "music_volume": 0.7,
                "sfx_volume": 0.8
            }
            self.save_config(default_config)
            return default_config

    def save_config(self, config):
        CONFIG_FILE = "game_config.json"
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)

    def setup_display(self):
        if self.borderless:
            self.screen = pygame.display.set_mode(self.current_resolution, pygame.NOFRAME)
        elif self.fullscreen:
            self.screen = pygame.display.set_mode(self.current_resolution, pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.current_resolution, pygame.RESIZABLE)
        pygame.display.set_caption("DC Auto Battler")

    def set_resolution(self, index):
        if 0 <= index < len(self.resolutions):
            self.current_res_index = index
            new_res = self.resolutions[index]["size"]
            self.current_resolution = new_res
            self.config["resolution"] = list(new_res)
            self.setup_display()
            self.save_config(self.config)
            return True
        return False

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.config["fullscreen"] = self.fullscreen
        self.setup_display()
        self.save_config(self.config)

    def toggle_borderless(self):
        self.borderless = not self.borderless
        self.config["borderless"] = self.borderless
        self.setup_display()
        self.save_config(self.config)

    def get_current_resolution_name(self):
        return self.resolutions[self.current_res_index]["name"]