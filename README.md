# Mesh Triangulation

![python36](https://img.shields.io/badge/python-3.6-blue.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

A toy python code to produce a triangulated mesh using [Delauny](https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.Delaunay.html) from scipy.

![Example Mesh](./pictures/Figure_1.svg)

## Requirements
Python 3.6.x with the libraries, `matplotlib`,`scipy`, and `numpy`. For the file [`gui.py`](./gui.py), the library `PyQt5` is needed.

## Run
An example is run by 
```bash
$ python3 main.py
````
and the GUI is run by
```bash
$ python3 gui.py
```
