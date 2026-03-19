from manim import *
import numpy as np
import itertools

class NCubeVisualizer(ThreeDScene):
    def construct(self):
        # Configuración de la cámara 3D
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        self.begin_ambient_camera_rotation(rate=0.2)
        
        # Ejemplo de un cubo 3D (array de forma 2x2x2)
        cube_data = np.array([[[.5, .5],
                              [1., 0.]],
                             [[0., 1.],
                              [1., 0.]]])
        
        # Visualizar el cubo 3D
        self.visualize_ncube(cube_data)
        
        # Detener rotación
        self.wait(5)
        self.stop_ambient_camera_rotation()
        self.wait(1)
        self.clear()
        
        # Configurar cámara para 4D
        self.set_camera_orientation(phi=70 * DEGREES, theta=20 * DEGREES)
        self.begin_ambient_camera_rotation(rate=0.15)
        
        # Crear un hipercubo 4D (2x2x2x2)
        hypercube_data = np.zeros((2, 2, 2, 2))
        for indices in itertools.product([0, 1], repeat=4):
            hypercube_data[indices] = np.sum(indices) / 4
        
        # Visualizar el hipercubo 4D
        self.visualize_ncube(hypercube_data)
        
        # Detener rotación
        self.wait(5)
        self.stop_ambient_camera_rotation()
        self.wait(1)
    
    def dim_to_letter(self, dim):
        """Convierte un número de dimensión a su letra correspondiente (0->A, 1->B, etc.)"""
        return chr(65 + dim)  # 65 es el código ASCII para 'A'
    
    def create_3d_vertex(self, position, value):
        """Crea un vértice 3D con su valor"""
        # Crear esfera para el vértice
        sphere = Sphere(radius=0.1, resolution=(15, 15))
        sphere.set_color(self.value_to_color(value))
        sphere.move_to(position)
        
        # Crear texto 3D para el valor
        value_text = DecimalNumber(value, num_decimal_places=2, font_size=24)
        value_text.next_to(sphere, UP, buff=0.1)
        
        return VGroup(sphere, value_text)
    
    def visualize_ncube(self, data):
        """Visualiza un n-cubo con valores en los vértices"""
        # Detectar la dimensión del array
        if np.isscalar(data):  # Caso 0D
            n_dims = 0
        else:
            n_dims = len(data.shape)
        
        # Crear título 3D
        title = Text(f"Visualización de {n_dims}-Cubo", font_size=36)
        title.to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title))
        
        # Generar coordenadas de vértices según la dimensión
        if n_dims <= 1:
            # Casos especiales de 0D y 1D
            if n_dims == 0:
                # 0D: un solo punto
                value = float(data)
                vertex = self.create_3d_vertex(ORIGIN, value)
                self.play(Create(vertex))
                return
            else:
                # 1D: línea con dos puntos
                vertex_coords = [(0,), (1,)]
        else:
            # Para dimensiones mayores, generamos todas las combinaciones de 0 y 1
            vertex_coords = list(itertools.product([0, 1], repeat=n_dims))
        
        # Crear vértices y aristas
        vertices = VGroup()
        edges = VGroup()
        vertex_spheres = {}  # Para referencias a los vértices
        
        # Función para obtener posición 3D según coordenadas
        def get_position(coords):
            if n_dims == 1:
                # 1D: en el eje X
                return np.array([coords[0] * 2 - 1, 0, 0])
            elif n_dims == 2:
                # 2D: en el plano XY
                return np.array([coords[0] * 2 - 1, coords[1] * 2 - 1, 0])
            elif n_dims == 3:
                # 3D: cubo centrado en el origen
                return np.array([coords[0] * 2 - 1, coords[1] * 2 - 1, coords[2] * 2 - 1])
            else:
                # 4D+: proyección de hipercubo usando cubos anidados
                # Base: cubo 3D para las primeras 3 dimensiones
                base = np.array([coords[0] * 2 - 1, coords[1] * 2 - 1, coords[2] * 2 - 1])
                
                # Las dimensiones adicionales crean un desplazamiento en cada dirección
                for i in range(3, n_dims):
                    if coords[i] == 1:
                        # Crear un segundo cubo desplazado
                        factor = 0.35  # Factor de escala para el desplazamiento
                        if i == 3:
                            # 4a dimensión: desplazamiento diagonal sutil
                            base = base * (1 + coords[i] * factor)
                        else:
                            # 5a+ dimensión: pequeños desplazamientos adicionales
                            base = base * (1 + coords[i] * factor * 0.5)
                
                return base
        
        # Crear vértices
        for coords in vertex_coords:
            position = get_position(coords)
            
            # Obtener valor para este vértice
            try:
                if n_dims == 1:
                    value = float(data[coords[0]])
                else:
                    value = float(data[coords])
            except (IndexError, TypeError):
                value = 0
            
            # Crear vértice 3D
            vertex = Sphere(radius=0.1, resolution=(15, 15))
            vertex.set_color(self.value_to_color(value))
            vertex.move_to(position)
            vertices.add(vertex)
            vertex_spheres[coords] = vertex
            
            # Crear etiqueta de valor
            value_text = DecimalNumber(value, num_decimal_places=2, font_size=20)
            # Convertir a objeto 3D que sigue a la cámara
            value_text_3d = value_text.copy()
            value_text.move_to(position + UP * 0.2)
            self.add_fixed_orientation_mobjects(value_text)
            
            # Crear etiqueta de coordenadas usando letras
            if n_dims > 1:
                coord_text = "".join([self.dim_to_letter(i) for i, v in enumerate(coords) if v == 1])
                if not coord_text:  # Origen
                    coord_text = "O"
                    
                coord_label = Text(coord_text, font_size=16)
                coord_label.move_to(position + DOWN * 0.2)
                self.add_fixed_orientation_mobjects(coord_label)
        
        # Crear aristas entre vértices
        if n_dims >= 1:
            for i, coords1 in enumerate(vertex_coords):
                for coords2 in vertex_coords[i+1:]:
                    # Calcular cuántos índices son diferentes
                    diff_count = sum(1 for a, b in zip(coords1, coords2) if a != b)
                    
                    # Conectar con arista si difieren en exactamente una coordenada
                    if diff_count == 1:
                        # Determinar qué dimensión cambió
                        dim_changed = next((i for i, (a, b) in enumerate(zip(coords1, coords2)) if a != b), None)
                        
                        # Colores para aristas según dimensión
                        dim_colors = [RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE]
                        edge_color = dim_colors[dim_changed % len(dim_colors)]
                        
                        # Crear arista 3D
                        start = vertex_spheres[coords1].get_center()
                        end = vertex_spheres[coords2].get_center()
                        edge = Line3D(start=start, end=end, color=edge_color)
                        edges.add(edge)
        
        # Añadir leyenda para dimensiones
        dim_labels = VGroup()
        if n_dims > 1:
            for d in range(min(n_dims, 6)):  # Limitar a 6 dimensiones en la leyenda
                letter = self.dim_to_letter(d)
                dim_colors = [RED, GREEN, BLUE, YELLOW, PURPLE, ORANGE]
                color = dim_colors[d % len(dim_colors)]
                dim_label = Text(f"Dim {letter}", font_size=20, color=color)
                dim_label.to_corner(UL).shift(DOWN * (d * 0.4 + 0.5) + RIGHT * 0.5)
                self.add_fixed_in_frame_mobjects(dim_label)
                dim_labels.add(dim_label)
        
        # Añadir leyenda de color-valor
        color_legend = self.create_color_legend()
        self.add_fixed_in_frame_mobjects(color_legend)
        
        # Animar la creación de la visualización
        self.play(Create(edges), run_time=2)
        self.play(Create(vertices), run_time=1.5)
        if n_dims > 1:
            self.play(Write(dim_labels), run_time=1)
        self.play(FadeIn(color_legend))
        
        # Dejar que la cámara rote y explore la visualización
        self.wait(2)
    
    def create_color_legend(self):
        """Crea una leyenda para la escala de colores"""
        # Crear rectángulo para el gradiente
        segments = 10
        gradient_group = VGroup()
        
        for i in range(segments):
            t = i / (segments - 1)  # Valor de 0 a 1
            color = self.value_to_color(t)
            segment = Rectangle(
                height=0.3, 
                width=3/segments,
                fill_color=color,
                fill_opacity=1,
                stroke_width=0
            ).shift(RIGHT * (3/segments) * (i - segments/2 + 0.5))
            gradient_group.add(segment)
        
        # Añadir borde al gradiente
        border = Rectangle(height=0.3, width=3, stroke_color=WHITE, stroke_width=1, fill_opacity=0)
        gradient_group.add(border)
        
        # Etiquetas
        min_label = Text("0.0", font_size=16).next_to(gradient_group, LEFT)
        max_label = Text("1.0", font_size=16).next_to(gradient_group, RIGHT)
        title = Text("Valor", font_size=20).next_to(gradient_group, UP)
        
        # Agrupar todo
        legend = VGroup(gradient_group, min_label, max_label, title)
        legend.to_corner(DR)
        
        return legend
    
    def value_to_color(self, value):
        """Convierte un valor entre 0 y 1 a un color en escala azul-rojo"""
        # Asegurar que el valor esté entre 0 y 1
        value = min(max(float(value), 0), 1)
        
        # Interpolación simple entre azul y rojo
        return interpolate_color(BLUE, RED, value)


# Clase para visualizar un hipercubo 5D
class Hypercube5D(NCubeVisualizer):
    def construct(self):
        # Configuración de la cámara 3D
        self.set_camera_orientation(phi=70 * DEGREES, theta=20 * DEGREES)
        self.begin_ambient_camera_rotation(rate=0.15)
        
        # Crear un hipercubo 5D (2x2x2x2x2)
        hypercube_data = np.zeros((2, 2, 2, 2, 2))
        
        # Llenar con valores basados en combinaciones de índices
        for indices in itertools.product([0, 1], repeat=5):
            # Valor basado en coordenadas (ejemplo: suma normalizada)
            hypercube_data[indices] = np.sum(indices) / 5
        
        # Visualizar
        self.visualize_ncube(hypercube_data)
        
        # Detener rotación
        self.wait(5)
        self.stop_ambient_camera_rotation()
        self.wait(1)


# Para ejecutar:
# manim -pql ncube_visualizer.py NCubeVisualizer  # 0D a 4D
# manim -pql ncube_visualizer.py Hypercube5D      # 5D