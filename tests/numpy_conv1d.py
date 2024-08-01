'''
Numpy implementation of 1D convolution and transposed convolution of keras.Conv1D
and keras.Conv1DTranspose

The idea is to obtain the same output as keras.Conv1D and keras.Conv1DTranspose in
simple numpy code so that it can be implemented in C code.

Inspired by the following code:
https://github.com/rmwkwok/transposed_convolution_in_numpy/tree/main
'''

import numpy as np
import tensorflow.keras as keras
import traceback

'''
def out_shape(input_shape, kernel, strides=1, padding='valid', mode='normal')

Returns the output shape of the convolution operation.

Args:
    input_shape (tuple of 2 int): shape of the input tensor without batch size. (height, channels)
    kernel (numpy.ndarray): kernel of the convolution operation. Returned by model.layer[i].get_weights()[0] for a keras model.
    strides (int): strides of the convolution operation
    padding (str): padding of the convolution operation. 'valid' or 'same' are supported.
    mode (str): mode of the convolution operation. 'normal' means normal convolution and 'transposed' means transposed convolution.

Returns:
    tuple of 2 int: shape of the output tensor without batch size. (no of convolutions, no of filters)
'''
def out_shape(input_shape, kernel, strides=1, padding='valid', mode='normal'):
    ih, ic = input_shape
    if mode == 'normal':
        ksize, kc, nfilters = kernel.shape
        assert ic == kc
        if padding == 'valid':
            p_2 = 0
        elif padding == 'same':
            p_2 = ksize - 1
        nconv = (ih + p_2 - ksize) // strides + 1
    elif mode == 'transposed':
        ksize, nfilters, kc = kernel.shape
        assert ic == kc
        if padding == 'valid':
            nconv = ih + ksize - 1 + ((ih - 1) * (strides - 1))
        elif padding == 'same':
            nconv = ih + (ih * (strides - 1))
    return (nconv, nfilters)

'''
def padding1d(inputs, kernel, strides=1, padding='valid', mode='normal')

Returns the padded input tensor for the convolution operation and crops the output
tensor for the transposed convolution operation.

Args:
    inputs (numpy.ndarray): input tensor with batch size. (batch size, height, channels)
    kernel (numpy.ndarray): kernel of the convolution operation. Returned by model.layer[i].get_weights()[0] for a keras model.
    strides (int): strides of the convolution operation
    padding (str): padding of the convolution operation. 'valid' or 'same' are supported.
    mode (str): mode of the convolution operation. 'normal' means normal convolution and 'transposed' means transposed convolution.

Returns:
    numpy.ndarray: padded input tensor with batch size. (batch size, height, channels) or cropped output tensor with batch size. (batch size, convolutions, filters)
'''
def padding1d(inputs, kernel, strides=1, padding='valid', mode='normal'):
    ksize = kernel.shape[0]
    if padding == 'valid':
        return inputs
    elif padding == 'same':
        if mode == 'normal':
            p_2 = ksize - 1
        elif mode == 'transposed':
            p_2 = ksize - strides
    if p_2 % 2 == 0:
        before = after = p_2 // 2
    else:
        before = (p_2 - 1) // 2
        after = before + 1
    if mode == 'normal':
        outputs = np.zeros((inputs.shape[0], inputs.shape[1] + p_2, inputs.shape[2]))
        outputs[:, before:before+inputs.shape[1], :] = inputs
    elif mode == 'transposed':
        outputs = inputs[:, before:inputs.shape[1]-after, :]
    return outputs

'''
def stride1d(inputs, kernel, strides=1, padding='valid', mode='normal')

Returns the strided output tensor for the convolution operation or zeros inserted (unstrided) input tensor for the transposed convolution operation.

Args:
    inputs (numpy.ndarray): input tensor with batch size. (batch size, height, channels)
    kernel (numpy.ndarray): kernel of the convolution operation. Returned by model.layer[i].get_weights()[0] for a keras model.
    strides (int): strides of the convolution operation
    padding (str): padding of the convolution operation. 'valid' or 'same' are supported.
    mode (str): mode of the convolution operation. 'normal' means normal convolution and 'transposed' means transposed convolution.

Returns:
    numpy.ndarray: strided output tensor with batch size. (batch size, convolutions, filters) or unstrided input tensor with batch size. (batch size, height, channels)
'''
def stride1d(inputs, kernel, strides=1, padding='valid', mode='normal'):
    # if strides == 1:
    #     return inputs
    ksize = kernel.shape[0]
    if mode == 'normal':
        if padding == 'valid':
            outputs = inputs[:, ::strides, :]
        elif padding == 'same':
            total_skip = (inputs.shape[1]-1) % strides
            if total_skip % 2 == 0:
                start_ind = total_skip // 2
            else:
                start_ind = total_skip // 2 + (ksize % 2)
            outputs = inputs[:, start_ind::strides, :]
    elif mode == 'transposed':
        outputs = np.zeros((inputs.shape[0], inputs.shape[1] + (inputs.shape[1] - 1) * (strides - 1), inputs.shape[2]))
        outputs[:, ::strides, :] = inputs
    return outputs

