import torch
import torch.nn as nn
import torch.nn.functional as F

class Brain(nn.Module):
    def __init__(self, num_rays, hidden_layers):
        """
        A neural network brain for the car that processes raycast distances.
        
        Args:
            car: The car object this brain control            num_rays: Number of raycast distances to process
            hidden_layers: List of integers representing hidden layer sizes
        """
        super(Brain, self).__init__()
        
        # Build network layers
        self.layers = nn.ModuleList()
        
        if hidden_layers:
            # Input layer
            input_layer = nn.Linear(num_rays, hidden_layers[0])
            self.layers.append(input_layer)
            
            # Hidden layers
            for i in range(len(hidden_layers) - 1):
                hidden_layer = nn.Linear(hidden_layers[i], hidden_layers[i + 1])
                self.layers.append(hidden_layer)
                
            # Output layer (steering only)
            self.output_layer = nn.Linear(hidden_layers[-1], 1)
        else:
            # Direct input to output if no hidden layers
            self.output_layer = nn.Linear(num_rays, 1)
        
        # Initialize weights and biases
        self.randomize_weights()
        
    def randomize_weights(self):
        """Initialize all weights with Xavier uniform and biases to zero."""
        for layer in self.layers:
            nn.init.xavier_uniform_(layer.weight)
            nn.init.zeros_(layer.bias)
            
        nn.init.xavier_uniform_(self.output_layer.weight)
        nn.init.zeros_(self.output_layer.bias)
        
    def forward(self, x):
        # Apply hidden layers with ReLU activation if they exist
        for layer in self.layers:
            x = F.relu(layer(x))
            
        # Output layer with tanh to get values between -1 and 1
        x = self.output_layer(x)
        return torch.tanh(x)
        
    def think(self, ray_distances):
        """
        Process the raycast distances and return actions.
        
        Args:
            ray_distances: List or tensor of raycast distances
            
        Returns:
            steering values between -1 and 1
        """
        
        with torch.no_grad():
            # Convert to tensor if it's a list
            if isinstance(ray_distances, list):
                ray_distances = torch.tensor(ray_distances, dtype=torch.float32)
                
            # Add batch dimension if needed
            if len(ray_distances.shape) == 1:
                ray_distances = ray_distances.unsqueeze(0)
                
            # Get network output (steering only)
            steering = self(ray_distances)[0].item()
            
            return steering

    def mutate(self, example_brain, mutation_rate=0.01):
        for layer in self.layers:
            layer.weight.data += torch.randn_like(layer.weight.data) * 0.01
            layer.bias.data += torch.randn_like(layer.bias.data) * 0.01
