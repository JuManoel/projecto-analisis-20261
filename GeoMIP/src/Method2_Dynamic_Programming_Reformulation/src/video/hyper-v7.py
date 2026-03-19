from manim import *
import numpy as np
import itertools

class NCubeVisualizer(ThreeDScene):
    def construct(self):
        # Configuración de la cámara 3D
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        
        # Crear un hipercubo 4D (2x2x2x2)
        hypercube_data = np.zeros((2, 2, 2, 2))
        for indices in itertools.product([0, 1], repeat=4):
            hypercube_data[indices] = np.sum(indices) / 4
        
        # Título general
        title = Text("Reducción Dimensional con np.mean", font_size=36)
        title.to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title))
        
        # Crear un subtítulo para la dimensión actual
        subtitle = Text("Teseracto (4D)", font_size=28)
        subtitle.next_to(title, DOWN)
        self.add_fixed_in_frame_mobjects(subtitle)
        self.play(Write(subtitle))
        
        # Visualizar el teseracto (4D)
        cube4d_group = self.visualize_ncube(hypercube_data)
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(3)
        self.stop_ambient_camera_rotation()
        
        # Aplicar np.mean para reducir dimensiones consecutivamente
        dimensions = 4
        for dim in range(dimensions-1, -1, -1):
            # Aplicar np.mean en la dimensión actual
            reduced_data = np.mean(hypercube_data, axis=dim)
            
            # Actualizar el subtítulo
            new_dim_name = ""
            if dim == 3:
                new_dim_name = "Cubo (3D)"
            elif dim == 2:
                new_dim_name = "Cuadrado (2D)"
            elif dim == 1:
                new_dim_name = "Línea (1D)"
            elif dim == 0:
                new_dim_name = "Punto (0D)"
                
            new_subtitle = Text(f"{new_dim_name}", font_size=28)
            new_subtitle.next_to(title, DOWN)
            self.add_fixed_in_frame_mobjects(new_subtitle)
            
            # Mostrar la fórmula de reducción
            formula = MathTex(r"\text{np.mean(data, axis=", f"{dim}", r")}")
            formula.scale(0.8)
            formula.to_corner(UL).shift(DOWN * 0.5 + RIGHT * 1.0)
            self.add_fixed_in_frame_mobjects(formula)
            
            # Visualizar la estructura reducida
            self.play(
                FadeOut(subtitle),
                FadeIn(new_subtitle),
                FadeIn(formula)
            )
            subtitle = new_subtitle
            
            # Crear la nueva visualización
            new_group = self.visualize_ncube(reduced_data, animate=False)
            
            # Transición entre visualizaciones
            self.play(
                FadeOut(cube4d_group),
                run_time=1
            )
            self.play(
                FadeIn(new_group),
                run_time=1
            )
            
            # Actualizar referencia y permitir exploración
            cube4d_group = new_group
            
            # Ajustar la cámara para cada dimensión
            if dimensions - dim == 2:  # 3D -> 2D
                self.play(
                    self.camera.animate.set_phi(75 * DEGREES),
                    self.camera.animate.set_theta(0 * DEGREES),
                    run_time=1
                )
            elif dimensions - dim == 3:  # 2D -> 1D
                self.play(
                    self.camera.animate.set_phi(0 * DEGREES),
                    self.camera.animate.set_theta(0 * DEGREES),
                    run_time=1
                )
            
            # Rotación breve para hipercubo, cubo y cuadrado
            if dimensions - dim <= 2:
                self.begin_ambient_camera_rotation(rate=0.15)
                self.wait(3)
                self.stop_ambient_camera_rotation()
            else:
                self.wait(2)
            
            # Limpiar la fórmula para la siguiente iteración
            self.play(FadeOut(formula))
            
            # Actualizar el array para la siguiente reducción
            hypercube_data = reduced_data
    
    def dim_to_letter(self, dim):
        """Convierte un número de dimensión a su letra correspondiente (0->A, 1->B, etc.)"""
        return chr(65 + dim)  # 65 es el código ASCII para 'A'
    
    def visualize_ncube(self, data, animate=True):
        """Visualiza un n-cubo con valores en los vértices y devuelve el grupo resultante"""
        # Detectar la dimensión del array
        if np.isscalar(data):  # Caso 0D
            n_dims = 0
        else:
            n_dims = len(data.shape)
        
        # Generar coordenadas de vértices según la dimensión
        if n_dims <= 1:
            # Casos especiales de 0D y 1D
            if n_dims == 0:
                # 0D: un solo punto
                value = float(data)
                vertex = Sphere(radius=0.2, resolution=(15, 15))
                vertex.set_color(self.value_to_color(value))
                
                # Etiqueta de valor
                value_text = DecimalNumber(value, num_decimal_places=2, font_size=24)
                value_text.next_to(vertex, UP, buff=0.2)
                self.add_fixed_orientation_mobjects(value_text)
                
                # Agrupar todo
                result_group = VGroup(vertex)
                
                if animate:
                    self.play(Create(vertex), Write(value_text), run_time=1.5)
                    
                return result_group
            else:
                # 1D: línea con dos puntos
                vertex_coords = [(0,), (1,)]
        else:
            # Para dimensiones mayores, generamos todas las combinaciones de 0 y 1
            vertex_coords = list(itertools.product([0, 1], repeat=n_dims))
        
        # Crear vértices y aristas
        vertices = VGroup()
        edges = VGroup()
        labels = VGroup()
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
            value_text.move_to(position + UP * 0.2)
            labels.add(value_text)
            self.add_fixed_orientation_mobjects(value_text)
            
            # Crear etiqueta de coordenadas usando letras
            if n_dims > 1:
                coord_text = "".join([self.dim_to_letter(i) for i, v in enumerate(coords) if v == 1])
                if not coord_text:  # Origen
                    coord_text = "O"
                    
                coord_label = Text(coord_text, font_size=16)
                coord_label.move_to(position + DOWN * 0.2)
                labels.add(coord_label)
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
        
        # Agrupar todo (excepto las etiquetas fijas al marco)
        result_group = VGroup(vertices, edges)
        
        # Animar la creación si se solicita
        if animate:
            self.play(Create(edges), run_time=1.5)
            self.play(Create(vertices), run_time=1)
            if n_dims > 1:
                self.play(Write(dim_labels), run_time=0.8)
            self.play(FadeIn(color_legend), run_time=0.8)
        
        return result_group
    
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


