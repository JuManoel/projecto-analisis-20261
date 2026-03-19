from manim import *
import numpy as np
import itertools

class NCubeSystem(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=70*DEGREES, theta=-30*DEGREES)
        
        # Hipercubo 4D de ejemplo (2x2x2x2)
        hypercube = np.array([
            [
                [[0.0,1.0], [1.0,0.0]],
                [[0.5,0.5], [0.5,0.5]]
            ],
            [
                [[0.5,0.5], [0.5,0.5]],
                [[1.0,0.0], [0.0,1.0]]
            ]
        ])
        
        # Visualización original
        original = self.create_hypercube(hypercube, LEFT*3)
        original_label = Text("4D Original").next_to(original, DOWN)
        
        # Transformación: Promedio en la 4ta dimensión
        transformed_data = np.mean(hypercube, axis=3, keepdims=False)
        transformed = self.create_hypercube(transformed_data, RIGHT*3)
        transformed_label = Text("3D Promediado").next_to(transformed, DOWN)
        
        self.play(
            Create(original), 
            Write(original_label),
            run_time=2
        )
        self.wait()
        
        self.play(
            Transform(original.copy(), transformed),
            Write(transformed_label),
            run_time=3
        )
        self.wait(3)
    
    def create_hypercube(self, data, position=ORIGIN):
        """Visualización adaptable de N-cubos con proyección jerárquica"""
        n_dims = data.ndim
        vertices = list(itertools.product([0, 1], repeat=n_dims))
        
        # Sistema de proyección recursiva
        def project(v):
            # v es una tupla (o lista) de 0s y 1s de longitud n
            if len(v) <= 3:
                # Rellenar con ceros hasta tener 3 componentes
                padded = list(v) + [0] * (3 - len(v))
                return np.array(padded) * 2 - np.array([1, 1, 1])
            else:
                # Para dimensiones extra, usamos la última componente para un desplazamiento
                # que depende de cuántas dimensiones extra haya.
                extra_index = len(v) - 3  # 1 para 4D, 2 para 5D, etc.
                # Definir direcciones para el desplazamiento (se alternan)
                offset_dirs = [RIGHT, UP, OUT]
                offset = 1.5 * offset_dirs[(extra_index - 1) % len(offset_dirs)]
                # Se proyecta recursivamente quitando la última componente
                return project(v[:-1]) + v[-1] * offset

        cube = VGroup()
        edge_cache = set()
        
        # Vértices y aristas
        for v in vertices:
            pos = project(v) + position
            value = data[tuple(v)]
            
            # Esfera con color y etiqueta
            sphere = Sphere(radius=0.1, color=self.color_map(value))
            label = Text(f"{value:.1f}", font_size=14).next_to(pos, OUT)
            cube.add(sphere, label)
            self.add_fixed_in_frame_mobjects(label)
            
            # Conexiones para aristas
            for i in range(n_dims):
                neighbor = list(v)
                neighbor[i] = 1 - neighbor[i]  # Invertir bit
                if tuple(neighbor) in vertices:
                    edge = tuple(sorted((v, tuple(neighbor))))
                    if edge not in edge_cache:
                        start = project(v) + position
                        end = project(neighbor) + position
                        line = Line3D(start, end, color=WHITE, thickness=0.02)
                        cube.add(line)
                        edge_cache.add(edge)
        
        return cube
    
    def color_map(self, value):
        return interpolate_color(BLUE, RED, value)