'''
def unroll_kernel1d(input_shape, kernel, strides=1, padding='valid', mode='normal')

Returns the unrolled kernel for the convolution or transposed convolution operations.

Args:
    input_shape (tuple of 2 int): shape of the input tensor without batch size. (height, channels)
    kernel (numpy.ndarray): kernel of the convolution operation. Returned by model.layer[i].get_weights()[0] for a keras model.
    strides (int): strides of the convolution operation
    padding (str): padding of the convolution operation. 'valid' or 'same' are supported.
    mode (str): mode of the convolution operation. 'normal' means normal convolution and 'transposed' means transposed convolution.

Returns:
    In normal mode:
        numpy.ndarray: unrolled kernel for the convolution operation. (channels, no of convolutions, filters, padded input size)
        Note: In current implmentation, the unrolled kernel in normal mode would only work for strides=1 case and it is assumed that
              the striding is done after the convolution operation.
    In transposed mode:
        numpy.ndarray: unrolled kernel for the transposed convolution operation.
                       (channels, zero inserted input size + kernel size - 1, filters, zero inserted input size)
        Note: In current implmentation, the unrolled kernel in transposed mode would only work for padding='valid' case and it is assumed that
              any cropping for padding='same' is done after the transposed convolution operation.

'''
def unroll_kernel1d(input_shape, kernel, strides=1, padding='valid', mode='normal'):
    nconv, nfilters = out_shape(input_shape, kernel, strides=strides, padding=padding, mode=mode)
    nh, nc = input_shape
    ksize = kernel.shape[0]
    if mode == 'normal':
        if padding == 'valid':
            p_2 = 0
        elif padding == 'same':
            p_2 = ksize - 1
        total_inp_size = nh + p_2
    elif mode == 'transposed':
        total_inp_size = nh + (nh - 1) * (strides - 1)
    if mode == 'normal':
        if padding == 'valid':
            start_ind = 0
        elif padding == 'same':
            # nconv_stride1 = ih + p_2 - ksize + 1 = total_inp_size - ksize + 1
            # total_skip = (nconv_stride1 - 1) % strides
            total_skip = (total_inp_size - ksize) % strides
            if total_skip % 2 == 0:
                start_ind = total_skip // 2
            else:
                start_ind = total_skip // 2 + (ksize % 2)
        unrolled_kernel = np.zeros((nc, nconv, nfilters, total_inp_size), dtype=np.float32)
        for ch in range(nc):
            for i in range(nconv):
                # Go through only those convs which are not removed in stride1d later
                i_s = start_ind + i * strides
                for f in range(nfilters):
                    if mode == 'normal':
                        unrolled_kernel[ch, i, f, i_s:i_s+ksize] += kernel[:, ch, f]
        return unrolled_kernel
    elif mode == 'transposed':
        unrolled_kernel = np.zeros((nc, total_inp_size + ksize - 1, nfilters, total_inp_size), dtype=np.float32)
        for ch in range(nc):
            for f in range(nfilters):
                for i in range(total_inp_size):
                    unrolled_kernel[ch, i:i+ksize, f, i] += kernel[:, f, ch]
    return unrolled_kernel

'''
def conv1d(inputs, kernel, strides=1, padding='valid')

Returns the output tensor of the convolution operation.

Args:
    inputs (numpy.ndarray): input tensor with batch size. (batch size, height, channels)
    kernel (numpy.ndarray): kernel of the convolution operation. Returned by model.layer[i].get_weights()[0] for a keras model.
    strides (int): strides of the convolution operation
    padding (str): padding of the convolution operation. 'valid' or 'same' are supported.

Returns:
    numpy.ndarray: output tensor with batch size. (batch size, convolutions, filters)
'''
def conv1d(inputs, kernel, strides=1, padding='valid'):
    n_batches, n_height, n_channels = inputs.shape
    outputs = np.zeros((n_batches, *out_shape((n_height, n_channels), kernel, strides=strides, padding=padding, mode='normal')))
    padded_input = padding1d(inputs, kernel, strides=strides, padding=padding, mode='normal')
    unrolled_kernel = unroll_kernel1d((n_height, n_channels), kernel, strides=strides, padding=padding, mode='normal')
    _, n_convs, n_filters, n_padded_inp = unrolled_kernel.shape
    assert n_padded_inp == padded_input.shape[1]
    for batch in range(n_batches):
        for ch in range(n_channels):
            flat_inp = np.zeros((n_padded_inp, 1))
            flat_inp[:, 0] = padded_input[batch, :, ch]
            for i in range(n_convs):
                outputs[batch, i, :] += np.matmul(unrolled_kernel[ch, i, :, :], flat_inp).flatten()
    return outputs
    # return stride1d(outputs, kernel, strides=strides, padding=padding, mode='normal')
    # This output striding is needed when unrolled kernel is first calculated with strides=1

