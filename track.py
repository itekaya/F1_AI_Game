"""
track.py

Defines the race track and environment.

Responsibilities:
- Load the visible track image
- Load the collision mask
- Store the spawn point
- Draw the track with camera offset
- Check whether a world position is on the road
"""

import os
import pygame
import json


class Track:
    def __init__(self) -> None:
        self.background_color = (20, 20, 20)

        base_path = os.path.dirname(__file__)
        track_path = os.path.join(base_path, "assets", "track_new.png")
        mask_path = os.path.join(base_path, "assets", "track_new_mask.png")

        self.image = pygame.image.load(track_path).convert()
        self.mask_image = pygame.image.load(mask_path).convert()

        self.width = self.image.get_width()
        self.height = self.image.get_height()

        self.spawn_position = (399, 660)
        self.spawn_angle = 0
        self.checkpoints_file = os.path.join(base_path, "assets", "checkpoints.json")
        self.checkpoints = self._load_checkpoints()
        self.start_finish_rect = pygame.Rect(399, 560, 20, 140)

    def draw(self, surface: pygame.Surface, camera_x: float, camera_y: float) -> None:
        surface.fill(self.background_color)
        surface.blit(self.image, (-camera_x, -camera_y))

        font = pygame.font.SysFont(None, 22)

        for i, checkpoint in enumerate(self.checkpoints):
            checkpoint_screen = checkpoint.move(-camera_x, -camera_y)
            pygame.draw.rect(surface, (0, 0, 255), checkpoint_screen, 2)

            label = font.render(str(i), True, (0, 0, 255))
            surface.blit(label, (checkpoint_screen.x, checkpoint_screen.y - 18))

            
        start_finish_screen_rect = self.start_finish_rect.move(-camera_x, -camera_y)
        pygame.draw.rect(surface, (255, 255, 255), start_finish_screen_rect)

    def is_on_track(self, x: float, y: float) -> bool:
        px = int(x)
        py = int(y)

        if px < 0 or px >= self.width or py < 0 or py >= self.height:
            return False

        color = self.mask_image.get_at((px, py))

        return color.r > 200 and color.g > 200 and color.b > 200
    
    def is_on_start_finish(self, x: float, y: float) -> bool:
        return self.start_finish_rect.collidepoint(int(x), int(y))
    
    def is_on_checkpoint(self, checkpoint_index: int, x: float, y: float) -> bool:
        if checkpoint_index < 0 or checkpoint_index >= len(self.checkpoints):
            return False

        return self.checkpoints[checkpoint_index].collidepoint(int(x), int(y))
    
    def _load_checkpoints(self) -> list[pygame.Rect]:
        if not os.path.exists(self.checkpoints_file):
            return []

        with open(self.checkpoints_file, "r", encoding="utf-8") as file:
            raw_checkpoints = json.load(file)

        return [
            pygame.Rect(
                checkpoint["x"],
                checkpoint["y"],
                checkpoint["width"],
                checkpoint["height"],
            )
            for checkpoint in raw_checkpoints
        ]


    def save_checkpoints(self) -> None:
        data = [
            {
                "x": checkpoint.x,
                "y": checkpoint.y,
                "width": checkpoint.width,
                "height": checkpoint.height,
            }
            for checkpoint in self.checkpoints
        ]

        with open(self.checkpoints_file, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)