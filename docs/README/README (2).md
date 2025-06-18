🧱 Project Structure: `your_project/`
-------------------------------------

```bash

your_project/
│
├── run.py                  # Main entry point (cleanest way to run in dev)
├── .env                    # Optional: For setting PYTHONPATH or config vars
├── README.md               # Project description
├── requirements.txt        # Your dependencies
│
├── config/
│   └── paths.py            # All path handling (project root, data paths, etc.)
│
├── data/                   # Your datasets (raw, processed, etc.)
│   ├── raw/
│   └── processed/
│
├── script/                 # Standalone scripts, tests, dev code
│   └── temp.py             # Can run with run.py or directly (controlled imports)
│
├── test_module/            # Your actual logic/modules
│   ├── __init__.py
│   └── module.py
│
└── utils/                  # Optional: helpers shared across code
    └── logger.py
```