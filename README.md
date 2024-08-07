# keras2c


[![Test](https://github.com/anchal-physics/keras2c/actions/workflows/test.yml/badge.svg)](https://github.com/anchal-physics/keras2c/actions/workflows/test.yml)
![Codecov](https://img.shields.io/codecov/c/github/anchal-physics/keras2c)


**Note**: This is a fork of the original [keras2c](https://github.com/PlasmaControl/keras2c) library. The licence
remains the same as the original library. This fork adds additional features and installment instructions.

Install conda environment (for MacOS):
```bash
conda env create -f conda_keras2c.yml
conda develop /path/to/this/repo
```

Installation for linux:
```bash
cd /path/to/this/repo
conda create -n keras2c python=3.11.5
conda activate keras2c
python -m pip install -r requirements
conda develop .
```
Then you can run keras2c code from anywhere on your machine after activating conda environment `keras2c`.

**********

keras2c is a library for deploying keras neural networks in C99, using only standard libraries.
It is designed to be as simple as possible for real time applications.

## Quickstart

After cloning the repo, install the necessary packages with ``pip install -r requirements.txt``.

keras2c can be used from the command line:

```bash
python -m keras2c [-h] [-m] [-t] model_path function_name

A library for converting the forward pass (inference) part of a keras model to
    a C function

positional arguments:
    model_path         File path to saved keras .h5 model file
    function_name      What to name the resulting C function
    
optional arguments:
    -h, --help         show this help message and exit
    -m, --malloc       Use dynamic memory for large arrays. Weights will be
                        saved to .csv files that will be loaded at runtime
    -t , --num_tests   Number of tests to generate. Default is 10
```

It can also be used with a python environment in the following manner:

```python
from keras2c import k2c
k2c(model, function_name, malloc=False, num_tests=10, verbose=True)
```
For more information, see `Installation <https://f0uriest.github.io/keras2c/installation.html>`_ and  `Usage <https://f0uriest.github.io/keras2c/usage.html>`_


## Supported Layers

- **Core Layers**: Dense, Activation, Dropout, Flatten, Input, Reshape, Permute, RepeatVector,  ActivityRegularization, SpatialDropout1D, SpatialDropout2D, SpatialDropout3D
- **Convolution Layers**: Conv1D, Conv2D, Conv3D, Cropping1D, Cropping2D, Cropping3D, UpSampling1D, UpSampling2D, UpSampling3D, ZeroPadding1D, ZeroPadding2D, ZeroPadding3D
- **Pooling Layers**: MaxPooling1D, MaxPooling2D, AveragePooling1D, AveragePooling2D, GlobalMaxPooling1D, GlobalAveragePooling1D, GlobalMaxPooling2D, GlobalAveragePooling2D, GlobalMaxPooling3D,GlobalAveragePooling3D
- **Recurrent Layers**: SimpleRNN, GRU, LSTM, SimpleRNNCell, GRUCell, LSTMCell
- **Embedding Layers**: Embedding
- **Merge Layers**: Add, Subtract, Multiply, Average, Maximum, Minimum, Concatenate, Dot
- **Advanced Activation Layers**: LeakyReLU, PReLU, ELU, ThresholdedReLU, Softmax, ReLU
- **Normalization Layers**: BatchNormalization
- **Noise Layers**: GaussianNoise, GaussianDropout, AlphaDropout
- **Layer Wrappers**: TimeDistributed, Bidirectional
  
## ToDo
- **Core Layers**: Lambda, Masking
- **Convolution Layers**: SeparableConv1D, SeparableConv2D, DepthwiseConv2D, Conv2DTranspose, Conv3DTranspose
- **Pooling Layers**: MaxPooling3D, AveragePooling3D
- **Locally Connected Layers**: LocallyConnected1D, LocallyConnected2D
- **Recurrent Layers**: ConvLSTM2D, ConvLSTM2DCell
- **Merge Layers**: Broadcasting merge between different sizes
- **Misc**: models made from submodels
  
## License

The project is licensed under the LGPLv3 license.
