from manim import *
import numpy as np
import itertools

class NCubeVisualizer(Scene):
    def construct(self):
        # Ejemplos para diferentes dimensiones
        # 0D (un solo punto)
        point_data = np.array(0.75)
        self.visualize_ncube(point_data)
        self.wait(1)
        self.clear()
        
        # 1D (línea)
        line_data = np.array([0.25, 0.75])
        self.visualize_ncube(line_data)
        self.wait(1)
        self.clear()
        
        # 2D (cuadrado)
        square_data = np.array([[0.2, 0.4],
                               [0.6, 0.8]])
        self.visualize_ncube(square_data)
        self.wait(1)
        self.clear()
        
        # 3D (cubo)
        cube_data = np.array([[[.5, .5],
                              [1., 0.]],
                             [[0., 1.],
                              [1., 0.]]])
        self.visualize_ncube(cube_data)
        self.wait(1)
        self.clear()
        
        # 4D (hipercubo)
        hypercube_data = np.zeros((2, 2, 2, 2))
        for indices in itertools.product([0, 1], repeat=4):
            hypercube_data[indices] = np.sum(indices) / 4
        self.visualize_ncube(hypercube_data)
    
    def dim_to_letter(self, dim):
        """Convierte un número de dimensión a su letra correspondiente (0->A, 1->B, etc.)"""
        return chr(65 + dim)  # 65 es el código ASCII para 'A'
    
    def project_nested_cube(self, coords, scale_factor=0.7):
        """Proyecta usando el enfoque de cubos anidados/teseracto"""
        n_dims = len(coords)
        
        if n_dims <= 3:
            # Para 3D o menos, usamos proyección isométrica
            return self.project_isometric(coords)
        
        # Para 4D+, usamos cubos anidados
        # Los primeros 3 índices determinan la posición base en el cubo interior
        base_position = self.project_isometric(coords[:3])
        
        # Las dimensiones adicionales determinan el desplazamiento
        # Aseguramos que sea un array de flotantes
        direction = np.array([0.0, 0.0, 0.0])
        for i in range(3, n_dims):
            # Si el índice es 1, desplazamos en dirección positiva
            if coords[i] == 1:
                # Calculamos una dirección basada en la dimensión
                # Cada dimensión superior alterna entre desplazamientos
                displacement = (scale_factor ** (i - 2))
                if (i - 3) % 3 == 0:  # 4ᵃ, 7ᵃ, 10ᵃ dimensión
                    direction = direction + np.array([displacement, 0.0, 0.0])
                elif (i - 3) % 3 == 1:  # 5ᵃ, 8ᵃ, 11ᵃ dimensión
                    direction = direction + np.array([0.0, displacement, 0.0])
                else:  # 6ᵃ, 9ᵃ, 12ᵃ dimensión
                    direction = direction + np.array([0.0, 0.0, displacement])
        
        # La posición final es la base más el desplazamiento
        return base_position + direction * scale_factor
    
    def project_isometric(self, coords):
        """Proyección isométrica para 3D o menos"""
        if len(coords) == 0:
            return np.array([0, 0, 0])
        elif len(coords) == 1:
            return np.array([coords[0], 0, 0])
        elif len(coords) == 2:
            return np.array([coords[0], coords[1], 0])
        elif len(coords) == 3:
            # Proyección isométrica para 3D
            x, y, z = coords
            # Ajustamos ángulos para mejor visibilidad
            iso_x = x - 0.5*y
            iso_y = 0.5*x + y + z
            return np.array([iso_x, iso_y, 0])
        else:
            # No debería llegar aquí si se usa correctamente
            return np.zeros(3)
    
    def visualize_ncube(self, data):
        """Visualiza un n-cubo con valores en los vértices"""
        # Detectar la dimensión del array
        if np.isscalar(data):  # Caso 0D
            n_dims = 0
            shape = []
        else:
            n_dims = len(data.shape)
            shape = data.shape
        
        # Crear título
        title = Text(f"Visualización de {n_dims}-Cubo", font_size=36)
        self.play(Write(title))
        self.play(title.animate.to_edge(UP))
        
        # Caso especial para 0D (un solo punto)
        if n_dims == 0:
            value = float(data)
            point = Dot(point=ORIGIN, radius=0.2, color=self.value_to_color(value))
            label = Text(f"{value:.2f}", font_size=24).next_to(point, UP)
            
            self.play(Create(point), Write(label))
            return
        
        # Generar coordenadas de vértices según la dimensión
        if n_dims == 1:
            # Para 1D, usamos coordenadas [0] y [1] en el eje x
            vertex_coords = [(0,), (1,)]
        else:
            # Para dimensiones mayores, generamos todas las combinaciones de 0 y 1
            vertex_coords = list(itertools.product([0, 1], repeat=n_dims))
        
        # Calcular posiciones para los vértices
        vertex_positions = {}
        for coords in vertex_coords:
            # Proyectar según la dimensión
            if n_dims <= 3:
                pos = self.project_isometric(coords)
            else:
                pos = self.project_nested_cube(coords)
            
            # Escalar para mejor visualización
            scale_factor = 3 if n_dims <= 3 else 2.5
            pos = pos * scale_factor
            vertex_positions[coords] = pos
        
        # Crear vértices y etiquetas
        vertices = VGroup()
        value_labels = VGroup()
        coord_labels = VGroup()
        
        for coords in vertex_coords:
            position = vertex_positions[coords]
            
            # Obtener valor para este vértice
            try:
                if n_dims == 1:
                    value = float(data[coords[0]])
                else:
                    value = float(data[coords])
            except (IndexError, TypeError):
                value = 0
            
            # Crear vértice
            vertex = Dot(point=position, radius=0.15, color=self.value_to_color(value))
            vertices.add(vertex)
            
            # Añadir etiqueta con el valor
            value_label = Text(f"{value:.2f}", font_size=18).move_to(position + UP * 0.25)
            value_labels.add(value_label)
            
            # Añadir etiqueta con coordenadas dimensionales (usando letras)
            if n_dims > 1:
                coord_text = "".join([self.dim_to_letter(i) for i, v in enumerate(coords) if v == 1])
                if not coord_text:  # Si no hay ninguna dimensión en 1 (origen)
                    coord_text = "O"
                coord_label = Text(coord_text, font_size=16).move_to(position + DOWN * 0.25)
                coord_labels.add(coord_label)
        
        # Crear aristas entre vértices
        edges = VGroup()
        
        # No hay aristas para 0D, para 1D solo una arista
        if n_dims == 1:
            start = vertex_positions[(0,)]
            end = vertex_positions[(1,)]
            edge = Line(start, end, color=WHITE)
            edges.add(edge)
        else:
            # Para dimensiones mayores, conectar vértices que difieren en una coordenada
            for i, coords1 in enumerate(vertex_coords):
                for coords2 in vertex_coords[i+1:]:
                    # Calcular cuántos índices son diferentes
                    diff_count = sum(1 for a, b in zip(coords1, coords2) if a != b)
                    
                    # Conectar con arista si difieren en exactamente una coordenada
                    if diff_count == 1:
                        # Determinar qué dimensión cambió
                        dim_changed = next((i for i, (a, b) in enumerate(zip(coords1, coords2)) if a != b), None)
                        
                        # Crear arista con color basado en dimensión para ayudar a distinguir
                        start = vertex_positions[coords1]
                        end = vertex_positions[coords2]
                        
                        # Colores para aristas según dimensión
                        dim_colors = [RED, GREEN, BLUE, YELLOW, PURPLE, TEAL, ORANGE, MAROON]
                        edge_color = dim_colors[dim_changed % len(dim_colors)]
                        
                        edge = Line(start, end, color=edge_color, stroke_opacity=0.8)
                        edges.add(edge)
        
        # Añadir leyenda para dimensiones si son más de 1
        dim_labels = VGroup()
        if n_dims > 1:
            for d in range(n_dims):
                letter = self.dim_to_letter(d)
                dim_colors = [RED, GREEN, BLUE, YELLOW, PURPLE, TEAL, ORANGE, MAROON]
                color = dim_colors[d % len(dim_colors)]
                dim_label = Text(f"Dim {letter}", font_size=20, color=color).to_edge(LEFT).shift(UP * (2 - d * 0.4))
                dim_labels.add(dim_label)
        
        # Agrupar todo en un objeto para rotación
        cube_group = VGroup(edges, vertices, value_labels, coord_labels)
        
        # Añadir elementos a la escena
        self.play(Create(edges), run_time=1.5)
        self.play(Create(vertices), run_time=1)
        self.play(Write(value_labels), Write(coord_labels), run_time=1.5)
        if n_dims > 1:
            self.play(Write(dim_labels), run_time=1)
        
        # Añadir una leyenda de color-valor
        color_legend = self.create_color_legend()
        self.play(FadeIn(color_legend))
        
        # Rotar la visualización para 3D o más
        if n_dims >= 3:
            self.play(
                Rotate(cube_group, angle=PI/6, axis=RIGHT, about_point=ORIGIN),
                run_time=2
            )
            self.play(
                Rotate(cube_group, angle=PI/4, axis=UP, about_point=ORIGIN),
                run_time=2
            )
            self.play(
                Rotate(cube_group, angle=-PI/8, axis=RIGHT+UP, about_point=ORIGIN),
                run_time=2
            )
        
        # Esperar un momento
        self.wait(1)
    
    def create_color_legend(self):
        """Crea una leyenda para la escala de colores"""
        # Crear rectángulo para el gradiente
        gradient = Rectangle(height=0.3, width=3)
        
        # Crear gradiente manualmente con segmentos
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
        # Crear un hipercubo 5D (2x2x2x2x2)
        hypercube_data = np.zeros((2, 2, 2, 2, 2))
        
        # Llenar con valores basados en combinaciones de índices
        for indices in itertools.product([0, 1], repeat=5):
            # Valor basado en coordenadas (ejemplo: suma normalizada)
            hypercube_data[indices] = np.sum(indices) / 5
        
        # Visualizar
        self.visualize_ncube(hypercube_data)


# Para ejecutar:
# manim -pql ncube_visualizer.py NCubeVisualizer  # 0D a 4D
# manim -pql ncube_visualizer.py Hypercube5D      # 5D