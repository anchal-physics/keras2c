"""test_convolution_layers.py
This file is part of the test suite for keras2c
Implements tests for convolution layers
"""

#!/usr/bin/env python3

import unittest
import tensorflow.keras as keras
from keras2c import keras2c_main
import subprocess
import time
import os
from test_core_layers import build_and_run
import tensorflow as tf
tf.compat.v1.disable_eager_execution()

__author__ = "Rory Conlin"
__copyright__ = "Copyright 2020, Rory Conlin"
__license__ = "MIT"
__maintainer__ = "Rory Conlin, https://github.com/f0uriest/keras2c"
__email__ = "wconlin@princeton.edu"


class TestConvolutionTransposeLayers(unittest.TestCase):
    """tests for convolution layers"""

    def test_Conv1DTranspose1(self):
        inshp = (6, 4)
        filters = 13
        kernel_size = 3
        strides = 1
        padding = 'valid'
        dilation_rate = 1
        activation = 'relu'
        a = keras.layers.Input(inshp)
        b = keras.layers.Conv1DTranspose(8, kernel_size=6, padding='valid')(a)
        # b = keras.layers.Conv1DTranspose(filters=filters,
        #                                  kernel_size=kernel_size,
        #                                  strides=strides,
        #                                  padding=padding,
        #                                  dilation_rate=dilation_rate,
        #                                  activation=activation,
        #                                  use_bias=False)(a)
        model = keras.models.Model(inputs=a, outputs=b)
        name = 'test___Conv1DTranspose1' + str(int(time.time()))
        keras2c_main.k2c(model, name)
        rcode = build_and_run(name)
        self.assertEqual(rcode, 0)

if __name__ == "__main__":
    unittest.main()