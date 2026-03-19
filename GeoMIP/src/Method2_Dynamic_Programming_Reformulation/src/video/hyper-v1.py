from manim import *
import numpy as np
import itertools

class NCubeDataVisualization(ThreeDScene):
    def construct(self):
        # Configuración de cámara...
        
        # Ejemplo de datos 4D CORREGIDO (shape=2x2x2x2)
        ncube_data = np.array([
            [
                [[0.0,1.0], [1.0,0.0]],
                [[0.5,0.5], [0.5,0.5]]
            ],
            [
                [[0.5,0.5], [0.5,0.5]],
                [[1.0,0.0], [0.0,1.0]]
            ]
        ])
        
        cube = self.create_cube_with_data(ncube_data)
        self.play(Create(cube))
        self.wait(2)
    
    def create_cube_with_data(self, data, position=ORIGIN):
        # Verificar que todas las dimensiones sean tamaño 2
        assert all(dim == 2 for dim in data.shape), "El array debe ser 2x2x...x2"
        
        n_dims = data.ndim
        vertices = list(itertools.product([0,1], repeat=n_dims)) 
        # Proyección 3D con ajuste para dimensiones superiores
        scale = 2.0
        delta = 0.5  # Separación para dimensiones >3
        projected = []
        for v in vertices:
            coords = list(v[:3]) + [0]*(3 - len(v))  # Base 3D
            pos = np.array(coords) * scale - np.array([1, 1, 1])
            
            # Añadir desplazamiento por dimensiones extras
            for dim in range(3, n_dims):
                axis = (dim - 3) % 3  # Alternar ejes X/Y/Z
                pos[axis] += v[dim] * delta
            projected.append(pos + position)
        
        cube_group = VGroup()
        values = [float(data[v]) for v in vertices]
        
        # Vértices y etiquetas
        for i, pos in enumerate(projected):
            color = self.get_color_from_value(values[i])
            dot = Sphere(radius=0.1, color=color).move_to(pos)
            label = Text(f"{values[i]:.1f}", font_size=14).next_to(pos, OUT)
            cube_group.add(dot, label)
            self.add_fixed_in_frame_mobjects(label)
        
        # Aristas (conexiones adyacentes)
        edges = []
        for i, j in itertools.combinations(range(len(vertices)), 2):
            if sum(a != b for a, b in zip(vertices[i], vertices[j])) == 1:
                line = Line3D(projected[i], projected[j], color=GREY, thickness=0.02)
                cube_group.add(line)
        
        return cube_group
    
    def get_color_from_value(self, value):
        return interpolate_color(BLUE, RED, value)