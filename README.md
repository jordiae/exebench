# ExeBench: an ML-scale dataset of executable C functions

ExeBench is a dataset of millions of C functions paired with dependencies and metadatada such that at least a subset of it can be executed with IO pairs. It is mainly inteded for machine learning applications but it is application-agnostic enough to have other usages.
Please read the paper for more information: https://dl.acm.org/doi/abs/10.1145/3520312.3534867

## Usage

### Option 1: Using the helpers in this repo


```
git clone https://github.com/jordiae/exebench.git
cd exebench/
python -m venv venv
source venv/bin/activate
pip install -r requirements_examples.txt
PYTHONPATH="${PYTHONPATH}:${pwd}" python examples/basic.py
```

### Option 2: Directly using the Hugginface Datasets library


```
!pip install datasets zstandard
from datasets import load_dataset

# Load dataset split. In this case, synthetic test split
dataset = load_dataset('jordiae/exebench', split='test_synth')
for e in dataset:
  ...
```

### Option 3: Directly download the dataset

Take a look at the files at: https://huggingface.co/datasets/jordiae/exebench/tree/main
The dataset consist of directories compressed with TAR. Inside each TAR, there is a series of jsonline files compressed with zstandard.

## Statistics and versions

This release corresponds to ExeBench v1.01, a version with some improvements with respect to the original one presented in the paper. The statistics and studies presented in the paper remain consistent with respect to the new ones. The final splits of the new version consist of the following functions:


```
train_not_compilable: 2.357M
train_synth_compilable: 2.308373M
train_real_compilable: 0.675074M
train_synth_simple_io: 0.550116M
train_real_simple_io: 0.043769M
train_synth_rich_io: 0.097250M
valid_synth: 5k
valid_real: 2.133k
test_synth: 5k
test_real: 2.134k
```

The original dataset (v1.00) with the exact same data studied in the paper can be accessed on request at: https://huggingface.co/datasets/jordiae/exebench_legacy (please reach out for access)


## License

All C functions keep the original license as per their original Github repository (available in the metadata). All ExeBench contributions (I/O examples, boilerplate to run functions, etc) are released with an MIT license.

## Citation

```
@inproceedings{10.1145/3520312.3534867,
author = {Armengol-Estap\'{e}, Jordi and Woodruff, Jackson and Brauckmann, Alexander and Magalh\~{a}es, Jos\'{e} Wesley de Souza and O'Boyle, Michael F. P.},
title = {ExeBench: An ML-Scale Dataset of Executable C Functions},
year = {2022},
isbn = {9781450392730},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3520312.3534867},
doi = {10.1145/3520312.3534867},
abstract = {Machine-learning promises to transform compilation and software engineering, yet is frequently limited by the scope of available datasets. In particular, there is a lack of runnable, real-world datasets required for a range of tasks ranging from neural program synthesis to machine learning-guided program optimization. We introduce a new dataset, ExeBench, which attempts to address this. It tackles two key issues with real-world code: references to external types and functions and scalable generation of IO examples. ExeBench is the first publicly available dataset that pairs real-world C code taken from GitHub with IO examples that allow these programs to be run. We develop a toolchain that scrapes GitHub, analyzes the code, and generates runnable snippets of code. We analyze our benchmark suite using several metrics, and show it is representative of real-world code. ExeBench contains 4.5M compilable and 700k executable C functions. This scale of executable, real functions will enable the next generation of machine learning-based programming tasks.},
booktitle = {Proceedings of the 6th ACM SIGPLAN International Symposium on Machine Programming},
pages = {50–59},
numpages = {10},
keywords = {Code Dataset, Program Synthesis, Mining Software Repositories, C, Machine Learning for Code, Compilers},
location = {San Diego, CA, USA},
series = {MAPS 2022}
}
```

## Credits

We thank Anghabench authors for their type inference-based synthetic dependencies generation for C functions. This software, Psyche-C, can be found at: https://github.com/ltcmelo/psychec

## Contact

```
jordi.armengol.estape at ed.ac.uk
```
