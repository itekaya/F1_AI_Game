"""
Entry point of the project.

Responsibilities:
- Load the track and assets
- Run AI training using NEAT
- Manage generations of AI drivers
- Update and render cars during simulation
"""

import os
import sys
import pygame
import neat

from car import Car
from track import Track

WIDTH = 1200
HEIGHT = 700
FPS = 60
TITLE = "F1 AI Racing"
generation = 0 


def eval_genomes(genomes, config) -> None:
    global generation
    generation += 1
    nets = []
    cars = []
    ge = []

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 30)

    track = Track()

    camera_x = track.spawn_position[0] - WIDTH / 2
    camera_y = track.spawn_position[1] - HEIGHT / 2
    camera_speed = 600
    follow_car = True
    checkpoint_editor_mode = True
    checkpoint_width = 160
    checkpoint_thickness = 20
    checkpoint_orientation = "horizontal"


    for _, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)

        car = Car(*track.spawn_position, track.spawn_angle)
        cars.append(car)

        genome.fitness = 0.0
        ge.append(genome)

    max_frames = 2000
    frame_count = 0
    running = True

    while running and len(cars) > 0 and frame_count < max_frames:
        dt = clock.tick(FPS) / 1000.0
        if len(cars) > 0 and follow_car:
            camera_x = cars[0].x - WIDTH / 2
            camera_y = cars[0].y - HEIGHT / 2
        frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    checkpoint_orientation = "horizontal"
                elif event.key == pygame.K_v:
                    checkpoint_orientation = "vertical"
                elif event.key == pygame.K_BACKSPACE:
                    if len(track.checkpoints) > 0:
                        track.checkpoints.pop()
                        track.save_checkpoints()
                elif event.key == pygame.K_p:
                    print("self.checkpoints = [")
                    for checkpoint in track.checkpoints:
                        print(
                            f"    pygame.Rect({checkpoint.x}, {checkpoint.y}, {checkpoint.width}, {checkpoint.height}),"
                        )
                    print("]")

            if event.type == pygame.MOUSEBUTTONDOWN and checkpoint_editor_mode:
                if event.button == 1:
                    mouse_x, mouse_y = event.pos

                    world_x = mouse_x + camera_x
                    world_y = mouse_y + camera_y

                    if checkpoint_orientation == "horizontal":
                        rect = pygame.Rect(
                            int(world_x - checkpoint_width / 2),
                            int(world_y - checkpoint_thickness / 2),
                            checkpoint_width,
                            checkpoint_thickness,
                        )
                    else:
                        rect = pygame.Rect(
                            int(world_x - checkpoint_thickness / 2),
                            int(world_y - checkpoint_width / 2),
                            checkpoint_thickness,
                            checkpoint_width,
                        )

                    track.checkpoints.append(rect)
                    track.save_checkpoints()

        keys = pygame.key.get_pressed()

        # Toggle follow camera
        if keys[pygame.K_f]:
            follow_car = False
        if keys[pygame.K_g]:
            follow_car = True

        # Manual camera movement
        if not follow_car:
            if keys[pygame.K_z]:
                camera_y -= camera_speed * dt
            if keys[pygame.K_s]:
                camera_y += camera_speed * dt
            if keys[pygame.K_q]:
                camera_x -= camera_speed * dt
            if keys[pygame.K_d]:
                camera_x += camera_speed * dt

        i = 0
        while i < len(cars):
            car = cars[i]

            sensor_data = car.get_sensor_data(track)
            inputs = sensor_data + [car.speed / car.max_forward_speed]

            output = nets[i].activate(inputs)

            throttle = 0
            steering = 0

            if output[0] > 0.5:
                throttle = 1
            else:
                throttle = 0

            if output[1] > 0.5:
                steering = 1
            elif output[1] < -0.5:
                steering = -1

            previous_collisions = car.collision_count
            previous_checkpoints = car.checkpoints_passed
            previous_laps = car.lap_count

            car.update(throttle, steering, track, dt)

            ge[i].fitness += 0.05
            ge[i].fitness += max(car.speed, 0) * 0.01

            if car.checkpoints_passed > previous_checkpoints:
                ge[i].fitness += 20.0

            if car.lap_count > previous_laps:
                ge[i].fitness += 100.0

            if car.collision_count > previous_collisions:
                ge[i].fitness -= 5.0

            if car.collision_count >= 5:
                ge[i].fitness -= 2.0
                del nets[i]
                del cars[i]
                del ge[i]
            elif car.idle_time >= 3.0:
                ge[i].fitness -= 5.0
                del nets[i]
                del cars[i]
                del ge[i]
            else:
                i += 1

        if len(cars) == 0:
            break

        track.draw(screen, camera_x, camera_y)

        for car in cars:
            car.draw(screen, camera_x, camera_y)

        text = font.render(f"Cars alive: {len(cars)}", True, (255, 255, 255))

        lap_text = font.render(f"Laps: {cars[0].lap_count}", True, (255, 255, 255))
        screen.blit(lap_text, (20, 90))
        lap_text = font.render(f"Laps: {cars[0].lap_count}", True, (255, 255, 255))
        screen.blit(lap_text, (20, 55))
        screen.blit(text, (20, 20))
        gen_text = font.render(f"Generation: {generation}", True, (255, 255, 255))
        screen.blit(gen_text, (20, 45))

        pygame.display.flip()

    pygame.display.quit()


def run_neat(config_path: str) -> None:
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.StatisticsReporter())

    population.run(eval_genomes, 50)


def main() -> None:
    pygame.init()

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")

    run_neat(config_path)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()