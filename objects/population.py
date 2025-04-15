from objects.car import Car
from objects.brain import Brain
import random
import pickle

class Population:
    def __init__(self, size, track):
        self.size = size
        self.cars = []
        self.track = track
        self.generation = 0
        self.test_positions = 3  # Number of different start positions to test each car
        self.current_test_position = 0
        self.stats = []
        self.reset_population(track)

    def reset_population(self, track, best_car=None):
        if self.generation % 100 == 0 and self.generation != 0:
            self.save_model()
        if len(self.cars) > 0:
            #add the fitness of the best car to the stats
            self.stats.append(self.get_best_car()["fitness"])
        self.cars = []
        start_angle, start_pos = track.randomize_start_pos()
        x, y = track.pixel_to_world(start_pos[1], start_pos[0])

        if best_car:
            # Keep the best car unchanged
            car = Car(x, y, track, color=(0, 0, 255))
            car.angle = start_angle
            self.cars.append({"car": car, "fitness": 0, "brain": best_car["brain"]})
            
            # Create variations of the best car
            for _ in range(self.size - 1):
                brain = Brain(5, [5])  # Simplified network
                brain.mutate(best_car["brain"], mutation_rate=0.01)  # Single mutation rate
                car = Car(x, y, track)
                car.angle = start_angle
                self.cars.append({"car": car, "fitness": 0, "brain": brain})
        else:
            # Initial population - all random
            for _ in range(self.size):
                brain = Brain(5, [5])  # Simplified network
                brain.randomize_weights()
                car = Car(x, y, track)
                car.angle = start_angle
                self.cars.append({"car": car, "fitness": 0, "brain": brain})

    def save_model(self):
        with open(f"models/model_{self.generation}.pkl", "wb") as f:
            pickle.dump(self.cars[0]["brain"], f)
        with open("stats.txt", "w") as f:
            for stat in self.stats:
                f.write(f"{stat},")

    def update_population(self):
        for car in self.cars:
            ray_distances = car["car"].ray_cast()
            steering = car["brain"].think(ray_distances)
            car["car"].control(steering, 0.35)
            car["car"].update()
            # Simplified fitness: just distance traveled
            car["fitness"] = car["car"].distance_traveled
        if self.population_dead():
            if self.current_test_position < self.test_positions:
                self.current_test_position += 1
                start_angle, start_pos = self.track.randomize_start_pos()
                # Reset all cars to the new start position and don't change the distance traveled to add the fitnesses of all the start positions
                for car in self.cars:
                    car["car"].x, car["car"].y = self.track.pixel_to_world(start_pos[1], start_pos[0])
                    car["car"].angle = start_angle
                    car["car"].is_alive = True # Reset alive status
            else:
                self.breed_population(self.get_best_car())
                self.generation += 1
                self.current_test_position = 0

    def draw_population(self, screen):
        for car in self.cars:
            car["car"].draw(screen)

    def population_dead(self):
        return sum(car["car"].is_alive for car in self.cars) == 0

    def get_best_car(self):
        return max(self.cars, key=lambda x: x["fitness"])

    def breed_population(self, best_car):
        self.reset_population(self.track, best_car)

