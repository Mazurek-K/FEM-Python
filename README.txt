fem_solver/
│
├─ main.py               # Entry point: runs analysis
├─ fem/
│   ├─ __init__.py
│   ├─ mesh.py           # Define nodes, elements, connectivity
│   ├─ materials.py      # Define material properties
│   ├─ elements.py       # Element matrices (stiffness, mass)
│   ├─ assembly.py       # Global K, M assembly and BC application
│   ├─ solver.py         # Static & vibration solvers
│   └─ utils.py          # Utilities (plotting, load definitions)
│
├─ examples/
│   └─ simple_bar.py     # Example problem definitions
│
└─ results/
    └─ *.csv, plots      # Optional output
