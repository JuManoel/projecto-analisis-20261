# Diagrama de Componentes

## Organización de Componentes

El diagrama de componentes muestra la estructura modular del sistema a nivel de implementación:

### 1. Componentes Principales
- `main.py`: Punto de entrada del sistema
- `Manager`: Gestión de configuración y recursos
- Estrategias (Phi/BruteForce/QNodes): Implementaciones concretas *(Pyphi es el módulo oficial, a pesar de esto utiliza fuerza bruta para la resolución del problema)*

### 2. Módulos Base
- `src.models.base`: Contiene las clases fundamentales
- `src.logic.base`: Implementa funciones auxiliares
- `src.constants/`: Define constantes globales o de modelos de datos

### 3. Middlewares
Proporcionan servicios transversales al sistema
- `profile`: Sistema de profiling
- `observer`: Sistema de monitoreo

### 4. Utilidades y Configuración
- Funciones de reindexación
- Selección de estados
- Configuraciones de la aplicación

El diagrama utiliza diferentes estilos visuales para distinguir:
- Componentes core (rosa)
- Middlewares (azul claro)
- Utilidades (azul muy claro)

Esta organización permite un desarrollo modular y mantenible, facilitando la extensión del sistema con nuevas funcionalidades.

¿Te gustaría que profundice en algún aspecto específico de alguno de los diagramas o que explique con más detalle alguna de las relaciones entre componentes?

```mermaid
%% Diagrama de Componentes
graph TD
    %% Componente Principal
    A[main.py] --> B[Manager]
    
    %% Gestión y Estrategias
    B --> C[BruteForce-Phi-QNodes]
    B --> H[src.constants.base]
    
    %% Modelos Base
    C --> D{src.models.base}
    D --> E[SIA]
    D --> F[System]
    D --> N[NCube]
    D --> O[Application]
    
    %% Solución y Visualización
    C --> G[Solution]
    G --> P[Voice Synthesis]
    
    %% Middlewares y Utilidades
    C --> I[src.middlewares]
    I --> J[profile]
    I --> K[observer]
    J --> Q[ProfilingManager]
    J --> R[ProfilerContext]
    
    %% Lógica y Funciones Base
    E --> L[src.logic.base]
    L --> S[reindexar]
    L --> T[seleccionar_subestado]
    
    %% Constantes y Configuración
    H --> U[PROFILING_PATH]
    H --> V[COLS_IDX]
    H --> W[HTML_EXTENSION]
    
    %% Enumeraciones y Tipos
    D --> X[src.models.enums]
    X --> Y[Notation]
    
    %% Funciones de Aplicación
    O --> Z[distancia_metrica]
    O --> AA[notacion]
    
    %% Estilos
    classDef core fill:#f9f,stroke:#333,stroke-width:2px
    classDef middleware fill:#bbf,stroke:#333,stroke-width:2px
    classDef util fill:#ddf,stroke:#333,stroke-width:2px
    
    %% Aplicar estilos
    class B,C,D,E,F core
    class I,J,K middleware
    class L,S,T,Q,R util
```

