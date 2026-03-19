import heapq
from src.constants.error import ERROR_INCOMPATIBLE_SIZES
from src.models.core.system import System
from src.constants.base import NET_LABEL, STR_ZERO
from src.funcs.base import ABECEDARY
from src.middlewares.slogger import SafeLogger
from src.funcs.base import emd_efecto
from src.models.base.sia import SIA
from src.constants.base import (
    ACTUAL,
    EFECTO,
    TYPE_TAG,
)
from src.constants.models import (
    GEOMETRIC_ANALYSIS_TAG,
    GEOMETRIC_LABEL,
    GEOMETRIC_STRAREGY_TAG,
)
from src.controllers.manager import Manager
from src.funcs.format import fmt_biparte_q
from src.middlewares.profile import profiler_manager, profile
from src.models.core.solution import Solution
import numpy as np
import time
from typing import List, Dict, Tuple

from concurrent.futures import ThreadPoolExecutor
import itertools

class GeometricSIA(SIA):
    def __init__(self, gestor: Manager):
        super().__init__(gestor)
        profiler_manager.start_session(
            f"{NET_LABEL}{len(gestor.estado_inicial)}{gestor.pagina}"
        )
        self.etiquetas = [tuple(s.lower() for s in ABECEDARY), ABECEDARY]
        self.logger = SafeLogger(GEOMETRIC_STRAREGY_TAG)
        self.tabla_transiciones: dict ={}
        self.vertices :set[tuple]
        self.tabla :dict[int, list[tuple[int, int]]] = {}
        self.memoria_particiones: dict[tuple[int, int], tuple[float, float]] = {}

    @profile(context={TYPE_TAG: GEOMETRIC_ANALYSIS_TAG})
    def aplicar_estrategia(
        self,
        condicion: str,
        alcance: str,
        mecanismo: str,
        tpm: np.ndarray #! COMENTAR PARA UN SOLO ESTADO INICIAL
    ):
        """ vamos a hacer que vaya desde el estado inicial hasta el final, bit a bit diferente, llenando la tabla primero para distancias hamming 1 hasta n, con n la cantidad de bits que cambian del estado inicial al final. para esto podemos usar una tabla de transiciones, donde cada fila es un estado y cada columna es un bit. la tabla de transiciones se llena con los estados que se pueden alcanzar desde el estado inicial, y luego se va llenando la tabla de distancias hamming. para esto vamos a usar una lista de listas, donde cada lista es una fila de la tabla de transiciones. la primera fila es el estado inicial, y las siguientes filas son los estados alcanzables desde el estado inicial. la última fila es el estado final.
        paso a paso
        1. cargar la matriz, pasar a ncubos
        2. condicionar
        3. obtener los bits que cambian entre el estado inicial y el final
        4. obener vecinos del estado final que van hacia el estado inicial y calcular el costo de la transicion.
        5. para cada vecino, obtener los vecinos que van hacia el estado inicial y calcular el costo de la transicion.
        6. repetir hasta llegar al estado inicial.


        nota: intentar llenar la tabla desde el estado final hacia atras, pues al contrario habra dependencia de los valores de la tabla de los estados que van en camino hacia el estado final
        """
        self.sia_preparar_subsistema(condicion, alcance, mecanismo, tpm) #! COMENTAR PARA UN SOLO ESTADO INICIAL
        # self.sia_preparar_subsistema(condicion, alcance, mecanismo) #! DESCOMENTAR PARA UN SOLO ESTADO INICIAL

        futuro = tuple(
            (EFECTO, efecto) for efecto in self.sia_subsistema.indices_ncubos
        )
        presente = tuple(
            (ACTUAL, actual) for actual in self.sia_subsistema.dims_ncubos
        )


        self._flat_data = []
        for idx, ncubo in enumerate(self.sia_subsistema.ncubos):
            # garantías: ncubo.data.shape == (2,2,...,2)
            # np.ravel() lo aplana. El orden ‘C’ equivale 
            # a little-endian si tus tuples están invertidas.
            self._flat_data.append(ncubo.data.ravel())

        self.vertices = set(presente + futuro)
        dims = self.sia_subsistema.dims_ncubos
        self.estado_inicial = self.sia_subsistema.estado_inicial[dims]
        self.estado_final = 1 - self.estado_inicial
        mip = self.find_mip()
        # print(mip)
        fmt_mip = fmt_biparte_q(list(mip), self.nodes_complement(mip))

        return Solution(
            estrategia= GEOMETRIC_LABEL,
            perdida=self.memoria_particiones[mip][0],
            distribucion_subsistema=self.sia_dists_marginales,
            distribucion_particion=self.memoria_particiones[mip][1],
            tiempo_total=time.time() - self.sia_tiempo_inicio,
            particion=fmt_mip,
        )
    
    def nodes_complement(self, nodes: list[tuple[int, int]]):
        return list(set(self.vertices) - set(nodes))
    
    def find_mip(self):
        """
        Implementa el algoritmo para encontrar la bipartición óptima
        utilizando el enfoque geométrico-topológico.
        """
        self.sia_logger.critic("empieza.")
        estado_inicial = self.estado_inicial
        estado_final = self.estado_final
        self.idx_ncubos = list(range(len(self.sia_subsistema.indices_ncubos)))
        self.caminos: Dict[int, List[List[int]]] = {0: [estado_inicial.tolist()]}
        self.tabla_transiciones[tuple(self.caminos[0][0]),tuple(self.caminos[0][0])] = [0.0 for _ in range(len(self.sia_subsistema.indices_ncubos))]
        for nivel in range(1, len(estado_inicial)+1):
            self.calcular_costos_nivel(estado_final,nivel)
        candidatos = self.identificar_particiones_optimas()
        for idx, (presentes, futuros) in enumerate(candidatos):
            presentes = self.sia_subsistema.dims_ncubos[presentes]
            futuros = self.sia_subsistema.indices_ncubos[futuros]
            dist =self.sia_subsistema.bipartir(futuros,presentes).distribucion_marginal()
            emd = emd_efecto(dist, self.sia_dists_marginales)
            key = [(0,nodo) for nodo in presentes]
            key.extend([(1,nodo) for nodo in futuros])
            # print(fmt_biparte_q(list(key), self.nodes_complement(key)))
            self.memoria_particiones[tuple(key)] = (emd, dist)
        return min(
            self.memoria_particiones, key=lambda k: self.memoria_particiones[k][0]
        )
    
    def calcular_costos_nivel(self,estado_final: np.ndarray, nivel):
        n = len(estado_final)      
        visitados:set[tuple] = set()
        self.caminos[nivel] = []
        for estado_anterior in self.caminos[nivel - 1]:
            estado_actual = np.array(estado_anterior)
            for i in range(n):
                if estado_actual[i] != estado_final[i]:
                    nuevo_estado = estado_actual.copy()
                    nuevo_estado[i] = estado_final[i]
                    nuevo_estado_tuple = tuple(nuevo_estado)
                    if nuevo_estado_tuple not in visitados:
                        self.caminos[nivel].append(nuevo_estado.tolist())
                        self.calcular_costo(self.caminos[0][0],nuevo_estado.tolist(),self.idx_ncubos)
                        visitados.add(nuevo_estado_tuple)

    def calcular_costo(self, estado_inicial:tuple, estado_final:tuple, ncubos:list[int]):
        """
            Funcion encargada de calcular el costo de transicion de transicion del estado inicial al estado final
            para las variables futuras definidas en ncubos
            aplica la funcion de costo tx(i,j)= y(|X[i]-X[j]|+ sum(tx(k,j)))
            donde:
                - y es el factor de decrecimiento 1/2^(dh(i,j))
                - dh(i,j) es la distancia hamming entre i y j
                - X[i] es el valor de probabilida de transicion de un estado para cada variable futura
                - sum(tx(i,k)) son todos costos de transicion de los vecinos de j que estan en un 
                  camino optimo desde i
        """
        key = tuple(estado_inicial), tuple(estado_final)
        if key not in self.tabla_transiciones:
            self.tabla_transiciones[key] = [None]*len(self.sia_subsistema.indices_ncubos)
        distancia_hamming = self.hamming(estado_inicial, estado_final)
        factor = 1/(2**distancia_hamming)
        # index_inicial = tuple(np.array(estado_inicial)[::-1])
        # index_final = tuple(np.array(estado_final)[::-1])


        estado_ini_int = int("".join(map(str, estado_inicial[::-1])), 2)
        estado_fin_int = int("".join(map(str, estado_final[::-1])), 2)

        # Con eso, cada flat_data[idx][...] ya te da directamente X[i] o X[j].
        diffs = np.abs(
            np.array([flat[estado_ini_int] for flat in self._flat_data])
        - np.array([flat[estado_fin_int] for flat in self._flat_data])
        )
        self.tabla_transiciones[key] = diffs.tolist()
        # for idx in ncubos:
        #     self.tabla_transiciones[key][idx] = (abs(self.sia_subsistema.ncubos[idx].data[index_inicial]-self.sia_subsistema.ncubos[idx].data[index_final]))
        
        if distancia_hamming > 1:
            for i in range(len(estado_inicial)):
                if estado_inicial[i] != estado_final[i]:
                    nuevo_estado = estado_final.copy()
                    nuevo_estado[i] = estado_inicial[i]
                    nuevo_estado_tuple = tuple(nuevo_estado)
                    temp_key = tuple(estado_inicial), nuevo_estado_tuple
                    for n in ncubos:
                        self.tabla_transiciones[key][n] = self.tabla_transiciones[key][n] + self.tabla_transiciones[temp_key][n]
        tmp =[]
        for i,n in enumerate(self.tabla_transiciones[key]):
            if n is not None:
                tmp.append(factor * n)
            else:
                tmp.append(n)
        self.tabla_transiciones[key] = tmp

    def identificar_particiones_optimas(self):
        """
        Identifica las particiones óptimas basadas en los costos de transición
        y las distancias Hamming entre los estados.
        """
        # idx_nivel_cero = 0
        # idx_nivel_cero_2 = 1
        # costo=1e5
        key = tuple(self.caminos[0][0]), tuple(self.estado_final)
        costos: list = self.tabla_transiciones[key]
        # print(f"costos nivel cero {costos}")
        # for idx, valor in enumerate(costos):
        #     if valor < costo:
        #         costo = valor
        #         idx_nivel_cero = idx
        # presentes_nivel_cero = [i for i in range(len(self.estado_final))]
        # furutros_nivel_cero = [i for i in range(len(self.sia_subsistema.indices_ncubos)) if i != idx_nivel_cero]
        # candidatos = [[presentes_nivel_cero, furutros_nivel_cero]]
        # pares = [(valor, idx) for idx, valor in enumerate(costos)]
        # menores = heapq.nsmallest(len(self.estado_inicial), pares, key=lambda x: x[0])
        candidatos = []
        n_vars = len(costos)
        for idx in range(n_vars):
            presentes = [i for i in range(len(self.estado_final))]
            futuros = [i for i in range(n_vars) if i != idx]
            candidatos.append([presentes, futuros])
        # _, idx_nivel_cero_1 = dos_menores[0]
        # _, idx_nivel_cero_2 = dos_menores[1]
        # print(idx_nivel_cero_1, idx_nivel_cero_2)
        # presentes_1 = [i for i in range(n_vars)]
        # futuros_1  = [i for i in range(n_vars) if i != idx_nivel_cero_1]
        # presentes_2 = [i for i in range(n_vars)]
        # futuros_2  = [i for i in range(n_vars) if i != idx_nivel_cero_2]
        # candidatos = [
        #     [presentes_1, futuros_1],
        #     [presentes_2, futuros_2]
        # ]
        # print(f"candidatos nivel cero {candidatos}")
        es_par = len(self.caminos) % 2 == 0
        if es_par:
            mitad = len(self.caminos) // 2
        else:
            mitad = (len(self.caminos) // 2) + 1
        for nivel in range(1,mitad):
            # candidato_nivel = self.caminos[nivel][0]
            costo_candidato_nivel = 1e5
            presentes_nivel = []
            futuros_nivel = []
            for estado in self.caminos[nivel]:
                # candidato = estado
                costo_candidato = 0
                presentes = []
                futuros = []
                actual = self.tabla_transiciones.get((tuple(self.caminos[0][0]), tuple(estado)), None)
                estado_complementario = (1-np.array(estado)).tolist()
                complementario = self.tabla_transiciones.get((tuple(self.caminos[0][0]), tuple(estado_complementario)), None)
                for idx,i in enumerate(estado):
                    if i == self.caminos[0][0][idx]:
                        presentes.append(idx)
                for idx,_ in enumerate(self.idx_ncubos):
                    if actual[idx] <= complementario[idx]:
                        futuros.append(idx)
                        costo_candidato += actual[idx]
                    else:
                        costo_candidato += complementario[idx]
                if costo_candidato < costo_candidato_nivel:
                    # candidato_nivel = candidato
                    costo_candidato_nivel = costo_candidato
                    presentes_nivel = presentes
                    futuros_nivel = futuros
            candidatos.append([presentes_nivel, futuros_nivel])
        return candidatos

    def hamming(self,a: List[int], b: List[int]) -> int:
        return sum(x != y for x, y in zip(a, b))