1. Overview

This dataset accompanies the GeoMIP project and contains all data used to validate the algorithms described in the manuscript.
The data include transition probability matrices (TPMs) generated for different networks and experimental results comparing three reference strategies:

PyPhi (theoretical reference implementation),

Strategy Q (used as reference when PyPhi values are not available), and

GeoMIP (Geometric strategy, proposed in this study), which includes Method 1 and Method 2 variants.

All datasets are provided to ensure full transparency and reproducibility of the reported results.

2. Data Structure
GeoMIP/
├── data/
│   ├── samples/
│   │   ├── N3A.csv
│   │   ├── N4A.csv
│   │   ├── N15A.csv
│   │   └── ...
│   ├── creation.py        ← script for generating larger synthetic networks (>15 nodes)
│
├── src/
│   ├── Method_1/          ← implementation of GeoMIP Method 1
│   └── Method_2/          ← implementation of GeoMIP Method 2
│
└── results/
│   ├── Pruebas_Metodo1.xlsx
│   └── Pruebas_Metodo2.xlsx
└── README.md          ← this document

The data/samples/ folder contains the transition probability matrices (TPMs) for each network used in the experiments.

The data/creation.py script allows generating new TPMs for larger or customized networks (e.g., >15 nodes).

The src/ folder contains the source code implementing both variants of the GeoMIP algorithm (Method 1 and Method 2).

The results/Pruebas_Metodo1.xlsx file contains the results obtained by Method 1 (GPU Accelerated) of GeoMIP and strategies (PyPhi and Q) for the same networks.
The results/Pruebas_Metodo2.xlsx file contains the results obtained by Method 2 (Dynamic Programming reformulation) of GeoMIP and strategies (PyPhi and Q) for the same networks.

3. File Formats
| File type | Format                 | Description                                                                                                                                                        |
| --------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `.csv`    | Comma-separated values | TPMs representing the probabilistic state transitions of each network. Each row corresponds to a current system state and each column to a next-state probability. |
| `.xlsx`   | Microsoft Excel        | Consolidated experimental results for each method, including Φ values, runtimes, and reference comparisons.                                                        |
| `.py`     | Python script          | Script for generating new synthetic networks and TPMs with arbitrary sizes and parameters.                                                                         |
| `.md`     | Markdown               | Documentation describing datasets and folder structure.                                                                                                            |
                                                                                                      |

All CSV files use UTF-8 encoding, decimal points ".", and commas "," as separators.
Excel files use standard worksheet format compatible with Microsoft Excel ≥2016 or LibreOffice Calc.

4. Data Interpretation
4.1 TPM files (src/samples/*.csv)

Each CSV file encodes the Transition Probability Matrix (TPM) for a specific test network.
  -Each row corresponds to a current state of the system.
  -Each column represents the probability of transitioning to a next state.
  -The matrices are row-stochastic (rows sum to 1).
  -These TPMs are the direct input to the GeoMIP algorithms (Methods 1 and 2) and to PyPhi when applicable.

Typical file naming convention:
N15A.csv  →  TPM for a 5-node network A

4.2 Results file

This file summarizes Φ-values and other evaluation metrics across strategies.
Each sheet or block includes the following columns:
| Column             | Description                                                            |
| ------------------ | ---------------------------------------------------------------------- |
| **Network**        | Identifier of the test network (e.g., 3Nodes, 4Nodes…).                |
| **Strategy**       | Algorithm used: `PyPhi`, `Q`, or `GeoMIP`.                             |
| **Method**         | When applicable: `GeoMIP-1` (Method 1) or `GeoMIP-2` (Method 2).       |
| **Phi_value**      | Computed integrated information (Φ) for the given network.             |
| **Runtime**        | Execution time (in seconds).                                           |
| **Status / Notes** | Additional comments (e.g., “PyPhi not available”, “reference Q used”). |

Interpretation guidelines:
  Use PyPhi values as ground truth when present. 
  If PyPhi results are missing, use Strategy Q as the secondary reference.
  Compare both GeoMIP methods (1 and 2) against these references to evaluate accuracy and efficiency.

Generating larger networks
The script data/creation.py can be used to generate synthetic networks with more than 15 nodes for scalability tests.
It supports user-defined parameters such as:
  -n_nodes (network size)
  -p_connect (connection probability)
  -distribution (rule for assigning transition probabilities)

5. Provenance
The TPM datasets were generated as follows:

Synthetic networks:
All networks except the two 15-node configurations were generated synthetically.
These synthetic datasets were designed to simulate small-scale system dynamics and allow systematic evaluation of algorithmic behavior under controlled conditions.

Empirical networks (15-node):
The two networks of 15 nodes correspond to empirical data derived from fruit fly (Drosophila melanogaster) neural recordings, processed according to the methodology described in the publications cited in the main article.
These networks represent biologically grounded connectivity structures used to validate GeoMIP under realistic conditions.

Thus, the dataset combines synthetic test networks (for scalability and robustness analysis) with biological networks (for ecological validity and comparison with established IIT benchmarks).
