from manim import *
import numpy as np
import csv

class NCubeVisualization(ThreeDScene):
    def construct(self):
        # Configuración de la escena 3D
        self.set_camera_orientation(phi=70 * DEGREES, theta=30 * DEGREES)
        self.camera.frame_center = ORIGIN
        
        # Añadir título
        title = Text("Transformación de N-Cubos", font_size=36)
        title.to_corner(UL)
        self.add_fixed_in_frame_mobjects(title)
        
        # Datos del NCube (ejemplo del sistema proporcionado)
        # Para el NCube(index=2) del ejemplo
        ncube_data_initial = np.array([
            [[[0., 1.],
              [1., 0.]]],
            [[[0., 1.],
              [1., 0.]]]
        ])
        
        # Una transformación hipotética del NCube
        ncube_data_transformed = np.array([
            [[[0.2, 0.8],
              [0.7, 0.3]]],
            [[[0.1, 0.9],
              [0.6, 0.4]]]
        ])
        
        # Crear y mostrar el primer cubo
        first_cube = self.create_cube_with_data(ncube_data_initial, position=LEFT*3)
        first_cube_label = Text("NCube Original", font_size=24)
        first_cube_label.next_to(first_cube, DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(first_cube_label)
        
        # Crear y mostrar el segundo cubo (transformado)
        second_cube = self.create_cube_with_data(ncube_data_transformed, position=RIGHT*3)
        second_cube_label = Text("NCube Transformado", font_size=24)
        second_cube_label.next_to(second_cube, DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(second_cube_label)
        
        # Animación
        self.play(Write(title), run_time=1)
        self.play(FadeIn(first_cube_label), FadeIn(second_cube_label), run_time=1)
        
        # Mostrar el primer cubo
        self.play(Create(first_cube), run_time=2)
        
        # Mostrar la transformación (animación de morfismo entre cubos)
        transform_arrow = Arrow(LEFT*1.5, RIGHT*1.5, buff=0.5, color=YELLOW)
        transform_text = Text("Transformación", font_size=20)
        transform_text.next_to(transform_arrow, UP, buff=0.2)
        self.add_fixed_in_frame_mobjects(transform_arrow, transform_text)
        
        self.play(Create(transform_arrow), Write(transform_text), run_time=1)
        self.play(Create(second_cube), run_time=2)
        
        # Rotar para mejor visualización
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait(5)
        
    def create_cube_with_data(self, data, position=ORIGIN):
        """Crea un cubo 3D con valores en los vértices según los datos proporcionados"""
        # Vértices del cubo (coordenadas 3D)
        vertices = []
        for x in [0, 1]:
            for y in [0, 1]:
                for z in [0, 1]:
                    vertices.append([x, y, z])
        
        # Convertir a coordenadas 3D para Manim (escaladas y centradas)
        vertices_3d = [np.array([v[0], v[1], v[2]]) * 2 - np.array([1, 1, 1]) for v in vertices]
        
        # Grupo para almacenar todos los elementos del cubo
        cube_group = VGroup()
        
        # Crear puntos para los vértices con colores según los valores
        dots = []
        values = []
        for i, v in enumerate(vertices):
            # Extraer el valor del array de datos
            x, y, z = v
            value = float(data[x, y, z])
            values.append(value)
            
            # Color basado en el valor (de azul a rojo)
            color = self.get_color_from_value(value)
            
            # Posición 3D
            pos = vertices_3d[i] + position
            
            # Crear el punto y su etiqueta
            dot = Sphere(radius=0.1, color=color).move_to(pos)
            value_label = Text(f"{value:.1f}", font_size=16).move_to(pos + UP*0.3 + RIGHT*0.3)
            self.add_fixed_in_frame_mobjects(value_label)
            
            dots.append(dot)
            cube_group.add(dot, value_label)
        
        # Definir las aristas del cubo
        edges = []
        for i, v1 in enumerate(vertices):
            for j, v2 in enumerate(vertices):
                if i < j:  # Para evitar duplicados
                    # Contar diferencias en coordenadas
                    diff = sum(1 for a, b in zip(v1, v2) if a != b)
                    if diff == 1:  # Conectar solo vértices adyacentes (que difieren en una coordenada)
                        edges.append((i, j))
        
        # Crear líneas para las aristas
        for i, j in edges:
            # Gradient color based on vertex values
            start_color = self.get_color_from_value(values[i])
            end_color = self.get_color_from_value(values[j])
            
            line = Line3D(
                vertices_3d[i] + position, 
                vertices_3d[j] + position,
                color=start_color,
                thickness=0.03
            )
            cube_group.add(line)
        
        return cube_group
    
    def get_color_from_value(self, value):
        """Devuelve un color en función del valor (0 -> azul, 1 -> rojo)"""
        return interpolate_color(BLUE, RED, value)


class NCubeDataVisualization(ThreeDScene):
    def construct(self):
        """Visualización de N-Cubos con los datos del sistema proporcionado"""
        # Configuración de la escena 3D
        self.set_camera_orientation(phi=70 * DEGREES, theta=30 * DEGREES)
        self.camera.frame_center = ORIGIN
        
        # Añadir título
        title = Text("Sistema de N-Cubos", font_size=36)
        title.to_corner(UL)
        self.add_fixed_in_frame_mobjects(title)
        
        # Datos de los tres NCubes del sistema de ejemplo
        ncube0_data = np.array([
            [[[0., 0.],
              [1., 1.]]],
            [[[1., 1.],
              [1., 1.]]]
        ])
        
        ncube1_data = np.array([
            [[[0., 0.],
              [0., 0.]]],
            [[[0., 1.],
              [0., 1.]]]
        ])
        
        ncube2_data = np.array([
            [[[0., 1.],
              [1., 0.]]],
            [[[0., 1.],
              [1., 0.]]]
        ])
        
        # Crear los tres cubos
        cube0 = self.create_cube_with_data(ncube0_data, position=LEFT*4)
        cube1 = self.create_cube_with_data(ncube1_data, position=ORIGIN)
        cube2 = self.create_cube_with_data(ncube2_data, position=RIGHT*4)
        
        # Etiquetas para los cubos
        cube0_label = Text("NCube 0", font_size=24)
        cube0_label.next_to(cube0, DOWN, buff=0.5)
        
        cube1_label = Text("NCube 1", font_size=24)
        cube1_label.next_to(cube1, DOWN, buff=0.5)
        
        cube2_label = Text("NCube 2", font_size=24)
        cube2_label.next_to(cube2, DOWN, buff=0.5)
        
        self.add_fixed_in_frame_mobjects(cube0_label, cube1_label, cube2_label)
        
        # Añadir leyenda de colores
        legend_title = Text("Valores:", font_size=20).to_corner(DR).shift(UP*2 + LEFT*1)
        self.add_fixed_in_frame_mobjects(legend_title)
        
        legend_items = VGroup()
        values = [0.0, 0.25, 0.5, 0.75, 1.0]
        
        for value in values:
            color = self.get_color_from_value(value)
            dot = Dot(color=color, radius=0.1)
            label = Text(f"{value:.2f}", font_size=16)
            item = VGroup(dot, label)
            label.next_to(dot, RIGHT, buff=0.2)
            legend_items.add(item)
        
        legend_items.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        legend_items.next_to(legend_title, DOWN, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(legend_items)
        
        # Animación
        self.play(Write(title), FadeIn(legend_title), FadeIn(legend_items), run_time=1)
        
        # Mostrar los cubos secuencialmente
        self.play(
            Create(cube0), FadeIn(cube0_label),
            run_time=1.5
        )
        self.play(
            Create(cube1), FadeIn(cube1_label),
            run_time=1.5
        )
        self.play(
            Create(cube2), FadeIn(cube2_label),
            run_time=1.5
        )
        
        # Rotar para mejor visualización
        self.begin_ambient_camera_rotation(rate=0.08)
        self.wait(7)
        
    def create_cube_with_data(self, data, position=ORIGIN):
        """Crea un cubo 3D con valores en los vértices según los datos proporcionados"""
        # Vértices del cubo (coordenadas 3D)
        vertices = []
        for x in [0, 1]:
            for y in [0, 1]:
                for z in [0, 1]:
                    vertices.append([x, y, z])
        
        # Convertir a coordenadas 3D para Manim (escaladas y centradas)
        vertices_3d = [np.array([v[0], v[1], v[2]]) * 2 - np.array([1, 1, 1]) for v in vertices]
        
        # Grupo para almacenar todos los elementos del cubo
        cube_group = VGroup()
        
        # Crear puntos para los vértices con colores según los valores
        dots = []
        values = []
        for i, v in enumerate(vertices):
            # Extraer el valor del array de datos
            x, y, z = v
            value = float(data[x, y, z])
            values.append(value)
            
            # Color basado en el valor (de azul a rojo)
            color = self.get_color_from_value(value)
            
            # Posición 3D
            pos = vertices_3d[i] + position
            
            # Crear el punto y su etiqueta
            dot = Sphere(radius=0.15, color=color).move_to(pos)
            value_label = Text(f"{value:.1f}", font_size=16).move_to(pos + UP*0.3 + RIGHT*0.3)
            self.add_fixed_in_frame_mobjects(value_label)
            
            dots.append(dot)
            cube_group.add(dot, value_label)
        
        # Definir las aristas del cubo
        edges = []
        for i, v1 in enumerate(vertices):
            for j, v2 in enumerate(vertices):
                if i < j:  # Para evitar duplicados
                    # Contar diferencias en coordenadas
                    diff = sum(1 for a, b in zip(v1, v2) if a != b)
                    if diff == 1:  # Conectar solo vértices adyacentes (que difieren en una coordenada)
                        edges.append((i, j))
        
        # Crear líneas para las aristas
        for i, j in edges:
            # Color basado en el promedio de los valores de los vértices
            color = self.get_color_from_value((values[i] + values[j])/2)
            
            line = Line3D(
                vertices_3d[i] + position, 
                vertices_3d[j] + position,
                color=color,
                thickness=0.03
            )
            cube_group.add(line)
        
        return cube_group
    
    def get_color_from_value(self, value):
        """Devuelve un color en función del valor (0 -> azul, 1 -> rojo)"""
        return interpolate_color(BLUE, RED, value)


class NCubeTransformationAnimation(ThreeDScene):
    def construct(self):
        """Animación de la transformación de un N-Cubo"""
        # Configuración de la escena 3D
        self.set_camera_orientation(phi=70 * DEGREES, theta=30 * DEGREES)
        self.camera.frame_center = ORIGIN
        
        # Añadir título
        title = Text("Transformación de N-Cubo a través del tiempo", font_size=36)
        title.to_corner(UL)
        self.add_fixed_in_frame_mobjects(title)
        
        # Datos para la animación de transformación
        # Estado inicial del NCube
        initial_data = np.array([
            [[[0., 1.],
              [1., 0.]]],
            [[[0., 1.],
              [1., 0.]]]
        ])
        
        # Varios estados intermedios para la animación
        states = [
            initial_data,  # Estado inicial
            np.array([  # Estado intermedio 1
                [[[0.1, 0.9],
                  [0.9, 0.1]]],
                [[[0.1, 0.9],
                  [0.9, 0.1]]]
            ]),
            np.array([  # Estado intermedio 2
                [[[0.3, 0.7],
                  [0.7, 0.3]]],
                [[[0.3, 0.7],
                  [0.7, 0.3]]]
            ]),
            np.array([  # Estado final
                [[[0.5, 0.5],
                  [0.5, 0.5]]],
                [[[0.5, 0.5],
                  [0.5, 0.5]]]
            ])
        ]
        
        # Subtítulo con explicación
        subtitle = Text("Evolución temporal de los valores en los vértices", font_size=24)
        subtitle.next_to(title, DOWN).align_to(title, LEFT)
        self.add_fixed_in_frame_mobjects(subtitle)
        
        # Leyenda de colores
        legend_title = Text("Valores:", font_size=20).to_corner(DR).shift(UP*2 + LEFT*1)
        self.add_fixed_in_frame_mobjects(legend_title)
        
        legend_items = VGroup()
        values = [0.0, 0.25, 0.5, 0.75, 1.0]
        
        for value in values:
            color = self.get_color_from_value(value)
            dot = Dot(color=color, radius=0.1)
            label = Text(f"{value:.2f}", font_size=16)
            item = VGroup(dot, label)
            label.next_to(dot, RIGHT, buff=0.2)
            legend_items.add(item)
        
        legend_items.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        legend_items.next_to(legend_title, DOWN, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(legend_items)
        
        # Crear el cubo inicial
        cube = self.create_cube_with_data(initial_data)
        
        # Estado de tiempo
        time_label = Text("t = 0", font_size=30)
        time_label.to_corner(UR).shift(DOWN + LEFT)
        self.add_fixed_in_frame_mobjects(time_label)
        
        # Animación inicial
        self.play(
            Write(title), 
            Write(subtitle),
            FadeIn(legend_title), 
            FadeIn(legend_items),
            Create(cube),
            Write(time_label),
            run_time=2
        )
        
        # Rotar para mejor visualización
        self.begin_ambient_camera_rotation(rate=0.05)
        self.wait(1)
        
        # Animación de la transformación a través de los estados
        for i, state_data in enumerate(states[1:], 1):
            # Actualizar etiqueta de tiempo
            new_time_label = Text(f"t = {i}", font_size=30)
            new_time_label.to_corner(UR).shift(DOWN + LEFT)
            
            # Crear el nuevo cubo con los datos actualizados
            new_cube = self.create_cube_with_data(state_data)
            
            # Animar la transformación
            self.play(
                Transform(cube, new_cube),
                Transform(time_label, new_time_label),
                run_time=2
            )
            
            self.wait(1)
        
        # Esperar un poco más al final
        self.wait(3)
    
    def create_cube_with_data(self, data, position=ORIGIN):
        """Crea un cubo 3D con valores en los vértices según los datos proporcionados"""
        # Vértices del cubo (coordenadas 3D)
        vertices = []
        for x in [0, 1]:
            for y in [0, 1]:
                for z in [0, 1]:
                    vertices.append([x, y, z])
        
        # Convertir a coordenadas 3D para Manim (escaladas y centradas)
        vertices_3d = [np.array([v[0], v[1], v[2]]) * 2 - np.array([1, 1, 1]) for v in vertices]
        
        # Grupo para almacenar todos los elementos del cubo
        cube_group = VGroup()
        
        # Crear puntos para los vértices con colores según los valores
        dots = []
        values_text = []
        values = []
        
        for i, v in enumerate(vertices):
            # Extraer el valor del array de datos
            x, y, z = v
            value = float(data[x, y, z])
            values.append(value)
            
            # Color basado en el valor (de azul a rojo)
            color = self.get_color_from_value(value)
            
            # Posición 3D
            pos = vertices_3d[i] + position
            
            # Crear el punto
            dot = Sphere(radius=0.2, color=color).move_to(pos)
            dots.append(dot)
            cube_group.add(dot)
            
            # Crear la etiqueta del valor
            value_text = Text(f"{value:.1f}", font_size=16).move_to(pos + UP*0.3 + RIGHT*0.3)
            values_text.append(value_text)
            self.add_fixed_in_frame_mobjects(value_text)
        
        # Añadir las etiquetas al grupo después de crear todos los vértices para evitar problemas de renderizado
        for text in values_text:
            cube_group.add(text)
        
        # Definir las aristas del cubo
        edges = []
        for i, v1 in enumerate(vertices):
            for j, v2 in enumerate(vertices):
                if i < j:  # Para evitar duplicados
                    # Contar diferencias en coordenadas
                    diff = sum(1 for a, b in zip(v1, v2) if a != b)
                    if diff == 1:  # Conectar solo vértices adyacentes (que difieren en una coordenada)
                        edges.append((i, j))
        
        # Crear líneas para las aristas
        for i, j in edges:
            # Color basado en el promedio de los valores de los vértices
            color = self.get_color_from_value((values[i] + values[j])/2)
            
            line = Line3D(
                vertices_3d[i] + position, 
                vertices_3d[j] + position,
                color=color,
                thickness=0.03
            )
            cube_group.add(line)
        
        return cube_group
    
    def get_color_from_value(self, value):
        """Devuelve un color en función del valor (0 -> azul, 1 -> rojo)"""
        return interpolate_color(BLUE, RED, value)