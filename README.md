# Benchmarking Commercial Online Search Language Models With and Without Source Control for Evidence-Based Neurology

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Under Review](https://img.shields.io/badge/Status-Under%20Review-orange.svg)](https://www.nature.com/npjdigmed/)

> **Under Review**: This repository contains code and analysis for a study currently under review at *Nature Comminications*.

## 📖 Overview

The rapid emergence of **Retrieval-Augmented Generation (RAG)** systems promises to change the way we conduct web search and access the internet, altering the way many of us ultimately access medical literature. However, the reliability of these systems for evidence-based medicine remains largely unvalidated. This study presents the first comprehensive benchmark of **commercial online search language models** for clinical questions, with a focus on source quality control and evidence accuracy.

We systematically evaluate **Perplexity.ai's** three commercial models alongside **OpenEvidence** using 130 neurology questions derived from **American Academy of Neurology (AAN) guidelines**:

### 🔬 Models Tested
- **Sonar** (Llama 3.3 70B-based, no reasoning)
- **Sonar-Pro** (Enhanced Llama 3.3 70B-based, no reasoning)  
- **Sonar-Pro-Reasoning** (DeepSeek-R1-based with reasoning capabilities)
- **OpenEvidence** (Medical-specific RAG system)

### 🎯 Key Research Questions
1. **Accuracy**: How accurate are commercial RAG systems for evidence-based neurology questions?
2. **Source Control**: Does domain whitelisting (limiting to AAN.com / Neurology.org sources) improve answer quality?
3. **Model Performance**: Which commercial models best for clinical applications? How do LLM + web-search setups compare more broadly?
4. **Evidence Quality**: How does source retrieval of different kind influence (professional sources vs. non-professional sources) answer quality?


## 📊 Results and Discussion

For detailed results, statistical analysis, and comprehensive discussion of our findings, please refer to our paper currently under review at *Nature Communications*.

---

## 📂 Repository Structure

```
Online-Search-Based-RAG/
├── 📊 results/                          # Experimental results and analysis
├── 📈 Visualizations/                   # Figures and plots
├── 🗂️ Graphical_Outlines/              # Experimental design diagrams
├── 🧪 Run_Experiments.ipynb            # Main experimental pipeline
├── 🔬 Testing_querying_functions.ipynb # API testing and validation
├── 📋 basic_analysis.ipynb             # Statistical analysis notebook
├── 🐍 perplexity_experiment.py         # Core API interaction module
├── 📝 questions.xlsx                   # AAN-derived question dataset
├── 📋 requirements.txt                 # Python dependencies
└── 📄 README.md                        # This documentation
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+ (analyses were run in venv on Python 3.9.6)
- Perplexity API key
- Required packages (see `requirements.txt`)

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/[username]/Online-Search-Based-RAG.git
   cd Online-Search-Based-RAG
   ```

2. **Install Dependencies (optionally create venv first)**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up API Credentials**
   ```bash
   export PERPLEXITY_API_KEY="your_api_key_here"
   ```
(Or set up in .env)

### Running Experiments

#### Single Question Testing
```python
from perplexity_experiment import run_experiment_on_question

# Test a clinical question
results = run_experiment_on_question(
    question="What is the recommended treatment for relapsing-remitting multiple sclerosis?",
    model="sonar-pro",
    whitelist=["aan.com", "neurology.org"],
    iterations=4
)
```

#### Full Experimental Pipeline
```python
from perplexity_experiment import run_experiment_on_excel

# Run complete benchmark
run_experiment_on_excel(
    input_file="questions.xlsx",
    output_file="results/experiment_results.xlsx",
    model="sonar-pro-reasoning",
    whitelist=["aan.com"],
    iterations=4
)
```

---

## 📊 Experimental Design

### Question Dataset
- **130 clinical questions** derived from AAN practice guidelines
- **Question types**: Knowledge-based, case-based clinical scenarios
- **Dataset Source**: Questions derived from the benchmark dataset published in [Masanneck et al., npj Digital Medicine (2025)](https://www.nature.com/articles/s41746-025-01536-y)

### Evaluation Methodology
- **Blinded expert review** by board-certified neurologists
- **Three-tier rating system**: Correct, Inaccurate, Wrong
- **Source quality assessment**: Professional vs. non-professional sources

### Model Configurations Tested
```python
experimental_conditions = {
    "no_whitelisting": {
        "models": ["sonar", "sonar-pro", "sonar-pro-reasoning"],
        "whitelist": None
    },
    "with_whitelisting": {
        "models": ["sonar", "sonar-pro", "sonar-pro-reasoning"], 
        "whitelist": ["aan.com", "neurology.org"]
    },
    "baseline": {
        "model": "OpenEvidence",
        "whitelist": "assumed"  # Medical literature focused
    }
}
```


---

## 📚 Citation

If you use this repository in your research, please cite:

```bibtex
@misc{Masanneck2025-Online-Search-RAG,
  title={Benchmarking Commercial Online Search Language Models With and Without Source Control for Evidence-Based Neurology},
  author={Masanneck, Lars and Epping, Paula Z. and Meuth, Sven G. and Pawlitzki, Marc},
  year={2025},
  doi={To be added later},
  note={Under review},
  url={To be added later}
  }
```

### Related Publications

For the AAN questions dataset used in this benchmark, please also cite:

```bibtex
@article{Masanneck2025Dataset,
  title={Evaluating base and retrieval augmented LLMs with document or online support for evidence based neurology},
  author={Masanneck, Lars and Meuth, Sven G. and Pawlitzki, Marc},
  journal={npj Digital Medicine},
  volume={8},
  number={137},
  year={2025},
  publisher={Nature Publishing Group},
  doi={10.1038/s41746-025-01536-y},
  url={https://www.nature.com/articles/s41746-025-01536-y}
}
```

---


## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Research institutions** L.M’.s work was supported by Deutsche Forschungsgemeinschaft (DFG, German Research Foundation) – 493659010 – and B.Braun Foundation. Computing expenses were further generously supported by the society of friends and supporters of Duesseldorf’s university (Gesellschaft von Freunden und Förderern der HHU – GFFU). 


