from manim import *
import numpy as np

class Hipercubo(ThreeDScene):
    def construct(self):
        # Configuración de la escena 3D
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
        self.camera.frame_center = ORIGIN
        
        # Añadir título
        title = Text("Visualización del Hipercubo 4D", font_size=36)
        title.to_corner(UL)
        self.add_fixed_in_frame_mobjects(title)
        
        # Definir vértices del hipercubo 4D (representados en coordenadas 4D)
        vertices_4d = []
        for x in [-1, 1]:
            for y in [-1, 1]:
                for z in [-1, 1]:
                    for w in [-1, 1]:
                        vertices_4d.append([x, y, z, w])
        
        # Función para proyectar del 4D al 3D (proyección estereográfica modificada)
        # Usamos un factor w_factor más grande para evitar que las líneas converjan al centro
        def project_4d_to_3d(point_4d, w_factor=2.0):
            x, y, z, w = point_4d
            # Modificamos la fórmula para reducir la convergencia
            factor = 1 / (w_factor - w*0.5)
            return np.array([x * factor, y * factor, z * factor])
        
        # Proyectar vértices a 3D
        vertices_3d = [project_4d_to_3d(v) for v in vertices_4d]
        
        # Crear puntos para los vértices
        dots = VGroup(*[Dot3D(point=p, color=BLUE_B, radius=0.08) for p in vertices_3d])
        
        # Definir las aristas del hipercubo conectando vértices que difieren en una coordenada
        edges = []
        for i, v1 in enumerate(vertices_4d):
            for j, v2 in enumerate(vertices_4d):
                if i < j:  # Para evitar duplicados
                    diff = sum(1 for a, b in zip(v1, v2) if a != b)
                    if diff == 1:  # Conectar solo vértices que difieren en una coordenada
                        edges.append((i, j))
        
        # Crear líneas para las aristas con colores que varían según las coordenadas
        lines = VGroup()
        for i, j in edges:
            # Determinar qué coordenada cambia entre los dos vértices
            diff_index = next(idx for idx, (a, b) in enumerate(zip(vertices_4d[i], vertices_4d[j])) if a != b)
            # Asignar color según la coordenada que cambia
            colors = [RED_B, GREEN_B, BLUE_B, YELLOW_B]
            line = Line3D(
                vertices_3d[i], vertices_3d[j],
                color=colors[diff_index], thickness=0.03
            )
            lines.add(line)
        
        # Crear el hipercubo (vértices + aristas)
        hypercube = VGroup(lines, dots)
        
        # Añadir subtítulo con explicación
        subtitle = Text("Proyección 3D de un cubo 4-dimensional", font_size=24)
        subtitle.next_to(title, DOWN).align_to(title, LEFT)
        self.add_fixed_in_frame_mobjects(subtitle)
        
        # Color code legend
        legend_title = Text("Coordenadas:", font_size=20).to_corner(DR).shift(UP*1.5 + LEFT*0.5)
        self.add_fixed_in_frame_mobjects(legend_title)
        
        legend_items = VGroup()
        coord_names = ["X", "Y", "Z", "W"]
        colors = [RED_B, GREEN_B, BLUE_B, YELLOW_B]
        
        for i, (name, color) in enumerate(zip(coord_names, colors)):
            dot = Dot(color=color, radius=0.1)
            label = Text(name, font_size=16, color=color)
            item = VGroup(dot, label)
            label.next_to(dot, RIGHT, buff=0.1)
            legend_items.add(item)
        
        legend_items.arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        legend_items.next_to(legend_title, DOWN, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(legend_items)
        
        # Mostrar y animar
        self.play(Write(title), Write(subtitle), run_time=1)
        self.play(FadeIn(legend_title), FadeIn(legend_items), run_time=1)
        self.play(Create(lines), run_time=2)
        self.play(Create(dots), run_time=1)
        
        # Rotar para mejor visualización
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait(8)