"""
car.py

Defines the Car class and its behavior.

Responsibilities:
- Store the car's position, speed, and direction
- Handle acceleration, braking, and steering
- Detect collisions with the track
- Update physics and movement each frame
- Render the car on the screen
"""

import math
import pygame


class Car:
    def __init__(self, x: float, y: float, angle: float = 0) -> None:
        
        self.original_sprite = pygame.image.load("assets/F1_CAR.png").convert_alpha()
        self.original_sprite = pygame.transform.smoothscale(self.original_sprite, (40, 20))
        
        self.is_colliding = False 
        self.collision_count = 0 
        self.on_start_finish = False
        self.lap_count = 0
        self.next_checkpoint = 0
        self.checkpoints_passed = 0
        self.on_checkpoint = False
        self.x = x
        self.y = y
        self.angle = angle
        self.idle_time = 0.0

        self.speed = 0.0
        self.max_forward_speed = 320.0

        self.acceleration = 220.0
        self.brake_force = 260.0
        self.friction = 140.0
        self.steering_speed = 140.0

        self.width = 40
        self.height = 20
        self.color = (220, 40, 40)

        self.alive = True

    def update(self, throttle: int, steering: int, track, dt: float) -> None:
        self._apply_engine(throttle, dt)
        self._apply_friction(throttle, dt)
        self._apply_steering(steering, dt)
        self._move(dt)
        if self.speed < 20:
            self.idle_time += dt
        else:
            self.idle_time = 0.0
        self._check_checkpoint(track)
        self._check_start_finish(track)
        self._check_collision(track)

    def _apply_engine(self, throttle: int, dt: float) -> None:
        if throttle > 0:
            self.speed += self.acceleration * dt
        elif throttle < 0:
            if self.speed > 0:
                self.speed -= self.brake_force * dt

        self.speed = max(0, min(self.speed, self.max_forward_speed))

    def _apply_friction(self, throttle: int, dt: float) -> None:
        if throttle == 0:
            if self.speed > 0:
                self.speed -= self.friction * dt
                if self.speed < 0:
                    self.speed = 0
            elif self.speed < 0:
                self.speed += self.friction * dt
                if self.speed > 0:
                    self.speed = 0

    def _apply_steering(self, steering: int, dt: float) -> None:
        if self.speed == 0:
            return

        speed_ratio = min(abs(self.speed) / self.max_forward_speed, 1.0)
        turn_amount = self.steering_speed * speed_ratio * dt

        if self.speed < 0:
            steering *= -1

        self.angle += steering * turn_amount

    def _move(self, dt: float) -> None:
        radians = math.radians(self.angle)
        self.x += math.cos(radians) * self.speed * dt
        self.y += math.sin(radians) * self.speed * dt

    def _check_collision(self, track) -> None:
        collision_detected = False

        for px, py in self.get_corners():
            if not track.is_on_track(px, py):
                collision_detected = True
                break

        if collision_detected and not self.is_colliding:
            self.collision_count += 1

            radians = math.radians(self.angle)

            # Save movement direction before changing speed
            direction = 1 if self.speed >= 0 else -1

            # Push the car opposite to the direction it was moving
            self.x -= math.cos(radians) * 10 * direction
            self.y -= math.sin(radians) * 10 * direction

            # Bounce the car back
            self.speed = -self.speed * 0.5

        self.is_colliding = collision_detected

    def _bounce(self) -> None:
        # reverse the velocity
        self.speed = -self.speed * 0.5

        # push the car slightly backward
        radians = math.radians(self.angle)
        self.x -= math.cos(radians) * 10
        self.y -= math.sin(radians) * 10

    def get_corners(self) -> list[tuple[float, float]]:
        half_w = self.width / 2
        half_h = self.height / 2

        local_corners = [
            (-half_w, -half_h),
            (half_w, -half_h),
            (half_w, half_h),
            (-half_w, half_h),
        ]

        radians = math.radians(self.angle)
        cos_a = math.cos(radians)
        sin_a = math.sin(radians)

        world_corners = []
        for local_x, local_y in local_corners:
            world_x = self.x + (local_x * cos_a - local_y * sin_a)
            world_y = self.y + (local_x * sin_a + local_y * cos_a)
            world_corners.append((world_x, world_y))

        return world_corners

    def draw(self, surface: pygame.Surface, camera_x: float, camera_y: float) -> None:
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y

        rotated_sprite = pygame.transform.rotate(self.original_sprite, -self.angle)
        rotated_rect = rotated_sprite.get_rect(center=(screen_x, screen_y))

        surface.blit(rotated_sprite, rotated_rect)

    def get_sensor_data(self, track) -> list[float]:
        sensor_angles = [-60, -30, 0, 30, 60]
        max_distance = 200
        readings = []

        for offset in sensor_angles:
            distance = self._cast_ray(track, offset, max_distance)
            readings.append(distance / max_distance)

        return readings
    
    def _cast_ray(self, track, offset_angle: float, max_distance: int) -> float:
        ray_angle = math.radians(self.angle + offset_angle)

        for distance in range(0, max_distance, 4):
            test_x = self.x + math.cos(ray_angle) * distance
            test_y = self.y + math.sin(ray_angle) * distance

            if not track.is_on_track(test_x, test_y):
                return distance

        return max_distance
    
    def reset(self, x: float, y: float, angle: float) -> None:
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 0.0
        self.is_colliding = False
        self.collision_count = 0
        self.next_checkpoint = 0
        self.checkpoints_passed = 0
        self.on_checkpoint = False
        self.idle_time = 0.0
        self.on_start_finish = False
        self.lap_count = 0

    def _check_start_finish(self, track) -> None:
        is_touching_line = track.is_on_start_finish(self.x, self.y)

        if is_touching_line and not self.on_start_finish:
            self.lap_count += 1

        self.on_start_finish = is_touching_line

    def _check_checkpoint(self, track) -> bool:
        is_touching_checkpoint = track.is_on_checkpoint(self.next_checkpoint, self.x, self.y)

        if is_touching_checkpoint and not self.on_checkpoint:
            self.checkpoints_passed += 1
            self.next_checkpoint += 1
            self.idle_time = 0.0

            if self.next_checkpoint >= len(track.checkpoints):
                self.next_checkpoint = 0
                self.lap_count += 1

            self.on_checkpoint = True
            return True

        if not is_touching_checkpoint:
            self.on_checkpoint = False

        return False