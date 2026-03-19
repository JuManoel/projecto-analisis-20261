from manim import *
import numpy as np
import itertools

class NCubeVisualization(ThreeDScene):
    def construct(self):
        # Configuración de cámara y título
        self.set_camera_orientation(phi=70 * DEGREES, theta=30 * DEGREES)
        self.camera.frame_center = ORIGIN
        title = Text("Visualizador de N-Cubos", font_size=36)
        title.to_corner(UL)
        self.add_fixed_in_frame_mobjects(title)

        # Parámetro: número de dimensiones (usamos n=3 para un cubo)
        n = 3

        # Datos del NCube (ejemplo para un cubo 3D con arreglo de forma (2,2,2))
        ncube_data = np.array([[[0., 1.],
                                [1., 0.]],
                               [[0., 1.],
                                [1., 0.]]])

        # Generar los vértices: cada vértice es una combinación de 0s y 1s
        vertices = [np.array(vertex, dtype=float) for vertex in itertools.product([0, 1], repeat=n)]
        # Centramos los vértices en el origen (restamos 0.5 a cada coordenada)
        vertices = [vertex - 0.5 for vertex in vertices]

        # Crear una matriz de proyección de R^n a R^3
        if n == 3:
            P = np.eye(3)
        else:
            np.random.seed(0)
            random_matrix = np.random.randn(3, n)
            for i in range(3):
                random_matrix[i] /= np.linalg.norm(random_matrix[i])
            P = random_matrix

        # Proyectar los vértices a 3D
        projected_vertices = [np.dot(P, v) for v in vertices]

        # En lugar de puntos, colocar los valores del NCUBE en cada vértice.
        # Se crea un grupo con un fondo translúcido y un objeto de texto.
        vertex_mobjects = []
        for v in vertices:
            # Convertir coordenada a índice: -0.5 -> 0, 0.5 -> 1
            index = tuple(int(coord + 0.5) for coord in v)
            cube_value = ncube_data[index]
            proj = np.dot(P, v)

            # Fondo translúcido (círculo) para mejorar la legibilidad
            bg_circle = Circle(radius=0.15, color=WHITE, fill_color=BLACK, fill_opacity=0.2)
            bg_circle.set_flat(True)  # Siempre plano, mirando a la cámara
            bg_circle.move_to(proj)

            # Etiqueta con el valor del NCUBE
            value_text = Text(str(cube_value), font_size=24, color=WHITE)
            value_text.set_flat(True)
            value_text.move_to(proj)

            # Agrupar y añadir a la escena
            vertex_group = VGroup(bg_circle, value_text)
            vertex_mobjects.append(vertex_group)
            self.add(vertex_group)

        # Colores con tonalidades azuladas para cada dimensión (para cubo 3D)
        dimension_colors = [LOGO_BLUE, BLUE, TEAL]

        # Dibujar las aristas: conectar dos vértices que difieren en exactamente una coordenada
        for i, v1 in enumerate(vertices):
            for j, v2 in enumerate(vertices):
                if j <= i:
                    continue
                diff = np.abs(v1 - v2)
                if np.isclose(np.sum(diff), 1.0):
                    # Determinar la dimensión en la que difieren (0, 1 o 2)
                    dim = int(np.argmax(diff))
                    start = np.dot(P, v1)
                    end = np.dot(P, v2)
                    line = Line3D(start, end, color=dimension_colors[dim])
                    self.add(line)

        self.wait(2)
