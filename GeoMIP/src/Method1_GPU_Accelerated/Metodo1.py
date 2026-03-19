from itertools import combinations
from src.constants.base import NET_LABEL
from src.constants.models import GEOMETRIC_STRAREGY_TAG
from src.models.base.sia import SIA
from src.controllers.manager import Manager
from src.middlewares.slogger import SafeLogger
from src.middlewares.profile import profiler_manager
from src.funcs.base import emd_efecto, be_to_le_string, le_to_be_index
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict
from src.models.core.solution import Solution
from src.funcs.format import _create_binary_pattern, _convert_partition_indices

class Geometry(SIA):
    def __init__(self, config: Manager) -> None:
        super().__init__(config)
        profiler_manager.start_session(f"{NET_LABEL}{len(config.estado_inicial)}{config.pagina}")
        self.logger = SafeLogger(GEOMETRIC_STRAREGY_TAG)

    def aplicar_estrategia(
        self,
        condiciones: str,
        alcance: str,
        mecanismo: str,
        initial_state: str = None,
        tpm: np.ndarray | None = None,
    ):
        # print("inital estate", self.config.estado_inicial)
        self.sia_preparar_subsistema(condiciones, alcance, mecanismo, tpm)
        sistema = self.sia_subsistema

        self.alcance_indices = np.array([i for i, bit in enumerate(alcance) if bit == '1'], dtype=np.int32)
        self.mecanismo_indices = np.array([i for i, bit in enumerate(mecanismo) if bit == '1'], dtype=np.int32)

        num_mecanismo_vars = len(self.mecanismo_indices)
        num_alcance_vars = len(self.alcance_indices)

        if initial_state is None:
            initial_state = "1" + "0" * (num_mecanismo_vars - 1)
        elif len(initial_state) != num_mecanismo_vars:
            raise ValueError("Initial state length must match mechanism variables")

        self.initial_state = initial_state
        initial_state_index = le_to_be_index(initial_state)

        self.create_table_cost(num_mecanismo_vars, num_alcance_vars, sistema.ncubos, initial_state_index)

        self.num_mecanismo_vars = num_mecanismo_vars
        self.num_alcance_vars = num_alcance_vars
        self.cost_matrix = np.array(self.tabla_costos)
        total_vars = num_mecanismo_vars + num_alcance_vars


        # Estrategia adaptativa basada en el tamaño del sistema
        if total_vars <= 6:  # Sistema pequeño - búsqueda exhaustiva
            candidates = self.exhaustive_search()
        else:  # Sistema grande - heurísticas optimizadas
            candidates = self.find_optimal_bipartitions(total_vars)
        
        best_partition = self.process_partitions(candidates)

        return Solution(
            estrategia="Geometry",
            perdida=best_partition.get("emd", float('inf')) if best_partition else float('inf'),
            distribucion_subsistema=self.sia_dists_marginales,
            distribucion_particion=best_partition.get("distribution", self.sia_dists_marginales) if best_partition else self.sia_dists_marginales,
            tiempo_total=time.time() - self.sia_tiempo_inicio,
            particion=best_partition.get("pattern", "No valid partition found") if best_partition else "No valid partition found",
        )

    def create_table_cost(self, num_mecanismo_vars, num_alcance_vars, cubos, initial_state_index):
        """
        Construye la tabla de costos de transición para cada variable de alcance
            respecto a todos los posibles estados del mecanismo.

            Args:
                num_mecanismo_vars (int): Número de variables del mecanismo.
                num_alcance_vars (int): Número de variables del alcance.
                cubos: cubo con datos tensoriales.
                initial_state_index (int): Estado inicial.

            Resultado:
                Se asigna a self.tabla_costos una lista de arrays numpy,
                cada uno representando los costos de transición para una variable de alcance.
        """
    # Número total de estados posibles del mecanismo (2^n)
        num_states = 1 << num_mecanismo_vars

        # Vector con todos los posibles estados del mecanismo (0 a 2^n - 1)
        estados = np.arange(num_states, dtype=np.int64)

        # Máscaras de bits para calcular vecinos por Hamming
        bit_masks = np.array([1 << bit for bit in range(num_mecanismo_vars)], dtype=np.int64)

        # Reorganiza los datos tensoriales de cada cubo a arrays 1D
        cubos_data = np.array([cubo.data.reshape(-1) for cubo in cubos])

        # Calcula la tabla de costos en paralelo, una tarea por variable de alcance
        with ThreadPoolExecutor() as executor:
            self.tabla_costos = list(executor.map(
                lambda i: compute_costs_for_var(
                    i, cubos_data, num_mecanismo_vars, estados,
                    bit_masks, initial_state_index
                ),
                range(num_alcance_vars)
            ))
            
    def exhaustive_search(self) -> List[Dict]:
        """
        Realiza una búsqueda exhaustiva de biparticiones posibles en sistemas pequeños
        (cuando el número total de variables es ≤ 6).

        Returns:
            List[Dict]: Lista de diccionarios que representan las particiones evaluadas,
                        ordenadas por costo total (ascendente).
        """
        partitions = []

        # Caso 1: Considera todas las posibles particiones con un alcance fijo a la izquierda
        for alcance_var in range(self.num_alcance_vars):
            left_alcance = np.array([alcance_var], dtype=np.int32)
            right_alcance = np.array([i for i in range(self.num_alcance_vars) if i != alcance_var], dtype=np.int32)

            # Explora todas las combinaciones posibles de variables de mecanismo
            for r in range(self.num_mecanismo_vars + 1):
                for left_mec_combo in combinations(range(self.num_mecanismo_vars), r):
                    left_mecanismo = np.array(list(left_mec_combo), dtype=np.int32)
                    right_mecanismo = np.array(
                        [i for i in range(self.num_mecanismo_vars) if i not in left_mec_combo],
                        dtype=np.int32
                    )

                    # Calcula el costo asociado a esta partición
                    cost = self.calculate_partition_cost(
                        left_alcance, left_mecanismo, right_alcance, right_mecanismo
                    )

                    # Guarda la partición en la lista de candidatos
                    partitions.append({
                        "strategy": "exhaustive_alcance",
                        "left_alcance": left_alcance,
                        "left_mecanismo": left_mecanismo,
                        "right_alcance": right_alcance,
                        "right_mecanismo": right_mecanismo,
                        "total_cost": cost,
                    })

        # Caso 2: Considera particiones con un solo mecanismo fijo a la izquierda
        for mec_var in range(self.num_mecanismo_vars):
            left_mecanismo = np.array([mec_var], dtype=np.int32)
            right_mecanismo = np.array(
                [i for i in range(self.num_mecanismo_vars) if i != mec_var],
                dtype=np.int32
            )

            # Explora todas las combinaciones posibles de variables de alcance
            for r in range(self.num_alcance_vars + 1):
                for left_alc_combo in combinations(range(self.num_alcance_vars), r):
                    left_alcance = np.array(list(left_alc_combo), dtype=np.int32)
                    right_alcance = np.array(
                        [i for i in range(self.num_alcance_vars) if i not in left_alc_combo],
                        dtype=np.int32
                    )

                    cost = self.calculate_partition_cost(
                        left_alcance, left_mecanismo, right_alcance, right_mecanismo
                    )

                    partitions.append({
                        "strategy": "exhaustive_mecanismo",
                        "left_alcance": left_alcance,
                        "left_mecanismo": left_mecanismo,
                        "right_alcance": right_alcance,
                        "right_mecanismo": right_mecanismo,
                        "total_cost": cost,
                    })

        # Devuelve las 50 mejores particiones según el menor costo total
        return sorted(partitions, key=lambda x: x["total_cost"])[:50]

    def calculate_partition_cost(self, left_alcance, left_mecanismo, right_alcance, right_mecanismo) -> float:
        """
        Calcula el costo total asociado a una partición específica del sistema, 
        considerando las variables asignadas al lado izquierdo y derecho 
        del mecanismo y del alcance.

        Args:
            left_alcance (np.ndarray): Índices de las variables de alcance en el lado izquierdo.
            left_mecanismo (np.ndarray): Índices de las variables de mecanismo en el lado izquierdo.
            right_alcance (np.ndarray): Índices de las variables de alcance en el lado derecho.
            right_mecanismo (np.ndarray): Índices de las variables de mecanismo en el lado derecho.
        Returns:
            float: Costo total estimado de la partición. Si es inválida, devuelve infinito.
        """

        # Evita particiones vacías (ninguna variable en un lado)
        if len(left_alcance) == 0 and len(left_mecanismo) == 0:
            return float('inf')
        if len(right_alcance) == 0 and len(right_mecanismo) == 0:
            return float('inf')

        total_cost = 0.0
        used_states = set()

        # Recorre cada variable de alcance para buscar su estado más económico
        for var_idx in range(self.num_alcance_vars):
            # Lógica separada para cada lado de la partición
            if var_idx in left_alcance:
                best_cost = float('inf')
                best_state = None

                for state_idx in range(2 ** self.num_mecanismo_vars):
                    if state_idx in used_states:
                        continue

                    cost = self.cost_matrix[var_idx, state_idx]
                    if cost < best_cost:
                        best_cost = cost
                        best_state = state_idx

                if best_state is not None:
                    total_cost += best_cost
                    used_states.add(best_state)
                    # También se descarta el estado complementario
                    complement = self._find_complementary_state(best_state)
                    if complement is not None:
                        used_states.add(complement)

            else:  # Parte derecha del alcance
                best_cost = float('inf')
                best_state = None

                for state_idx in range(2 ** self.num_mecanismo_vars):
                    if state_idx in used_states:
                        continue

                    cost = self.cost_matrix[var_idx, state_idx]
                    if cost < best_cost:
                        best_cost = cost
                        best_state = state_idx

                if best_state is not None:
                    total_cost += best_cost
                    used_states.add(best_state)

        return total_cost


    def find_optimal_bipartitions(self, num_vars) -> List[Dict]:
        """
        Ejecuta múltiples estrategias de partición para encontrar biparticiones
        candidatas de bajo costo. Combina heurísticas y búsqueda directa.

        Args:
            num_vars (int): Número total de variables (alcance + mecanismo).

        Returns:
            List[Dict]: Lista ordenada de particiones candidatas con sus costos.
        """
        partitions = []

        # Estrategias principales
        partitions.extend(self.strategy1_partitions())
        partitions.extend(self.strategy2_partitions())

        # Solo aplica estrategia adicional si el sistema es pequeño
        if num_vars <= 6:
            partitions.extend(self.cost_based_partitions())

        # Ordena por menor costo total
        return sorted(partitions, key=lambda x: x["total_cost"])


    def strategy1_partitions(self) -> List[Dict]:
        """
        Estrategia 1: Genera particiones candidatas evaluando el costo de transición 
        desde el estado inicial hacia su complemento binario (todos los bits invertidos).

        Lógica:
        - Se recorre cada variable de alcance.
        - Para cada una, se evalúa el costo de transición hacia el estado complementario.
        - Se crea una partición con esa variable en el lado izquierdo, y el resto en el derecho.
        - El mecanismo se mantiene completo (sin dividir).

        Returns:
            List[Dict]: Lista de diccionarios, cada uno representa una partición candidata 
                        con la estructura necesaria para evaluación posterior.
        """
        partitions = []

        # Genera el estado complementario del estado inicial
        # Ej: si initial_state = "100", entonces complement_state = "011"
        complement_state = ''.join('0' if bit == '1' else '1' for bit in self.initial_state)
        complement_state_idx = le_to_be_index(complement_state)  # Se convierte a índice entero (big endian)

        # Recorre todas las variables de alcance
        for var_idx in range(self.num_alcance_vars):
            # Costo de transición desde el estado inicial hacia el complementario
            cost_to_complement = self.cost_matrix[var_idx, complement_state_idx]

            # Se crea una partición donde esta variable queda sola a la izquierda
            left_alcance = np.array([var_idx], dtype=np.int32)
            right_alcance = np.array(
                [i for i in range(self.num_alcance_vars) if i != var_idx], dtype=np.int32
            )

            # Se construye el diccionario de partición candidata
            partitions.append({
                "strategy": 1,
                "left_alcance": left_alcance,
                "left_mecanismo": np.array([], dtype=np.int32),  # Sin división del mecanismo
                "right_alcance": right_alcance,
                "right_mecanismo": self.mecanismo_indices.copy(),
                "total_cost": cost_to_complement,
            })

        return partitions


    def strategy2_partitions(self) -> List[Dict]:
        """
        Estrategia 2: Busca transiciones desde el estado inicial hacia estados que
        difieren en un solo bit (Hamming distance = 1). Evalúa el costo usando el estado
        complementario de esos candidatos para construir particiones del mecanismo.

        Returns:
            List[Dict]: Lista de particiones candidatas basadas en diferencias mínimas
                        con el estado inicial.
        """
        partitions = []
        initial_state_idx = le_to_be_index(self.initial_state)

        for state_idx in range(2 ** self.num_mecanismo_vars):
            if state_idx == initial_state_idx:
                continue

            state_str = be_to_le_string(state_idx, self.num_mecanismo_vars)
            same_bits = [i for i in range(self.num_mecanismo_vars) if self.initial_state[i] == state_str[i]]

            if len(same_bits) != 1:
                continue

            same_bit_idx = same_bits[0]
            complement_state_idx = self._find_complementary_state(state_idx)

            if complement_state_idx is not None:
                costs_complement = self.cost_matrix[:, complement_state_idx]
                total_cost = np.sum(costs_complement)

                right_mecanismo = np.array([i for i in range(len(self.mecanismo_indices)) if i != same_bit_idx], dtype=np.int32)
                left_mecanismo = np.array([same_bit_idx], dtype=np.int32)

                partitions.append({
                    "strategy": 2,
                    "left_alcance": np.array([], dtype=np.int32),
                    "left_mecanismo": left_mecanismo,
                    "right_alcance": np.arange(self.num_alcance_vars, dtype=np.int32),
                    "right_mecanismo": right_mecanismo,
                    "total_cost": total_cost,
                })

        return partitions
    
    def cost_based_partitions(self) -> List[Dict]:
        """
        Estrategia alternativa basada en el análisis directo de la matriz de costos.
        Agrupa variables de alcance que tienen estados con costos similares.

        Returns:
            List[Dict]: Lista de particiones basadas en valores promedio bajos de costo.
        """
        partitions = []
        
        # Analizar la matriz de costos para encontrar patrones
        for var_idx in range(self.num_alcance_vars):
            costs = self.cost_matrix[var_idx, :]
            
            # Encontrar variables con costos similares para agrupar
            min_cost = np.min(costs[costs > 0]) if np.any(costs > 0) else 0
            threshold = min_cost * 2  # Umbral para considerar costos similares
            
            low_cost_states = np.where(costs <= threshold)[0]
            
            if len(low_cost_states) > 1:
                # Crear partición agrupando variables con costos similares
                left_alcance = np.array([var_idx], dtype=np.int32)
                right_alcance = np.array([i for i in range(self.num_alcance_vars) if i != var_idx], dtype=np.int32)
                
                avg_cost = np.mean(costs[low_cost_states])
                
                partitions.append({
                    "strategy": "cost_based",
                    "left_alcance": left_alcance,
                    "left_mecanismo": np.array([], dtype=np.int32),
                    "right_alcance": right_alcance,
                    "right_mecanismo": self.mecanismo_indices.copy(),
                    "total_cost": avg_cost,
                })
        
        return partitions


    def process_partitions(self, partitions):
        """
        Evalúa todas las particiones candidatas calculando el EMD (Earth Mover's Distance)
        entre la distribución del subsistema original y la distribución inducida por la partición.

        Args:
            partitions (List[Dict]): Lista de particiones generadas por estrategias previas.

        Returns:
            Dict: Partición con menor pérdida de información (menor EMD), incluyendo el patrón y la distribución.
        """
        best_partition = None
        min_emd = float('inf')

        for candidate in partitions:
            dims_alcance = _convert_partition_indices(candidate['left_alcance'], self.alcance_indices)
            dims_mecanismo = _convert_partition_indices(candidate['left_mecanismo'], self.mecanismo_indices)

            try:
                particion = self.sia_subsistema.bipartir(
                    np.array(dims_alcance, dtype=np.int8),
                    np.array(dims_mecanismo, dtype=np.int8)
                )

                vector_marginal = particion.distribucion_marginal()
                emd = emd_efecto(vector_marginal, self.sia_dists_marginales)

                if abs(emd) < abs(min_emd):
                    min_emd = emd
                    left_top = _create_binary_pattern(candidate['left_alcance'], self.alcance_indices, upper=True)
                    left_bottom = _create_binary_pattern(candidate['left_mecanismo'], self.mecanismo_indices, upper=False)
                    right_top = _create_binary_pattern(candidate['right_alcance'], self.alcance_indices, upper=True)
                    right_bottom = _create_binary_pattern(candidate['right_mecanismo'], self.mecanismo_indices, upper=False)

                    pattern = f"({''.join(left_top)})({''.join(left_bottom)}) | ({''.join(right_top)})({''.join(right_bottom)})"

                    best_partition = {
                        **candidate,
                        "emd": emd,
                        "distribution": vector_marginal,
                        "pattern": pattern,
                        "dims_alcance": dims_alcance,
                        "dims_mecanismo": dims_mecanismo
                    }

            except Exception:
                continue

        return best_partition

    def _find_complementary_state(self, state_idx: int) -> int:
        state_str = be_to_le_string(state_idx, self.num_mecanismo_vars)
        complement_str = ''.join('0' if bit == '1' else '1' for bit in state_str)
        return le_to_be_index(complement_str)