class DimensionalReduction(NCubeVisualizer):
    def construct(self):
        # Configuración de la cámara 3D
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        
        # Crear un hipercubo 4D (2x2x2x2)
        hypercube_data = np.zeros((2, 2, 2, 2))
        for indices in itertools.product([0, 1], repeat=4):
            hypercube_data[indices] = np.sum(indices) / 4
        
        # Título general
        title = Text("Reducción Dimensional con np.mean", font_size=36)
        title.to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title))
        
        # Visualizar el teseracto (4D) y mostrar la secuencia de reducción
        self.visualize_reduction_sequence(hypercube_data)
    
    def visualize_reduction_sequence(self, data):
        """Visualiza una secuencia de reducciones dimensionales mediante np.mean"""
        current_data = data
        dimensions = len(current_data.shape)
        
        # Crear subtítulo para la dimensión inicial
        dimension_names = ["Punto (0D)", "Línea (1D)", "Cuadrado (2D)", "Cubo (3D)", "Teseracto (4D)", "Hipercubo 5D"]
        subtitle = Text(dimension_names[dimensions], font_size=28)
        subtitle.next_to(self.get_top_edge(), DOWN)
        self.add_fixed_in_frame_mobjects(subtitle)
        self.play(Write(subtitle))
        
        # Visualizar la estructura inicial
        current_group = self.visualize_ncube(current_data)
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(3)
        self.stop_ambient_camera_rotation()
        
        # Para cada dimensión, reducir y visualizar
        for dim in range(dimensions-1, -1, -1):
            # Calcular la nueva estructura reducida
            reduced_data = np.mean(current_data, axis=dim)
            
            # Actualizar subtítulo
            new_subtitle = Text(dimension_names[dimensions-dim-1], font_size=28)
            new_subtitle.next_to(self.get_top_edge(), DOWN)
            self.add_fixed_in_frame_mobjects(new_subtitle)
            
            # Mostrar la fórmula de reducción
            formula = MathTex(r"\text{np.mean(data, axis=", f"{dim}", r")}")
            formula.scale(0.8)
            formula.to_corner(UL).shift(DOWN * 0.5 + RIGHT * 1.0)
            self.add_fixed_in_frame_mobjects(formula)
            
            # Transición entre subtítulos y mostrar fórmula
            self.play(
                FadeOut(subtitle),
                FadeIn(new_subtitle),
                FadeIn(formula)
            )
            subtitle = new_subtitle
            
            # Crear nueva visualización
            new_group = self.visualize_ncube(reduced_data, animate=False)
            
            # Transición entre visualizaciones
            self.play(
                FadeOut(current_group),
                run_time=1
            )
            self.play(
                FadeIn(new_group),
                run_time=1
            )
            current_group = new_group
            
            # Ajustar cámara según la dimensión - usando método más compatible
            if dim == 3:  # 4D -> 3D (mantener rotación 3D)
                pass
            elif dim == 2:  # 3D -> 2D (vista frontal del plano)
                self.move_camera(phi=90 * DEGREES, theta=0 * DEGREES, run_time=1)
            elif dim == 1:  # 2D -> 1D (vista lateral de la línea)
                self.move_camera(phi=0 * DEGREES, theta=90 * DEGREES, run_time=1)
            
            # Rotación para estructuras 3D+
            if dimensions - dim - 1 >= 3:
                self.begin_ambient_camera_rotation(rate=0.15)
                self.wait(3)
                self.stop_ambient_camera_rotation()
            else:
                self.wait(2)
            
            # Limpiar fórmula
            self.play(FadeOut(formula))
            
            # Actualizar datos para la siguiente reducción
            current_data = reduced_data
        
        # Mensaje final
        final_message = Text("Reducción completa: 4D → 0D", font_size=32)
        final_message.to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(final_message)
        self.play(Write(final_message))
        self.wait(2)

    def get_top_edge(self):
        return np.array([0, 3.5, 0])


# Para ejecutar la visualización con reducción dimensional:
# manim -pql ncube_visualizer.py DimensionalReduction