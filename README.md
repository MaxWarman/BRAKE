# Implementation of BRAKE Protocol

*Author:* Maksymilian Górski, Wrocław University of Science and Technology

This repository is dedicated for impementation of Biometric Resilient Authenticated Key Exchange (BRAKE) Protocol created for the author's bachelor's thesis.

The article, that the presented implementation is based on is available under this [link](https://eprint.iacr.org/2022/1408).

### Prerequisites

The proposed implementation of the BRAKE protocol was originally written using the Python programming language version 3.10.11. However, in accordance with the idea of backward compatibility of the Python language, it is possible to run the presented program using newer versions of the language.

### Installation of external Python modules

In order to install the external Python modules, necessary for the correct execution of the program, run the following command in `BRAKE/` directory:

```
python3 -m pip install -r requirements.txt
```

### Execution of the script

To run the script - after successful installation of external modules - from the `BRAKE/` directory run the following command:

```
python3 main.py
```