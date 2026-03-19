from enum import Enum


class MetricDistance(Enum):
    """La clase notaciones recopila diferentes notaciones binarias. Al definir el tipo se accede por `.value`."""

    EMD_EFECTO = "emd-effect"
    EMD_CAUSA = "emd-cause"
    MANHATTAN = "distancia-manhattan"
    EUCLIDIANA = "distancia-euclidiana"