# @njit
def compute_costs_for_var(idx_var, cubos_data, num_mecanismo_vars, estados, bit_masks, initial_state_index):
    tensor = cubos_data[idx_var]
    max_state = estados[-1]
    cost_array = np.zeros(max_state + 1, dtype=np.float64)
    cost_array[initial_state_index] = 0.0

    hamming_distances = np.zeros(len(estados), dtype=np.int64)
    gamma_values = np.zeros(len(estados), dtype=np.float64)

    for j in range(len(estados)):
        hamming_distances[j] = count_set_bits(initial_state_index ^ estados[j])
        gamma_values[j] = 2.0 ** (-hamming_distances[j])

    for distance in range(1, num_mecanismo_vars + 1):
        for j_idx in range(len(estados)):
            if hamming_distances[j_idx] != distance:
                continue

            j = estados[j_idx]
            sum_neighbors = 0.0

            for mask in bit_masks:
                neighbor = j ^ mask
                if neighbor < len(hamming_distances):
                    neighbor_distance = hamming_distances[neighbor]
                else:
                    neighbor_distance = count_set_bits(initial_state_index ^ neighbor)

                if neighbor_distance == distance - 1:
                    sum_neighbors += cost_array[neighbor]

            tensor_value_i = tensor[initial_state_index] if initial_state_index < len(tensor) else 0.0
            tensor_value_j = tensor[j] if j < len(tensor) else 0.0
            tensor_diff = abs(tensor_value_i - tensor_value_j)
            cost_array[j] = gamma_values[j_idx] * (tensor_diff + sum_neighbors)

    return cost_array


def count_set_bits(n):
    """
    Cuenta la cantidad de bits en '1' (set bits) en la representación binaria
    de un número entero.

    Utiliza el algoritmo de Brian Kernighan, que elimina el bit menos significativo
    en cada iteración, logrando una complejidad O(k), donde k es el número de bits en 1.

    Args:
        n (int): Número entero no negativo.

    Returns:
        int: Número de bits establecidos en 1 en la representación binaria de 'n'.

    Ejemplo:
        count_set_bits(13)  # binario: 1101 → retorna 3
    """

    count = 0
    while n:
        n &= n - 1
        count += 1
    return count
