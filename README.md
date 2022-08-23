# ExeBench: an ML-scale dataset of executable C functions

## Usage

```
# Load dataset split. In this case, synthetic test split
dataset = load_dataset('jordiae/exebench', split='test_synth')
```

See examples/ for examples.

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

We thank Anghabench authors for their type inference-based synthetic dependencies generation for C functions.

## Contact

```
jordi.armengol.estape at ed.ac.uk
```