'''
def conv1d_transpose(inputs, kernel, strides=1, padding='valid')

Returns the output tensor of the transposed convolution operation.

Args:
    inputs (numpy.ndarray): input tensor with batch size. (batch size, height, channels)
    kernel (numpy.ndarray): kernel of the transposed convolution operation. Returned by model.layer[i].get_weights()[0] for a keras model.
    strides (int): strides of the transposed convolution operation
    padding (str): padding of the transposed convolution operation. 'valid' or 'same' are supported.

Returns:
    numpy.ndarray: output tensor with batch size. (batch size, height, channels)
'''
def conv1d_transpose(inputs, kernel, strides=1, padding='valid'):
    n_batches, n_height, n_channels = inputs.shape
    outputs = np.zeros((n_batches, *out_shape((n_height, n_channels), kernel, strides=strides, padding='valid', mode='transposed')))
    strided_input = stride1d(inputs, kernel, strides=strides, padding='valid', mode='transposed')
    unrolled_kernel = unroll_kernel1d((n_height, n_channels), kernel, strides=strides, padding='valid', mode='transposed')
    _, n_convs, n_filters, n_strided_inp = unrolled_kernel.shape
    assert n_strided_inp == strided_input.shape[1]
    for batch in range(n_batches):
        for ch in range(n_channels):
            flat_inp = np.zeros((n_strided_inp, 1))
            flat_inp[:, 0] = strided_input[batch, :, ch]
            for f in range(n_filters):
                outputs[batch, :, f] += np.matmul(unrolled_kernel[ch, :, f, :], flat_inp).flatten()
    return padding1d(outputs, kernel, strides=strides, padding=padding, mode='transposed')


if __name__ == '__main__':
    for _ in range(100):
        nb = np.random.randint(1, 10)
        nh = np.random.randint(2, 50)
        nc = np.random.randint(1, 50)
        nf = np.random.randint(1, 50)
        nk = np.random.randint(1, nh)
        strides = np.random.randint(1, max(nk, 2))
        if np.random.randint(2):
            padding = 'valid'
        else:
            padding = 'same'

        if np.random.randint(2):
            mode = 'normal'
        else:
            mode = 'transposed'

        t_a = keras.layers.Input((nh, nc))
        if mode == 'normal':
            t_b = keras.layers.Conv1D(filters=nf, kernel_size=nk, padding=padding, strides=strides)(t_a)
        elif mode == 'transposed':
            t_b = keras.layers.Conv1DTranspose(filters=nf, kernel_size=nk, padding=padding, strides=strides)(t_a)
        mod = keras.models.Model(inputs=t_a, outputs=t_b)
        ker = mod.layers[1].get_weights()[0]
        inp = np.random.random((nb, nh, nc))
        out = mod.predict(inp)
        try:
            calc_out_shape = out_shape((nh, nc), ker, padding=padding, strides=strides, mode=mode)
        except BaseException:
            print('-'*50)
            print('Python Error in calculating output shape')
            traceback.print_exc()
            error = True
        
        error = False
        if calc_out_shape != out.shape[1:]:
            print('-'*50)
            print('Error in calculating output shape')
            error = True
        
        try:
            if mode == 'normal':
                out2 = conv1d(inp, ker, strides=strides, padding=padding)
            elif mode == 'transposed':
                out2 = conv1d_transpose(inp, ker, strides=strides, padding=padding)
        except BaseException:
            print('-'*50)
            print('Python Error in calculating output')
            traceback.print_exc()
            error = True
        
        if out.shape != out2.shape:
            print('-'*50)
            print('Error in returned output shape')
            error = True
        elif np.abs(out - out2).max() > 3e-6:
            print('-'*50)
            print('Error in output values')
            error = True
        
        if error:
            print('Batch size:', nb)
            print('Input shape:', (nh, nc))
            print('Number of filters:', nf)
            print('Kernel size:', nk)
            print('Strides:', strides)
            print('Padding:', padding)
            print('Mode:', mode)
            print('Expected output shape:', out.shape[1:])
            print('Calculated output shape:', calc_out_shape)
            print('Returned output shape:', out2.shape[1:])
            print('Output mismatch error:', np.abs(out - out2).max())
            break
    if not error:
        print('All tests passed!')