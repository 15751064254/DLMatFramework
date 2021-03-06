import numpy as np


def affine_forward(x, w, b):
  """
  Computes the forward pass for an affine (fully-connected) layer.

  The input x has shape (N, d_1, ..., d_k) and contains a minibatch of N
  examples, where each example x[i] has shape (d_1, ..., d_k). We will
  reshape each input into a vector of dimension D = d_1 * ... * d_k, and
  then transform it to an output vector of dimension M.

  Inputs:
  - x: A numpy array containing input data, of shape (N, d_1, ..., d_k)
  - w: A numpy array of weights, of shape (D, M)
  - b: A numpy array of biases, of shape (M,)
  
  Returns a tuple of:
  - out: output, of shape (N, M)
  - cache: (x, w, b)
  """
  out = None
  #############################################################################
  # TODO: Implement the affine forward pass. Store the result in out. You     #
  # will need to reshape the input into rows.                                 #
  #############################################################################
  # Get number of items
  N = x.shape[0]

  # Reshape to have N rows and as many collumns as needed
  x_temp = x.reshape(N,-1)

  # Simple linear operation, after this step just cache the inputs
  out = x_temp.dot(w) + b
  #############################################################################
  #                             END OF YOUR CODE                              #
  #############################################################################
  cache = (x, w, b)
  return out, cache


def affine_backward(dout, cache):
  """
  Computes the backward pass for an affine layer.

  Inputs:
  - dout: Upstream derivative, of shape (N, M)
  - cache: Tuple of:
    - x: Input data, of shape (N, d_1, ... d_k)
    - w: Weights, of shape (D, M)

  Returns a tuple of:
  - dx: Gradient with respect to x, of shape (N, d1, ..., d_k)
  - dw: Gradient with respect to w, of shape (D, M)
  - db: Gradient with respect to b, of shape (M,)
  """
  x, w, b = cache
  dx, dw, db = None, None, None
  #############################################################################
  # TODO: Implement the affine backward pass.                                 #
  #############################################################################
  # Get number of items
  N = x.shape[0]

  # Reshape to have N rows and as many collumns as needed
  x_temp = x.reshape(N,-1)

  # Calculate the gradients, for reference check:
  # https://leonardoaraujosantos.gitbooks.io/artificial-inteligence/content/fc_layer.html
  # http://cs231n.github.io/optimization-2/#mat
  db = np.sum(dout, axis = 0)
  dw = x_temp.T.dot(dout)
  dx = dout.dot(w.T).reshape(x.shape)
  #############################################################################
  #                             END OF YOUR CODE                              #
  #############################################################################
  return dx, dw, db


def relu_forward(x):
  """
  Computes the forward pass for a layer of rectified linear units (ReLUs).

  Input:
  - x: Inputs, of any shape

  Returns a tuple of:
  - out: Output, of the same shape as x
  - cache: x
  """
  out = None
  #############################################################################
  # TODO: Implement the ReLU forward pass.                                    #
  #############################################################################
  # Simple Relu forward propagation
  relu_func = lambda x: x * (x > 0).astype(float)
  out = relu_func(x)
  #############################################################################
  #                             END OF YOUR CODE                              #
  #############################################################################
  cache = x
  return out, cache


def relu_backward(dout, cache):
  """
  Computes the backward pass for a layer of rectified linear units (ReLUs).

  Input:
  - dout: Upstream derivatives, of any shape
  - cache: Input x, of same shape as dout

  Returns:
  - dx: Gradient with respect to x
  """
  dx, x = None, cache
  #############################################################################
  # TODO: Implement the ReLU backward pass.                                   #
  #############################################################################
  # The backward pass is just dout on the cases where x were positive (kind of mask)
  dx = dout * (x >= 0)
  #############################################################################
  #                             END OF YOUR CODE                              #
  #############################################################################
  return dx


def batchnorm_forward(x, gamma, beta, bn_param):
  """
  Forward pass for batch normalization.
  
  During training the sample mean and (uncorrected) sample variance are
  computed from minibatch statistics and used to normalize the incoming data.
  During training we also keep an exponentially decaying running mean of the mean
  and variance of each feature, and these averages are used to normalize data
  at test-time.

  At each timestep we update the running averages for mean and variance using
  an exponential decay based on the momentum parameter:

  running_mean = momentum * running_mean + (1 - momentum) * sample_mean
  running_var = momentum * running_var + (1 - momentum) * sample_var

  Note that the batch normalization paper suggests a different test-time
  behavior: they compute sample mean and variance for each feature using a
  large number of training images rather than using a running average. For
  this implementation we have chosen to use running averages instead since
  they do not require an additional estimation step; the torch7 implementation
  of batch normalization also uses running averages.

  Input:
  - x: Data of shape (N, D)
  - gamma: Scale parameter of shape (D,)
  - beta: Shift paremeter of shape (D,)
  - bn_param: Dictionary with the following keys:
    - mode: 'train' or 'test'; required
    - eps: Constant for numeric stability
    - momentum: Constant for running mean / variance.
    - running_mean: Array of shape (D,) giving running mean of features
    - running_var Array of shape (D,) giving running variance of features

  Returns a tuple of:
  - out: of shape (N, D)
  - cache: A tuple of values needed in the backward pass
  """
  mode = bn_param['mode']
  eps = bn_param.get('eps', 1e-5)
  momentum = bn_param.get('momentum', 0.9)

  N, D = x.shape
  running_mean = bn_param.get('running_mean', np.zeros(D, dtype=x.dtype))
  running_var = bn_param.get('running_var', np.zeros(D, dtype=x.dtype))

  out, cache = None, None
  if mode == 'train':
    #############################################################################
    # TODO: Implement the training-time forward pass for batch normalization.   #
    # Use minibatch statistics to compute the mean and variance, use these      #
    # statistics to normalize the incoming data, and scale and shift the        #
    # normalized data using gamma and beta.                                     #
    #                                                                           #
    # You should store the output in the variable out. Any intermediates that   #
    # you need for the backward pass should be stored in the cache variable.    #
    #                                                                           #
    # You should also use your computed sample mean and variance together with  #
    # the momentum variable to update the running mean and running variance,    #
    # storing your result in the running_mean and running_var variables.        #
    #############################################################################
    # Forward pass on trainning
    # Reference:
    # https://kratzert.github.io/2016/02/12/understanding-the-gradient-flow-through-the-batch-normalization-layer.html
    # This version is more expanded but facilitate discover backpropagation
    # Step 1 - calculate the mean
    mu = 1 / float(N) * np.sum(x, axis=0)
    # Step 2 - subtract the mean from the input x
    xmu = x - mu
    # Step 3 - calculate the denominator part
    carre = xmu**2
    # Step 4 - calculate the variance
    var = 1 / float(N) * np.sum(carre, axis=0)
    # Step 5 - Add eps(small number) for numerical stability
    sqrtvar = np.sqrt(var + eps)
    # Step 6 - Invert the square root
    invvar = 1. / sqrtvar
    # Step 7 - Calculate the normalization part
    va2 = xmu * invvar
    va3 = gamma * va2
    # Step 8 - Output
    out = va3 + beta

    # More compact form using numpy mean and variance commands
    # Reference:
    # https://github.com/ncchen55414/Winter-2016-CS231N/blob/master/Assignment2/cs231n/layers.py
    #sample_mean = np.mean(x, axis = 0)
    #sample_var = np.var(x, axis = 0)
    #x_normalized = (x-sample_mean) / np.sqrt(sample_var + eps)
    #out = gamma*x_normalized + beta
    #running_mean = momentum * running_mean + (1 - momentum) * sample_mean
    #running_var = momentum * running_var + (1 - momentum) * sample_var

    # Calculate the running mean and variance that will be used during prediction
    running_mean = momentum * running_mean + (1.0 - momentum) * mu
    running_var = momentum * running_var + (1.0 - momentum) * var


    # Store the values to be used later on other phases
    cache = (mu, xmu, carre, var, sqrtvar, invvar, va2, va3, gamma, beta, x, bn_param)
    #cache = (x, sample_mean, sample_var, x_normalized, beta, gamma, eps)

    #############################################################################
    #                             END OF YOUR CODE                              #
    #############################################################################
  elif mode == 'test':
    #############################################################################
    # TODO: Implement the test-time forward pass for batch normalization. Use   #
    # the running mean and variance to normalize the incoming data, then scale  #
    # and shift the normalized data using gamma and beta. Store the result in   #
    # the out variable.                                                         #
    #############################################################################
    # Load cached parameters
    # TODO: Discussing wih the team (Peng, David) they shown me that probably it's possible
    # to merge all those operations on the previous layer weights considering the fact that
    # the operations before the batch norm (FC, CONV) and the output transformation of the batchnorm itself
    # can be considered linear.
    # Reference:
    # https://github.com/vlfeat/matconvnet/blob/master/examples/imagenet/cnn_imagenet_deploy.m#L176
    running_mean = bn_param['running_mean']
    running_var = bn_param['running_var']
    xbar = (x-running_mean)/np.sqrt(running_var+eps)
    out = gamma*xbar + beta
    #############################################################################
    #                             END OF YOUR CODE                              #
    #############################################################################
  else:
    raise ValueError('Invalid forward batchnorm mode "%s"' % mode)

  # Store the updated running means back into bn_param
  bn_param['running_mean'] = running_mean
  bn_param['running_var'] = running_var

  return out, cache


def batchnorm_backward(dout, cache):
  """
  Backward pass for batch normalization.
  
  For this implementation, you should write out a computation graph for
  batch normalization on paper and propagate gradients backward through
  intermediate nodes.
  
  Inputs:
  - dout: Upstream derivatives, of shape (N, D)
  - cache: Variable of intermediates from batchnorm_forward.
  
  Returns a tuple of:
  - dx: Gradient with respect to inputs x, of shape (N, D)
  - dgamma: Gradient with respect to scale parameter gamma, of shape (D,)
  - dbeta: Gradient with respect to shift parameter beta, of shape (D,)
  """
  dx, dgamma, dbeta = None, None, None
  #############################################################################
  # TODO: Implement the backward pass for batch normalization. Store the      #
  # results in the dx, dgamma, and dbeta variables.                           #
  #############################################################################
  (mu, xmu, carre, var, sqrtvar, invvar, va2, va3, gamma, beta, x, bn_param) = cache
  eps = bn_param.get('eps', 1e-5)
  N, D = dout.shape

  # Backprop step 8
  dva3 = dout
  dbeta = np.sum(dout, axis=0)

  # Backprop step 7
  dva2 = gamma * dva3
  dgamma = np.sum(va2 * dva3, axis=0)

  # Backprop step 6
  dxmu = invvar * dva2
  dinvvar = np.sum(xmu * dva2, axis=0)

  # Backprop step 5
  dsqrtvar = -1.0 / (sqrtvar**2) * dinvvar

  # Backprop step 4
  dvar = 0.5 * (var + eps)**(-0.5) * dsqrtvar

  # Backprop step 3
  dcarre = 1 / float(N) * np.ones((carre.shape)) * dvar

  # Backprop step 2
  dxmu += 2 * xmu * dcarre

  # Backprop step 1
  dx = dxmu
  dmu = -np.sum(dxmu, axis=0)
  dx += 1 / float(N) * np.ones((dxmu.shape)) * dmu

  return dx, dgamma, dbeta

  #############################################################################
  #                             END OF YOUR CODE                              #
  #############################################################################

  return dx, dgamma, dbeta


def batchnorm_backward_alt(dout, cache):
  """
  Alternative backward pass for batch normalization.
  
  For this implementation you should work out the derivatives for the batch
  normalizaton backward pass on paper and simplify as much as possible. You
  should be able to derive a simple expression for the backward pass.
  
  Note: This implementation should expect to receive the same cache variable
  as batchnorm_backward, but might not use all of the values in the cache.
  
  Inputs / outputs: Same as batchnorm_backward
  """
  dx, dgamma, dbeta = None, None, None
  #############################################################################
  # TODO: Implement the backward pass for batch normalization. Store the      #
  # results in the dx, dgamma, and dbeta variables.                           #
  #                                                                           #
  # After computing the gradient with respect to the centered inputs, you     #
  # should be able to compute gradients with respect to the inputs in a       #
  # single statement; our implementation fits on a single 80-character line.  #
  #############################################################################
  # http://cthorey.github.io./backpropagation/
  mu, xmu, carre, var, sqrtvar, invvar, va2, va3, gamma, beta, x, bn_param = cache
  eps = bn_param.get('eps', 1e-5)
  N, D = dout.shape

  dbeta = np.sum(dout, axis=0)
  dgamma = np.sum((x - mu) * (1/np.sqrt(var + eps)) * dout, axis=0)
  dx = (1. / N) * gamma * (1/np.sqrt(var + eps)) * (N * dout - np.sum(dout, axis=0) - (x - mu) * (1/(var + eps)) * np.sum(dout * (x - mu), axis=0))
  #############################################################################
  #                             END OF YOUR CODE                              #
  #############################################################################
  
  return dx, dgamma, dbeta


def dropout_forward(x, dropout_param):
  """
  Performs the forward pass for (inverted) dropout.

  Inputs:
  - x: Input data, of any shape
  - dropout_param: A dictionary with the following keys:
    - p: Dropout parameter. We drop each neuron output with probability p.
    - mode: 'test' or 'train'. If the mode is train, then perform dropout;
      if the mode is test, then just return the input.
    - seed: Seed for the random number generator. Passing seed makes this
      function deterministic, which is needed for gradient checking but not in
      real networks.

  Outputs:
  - out: Array of the same shape as x.
  - cache: A tuple (dropout_param, mask). In training mode, mask is the dropout
    mask that was used to multiply the input; in test mode, mask is None.
  """
  p, mode = dropout_param['p'], dropout_param['mode']
  if 'seed' in dropout_param:
    np.random.seed(dropout_param['seed'])

  mask = None
  out = None

  if mode == 'train':
    ###########################################################################
    # TODO: Implement the training phase forward pass for inverted dropout.   #
    # Store the dropout mask in the mask variable.                            #
    ###########################################################################
    # Reference: Chainer (Python deep learning library)
    # https://github.com/pfnet/chainer/blob/a6a4e373071c6be3215bdc1367cb3d40fbcd8a2a/chainer/functions/noise/dropout.py
    # Create an apply mask (ie: with probability p=0.5) for turn-off half neurons. We scale
    # all by p to avoid having to multiply by p on backpropagation. This technique is called inverted dropout
    # Create mask
    [N,D] = x.shape
    # mask = (np.random.rand(N,D) < (1-p))/(1-p)
    mask = (np.random.rand(N,D) >= p)/(1-p) # (Slightly better results)
    # Apply mask
    out = x * mask
    ###########################################################################
    #                            END OF YOUR CODE                             #
    ###########################################################################
  elif mode == 'test':
    ###########################################################################
    # TODO: Implement the test phase forward pass for inverted dropout.       #
    ###########################################################################
    # During prediction no mask is used, it's completely transparent
    mask = None
    out = x
    ###########################################################################
    #                            END OF YOUR CODE                             #
    ###########################################################################

  cache = (dropout_param, mask)
  out = out.astype(x.dtype, copy=False)

  return out, cache


def dropout_backward(dout, cache):
  """
  Perform the backward pass for (inverted) dropout.

  Inputs:
  - dout: Upstream derivatives, of any shape
  - cache: (dropout_param, mask) from dropout_forward.
  """
  dropout_param, mask = cache
  mode = dropout_param['mode']
  
  dx = None
  if mode == 'train':
    ###########################################################################
    # TODO: Implement the training phase backward pass for inverted dropout.  #
    ###########################################################################
    # Just backpropagate dout from the neurons that were used during the dropout
    dx = dout * mask
    ###########################################################################
    #                            END OF YOUR CODE                             #
    ###########################################################################
  elif mode == 'test':
    dx = dout
  return dx


def conv_forward_naive(x, w, b, conv_param):
  """
  A naive implementation of the forward pass for a convolutional layer.

  The input consists of N data points, each with C channels, height H and width
  W. We convolve each input with F different filters, where each filter spans
  all C channels and has height HH and width HH.

  Input:
  - x: Input data of shape (N, C, H, W)
  - w: Filter weights of shape (F, C, HH, WW)
  - b: Biases, of shape (F,)
  - conv_param: A dictionary with the following keys:
    - 'stride': The number of pixels between adjacent receptive fields in the
      horizontal and vertical directions.
    - 'pad': The number of pixels that will be used to zero-pad the input.

  Returns a tuple of:
  - out: Output data, of shape (N, F, H', W') where H' and W' are given by
    H' = 1 + (H + 2 * pad - HH) / stride
    W' = 1 + (W + 2 * pad - WW) / stride
  - cache: (x, w, b, conv_param)
  """
  out = None
  #############################################################################
  # TODO: Implement the convolutional forward pass.                           #
  # Hint: you can use the function np.pad for padding.                        #
  #############################################################################
  # Get input shapes
  N, C, H, W = x.shape

  # Get weight shapes
  F, _, HH, WW = w.shape

  # Get convolution layer parameters
  stride = conv_param['stride']
  pad = conv_param['pad']

  # Calculate output dimensions
  H_out = 1 + (H + 2 * pad - HH) / stride
  W_out = 1 + (W + 2 * pad - WW) / stride
  # Alocate memory for output
  out = np.zeros((N,F,H_out,W_out))

  # Pad the input
  x_pad = np.zeros((N,C,H+2*pad,W+2*pad))
  # Pad every channel on every image on the batch
  for n in range(N):
    for c in range(C):
      x_pad[n,c] = np.pad(x[n,c],(1,1),'constant', constant_values=(0,0))

  # This version will be really slow
  # Iterate for every batch
  for n in range(N):
      # Iterate on every rows of the output
      for i in range(H_out):
        # Iterate on every cols of the output
        for j in range(W_out):
          # Iterate on every filter of the conv layer
          for f in range(F):
            # Select padded input
            current_x_matrix = x_pad[n,:, i*stride: i*stride+HH, j*stride:j*stride+WW]
            # Select filter
            current_filter = w[f]
            # Apply filtering window
            out[n,f,i,j] = np.sum(current_x_matrix*current_filter)
          out[n,:,i,j] = out[n,:,i,j]+b


  #############################################################################
  #                             END OF YOUR CODE                              #
  #############################################################################
  cache = (x, w, b, conv_param)
  return out, cache


def conv_backward_naive(dout, cache):
  """
  A naive implementation of the backward pass for a convolutional layer.

  Inputs:
  - dout: Upstream derivatives.
  - cache: A tuple of (x, w, b, conv_param) as in conv_forward_naive

  Returns a tuple of:
  - dx: Gradient with respect to x
  - dw: Gradient with respect to w
  - db: Gradient with respect to b
  """
  dx, dw, db = None, None, None
  #############################################################################
  # TODO: Implement the convolutional backward pass.                          #
  #############################################################################
  # Get the gradients for dx,dw,db. Remember that the dimension of the gradients
  # are the same as the dimensions of the original signams (x,w,b)
  # Get cached inputs (including weights and biases from the forward propagation)
  x, w, b, conv_param = cache

  # Get convolution parameters
  stride = conv_param['stride']
  pad = conv_param['pad']

  # Get shapes
  N, C, H, W = x.shape
  F, _, HH, WW = w.shape
  # dout is the previous gradient
  _,_,H_out,W_out = dout.shape

  # Do padding to correctly calculate the gradients
  x_pad = np.zeros((N,C,H+2,W+2))
  for n in range(N):
    for c in range(C):
      x_pad[n,c] = np.pad(x[n,c],(1,1),'constant', constant_values=(0,0))

  # Get bias gradient
  db = np.zeros((F))
  for n in range(N):
    for i in range(H_out):
      for j in range(W_out):
          db = db + dout[n,:,i,j]

  # Initialize dw, dx_pad
  dw = np.zeros(w.shape)
  dx_pad = np.zeros(x_pad.shape)

  # Get weight and input gradients
  # For each image on the batch
  for n in range(N):
    # For each filter
    for f in range(F):
      # For each row
      for i in range(H_out):
        # For each col
        for j in range(W_out):
          current_x_matrix = x_pad[n,:, i*stride: i*stride+HH, j*stride:j*stride+WW]
          dw[f] = dw[f] + dout[n,f,i,j]* current_x_matrix
          dx_pad[n,:, i*stride: i*stride+HH, j*stride:j*stride+WW] += w[f]*dout[n,f,i,j]

  # The dx gradient has the same dimensions as it's original x signal
  dx = dx_pad[:,:,1:H+1,1:W+1]
  #############################################################################
  #                             END OF YOUR CODE                              #
  #############################################################################
  return dx, dw, db


def max_pool_forward_naive(x, pool_param):
  """
  A naive implementation of the forward pass for a max pooling layer.

  Inputs:
  - x: Input data, of shape (N, C, H, W)
  - pool_param: dictionary with the following keys:
    - 'pool_height': The height of each pooling region
    - 'pool_width': The width of each pooling region
    - 'stride': The distance between adjacent pooling regions

  Returns a tuple of:
  - out: Output data
  - cache: (x, pool_param)
  """
  out = None
  #############################################################################
  # TODO: Implement the max pooling forward pass                              #
  #############################################################################
  # Get input shapes
  N, C, H, W = x.shape

  # Get maxpool parameters
  pool_height = pool_param['pool_height']
  pool_width = pool_param['pool_width']
  stride = pool_param['stride']

  # Calculate the result output sizes
  H_out = 1 + (H - pool_height) / stride
  W_out = 1 + (W - pool_width) / stride
  # Also allocate memory
  out = np.zeros((N,C,H_out,W_out))

  # Slow very slow version
  # For each image on the batch
  for n in xrange(N):
    # For each channel
    for depth in xrange(C):
      # For each row on the input jumping stride pixels vertically
      for r in xrange(0,H,stride):
        # For each col on the input jumpring stride pixels horizontally
        for c in xrange(0,W,stride):
          # Get the biggest value on the input window and put on the output
          out[n,depth,r/stride,c/stride] = np.max(x[n,depth,r:r+pool_height,c:c+pool_width])
  #############################################################################
  #                             END OF YOUR CODE                              #
  #############################################################################
  cache = (x, pool_param)
  return out, cache


def max_pool_backward_naive(dout, cache):
  """
  A naive implementation of the backward pass for a max pooling layer.

  Inputs:
  - dout: Upstream derivatives
  - cache: A tuple of (x, pool_param) as in the forward pass.

  Returns:
  - dx: Gradient with respect to x
  """
  dx = None
  #############################################################################
  # TODO: Implement the max pooling backward pass                             #
  #############################################################################
  # Get cached input
  x, pool_param = cache

  # Get maxpooling parameters
  pool_height = pool_param['pool_height']
  pool_width = pool_param['pool_width']
  stride = pool_param['stride']

  # Get shape of previous(backpropagation input) gradient
  N,C,H_out,W_out = dout.shape

  # Initialize the maxpool input gradient
  dx = np.zeros(x.shape)

  # Again very slow implementation,
  for n in xrange(N):
    for depth in xrange(C):
      for r in xrange(H_out):
        for c in range(W_out):
          # Get window and calculate the mask
          x_pool = x[n, depth, r*stride:r*stride+pool_height, c*stride:c*stride+pool_width]
          mask = (x_pool == np.max(x_pool))
          # Now just apply the mask to dout
          dx[n, depth, r*stride:r*stride+pool_height,c*stride:c*stride+pool_width] = mask*dout[n, depth, r, c]
  #############################################################################
  #                             END OF YOUR CODE                              #
  #############################################################################
  return dx


def spatial_batchnorm_forward(x, gamma, beta, bn_param):
  """
  Computes the forward pass for spatial batch normalization.
  
  Inputs:
  - x: Input data of shape (N, C, H, W)
  - gamma: Scale parameter, of shape (C,)
  - beta: Shift parameter, of shape (C,)
  - bn_param: Dictionary with the following keys:
    - mode: 'train' or 'test'; required
    - eps: Constant for numeric stability
    - momentum: Constant for running mean / variance. momentum=0 means that
      old information is discarded completely at every time step, while
      momentum=1 means that new information is never incorporated. The
      default of momentum=0.9 should work well in most situations.
    - running_mean: Array of shape (D,) giving running mean of features
    - running_var Array of shape (D,) giving running variance of features
    
  Returns a tuple of:
  - out: Output data, of shape (N, C, H, W)
  - cache: Values needed for the backward pass
  """
  out, cache = None, None

  #############################################################################
  # TODO: Implement the forward pass for spatial batch normalization.         #
  #                                                                           #
  # HINT: You can implement spatial batch normalization using the vanilla     #
  # version of batch normalization defined above. Your implementation should  #
  # be very short; ours is less than five lines.                              #
  #############################################################################
  # Get input shapes
  N, C, H, W = x.shape

  # Call normal batchnorm forward with trainsposed and reshaped input
  x_T = x.transpose((0,2,3,1))
  x_flat = x_T.reshape(-1, C)
  out, cache = batchnorm_forward(x_flat, gamma, beta, bn_param)

  # Reshape/transpose back the to normal input dimensions
  out_reshape = out.reshape((N,H,W,C))
  out = out_reshape.transpose(0,3,1,2)
  #############################################################################
  #                             END OF YOUR CODE                              #
  #############################################################################

  return out, cache


def spatial_batchnorm_backward(dout, cache):
  """
  Computes the backward pass for spatial batch normalization.
  
  Inputs:
  - dout: Upstream derivatives, of shape (N, C, H, W)
  - cache: Values from the forward pass
  
  Returns a tuple of:
  - dx: Gradient with respect to inputs, of shape (N, C, H, W)
  - dgamma: Gradient with respect to scale parameter, of shape (C,)
  - dbeta: Gradient with respect to shift parameter, of shape (C,)
  """
  dx, dgamma, dbeta = None, None, None

  #############################################################################
  # TODO: Implement the backward pass for spatial batch normalization.        #
  #                                                                           #
  # HINT: You can implement spatial batch normalization using the vanilla     #
  # version of batch normalization defined above. Your implementation should  #
  # be very short; ours is less than five lines.                              #
  #############################################################################
  # Get input shapes
  N,C,H,W = dout.shape

  dout_T = dout.transpose((0,2,3,1))
  dout_flat = dout_T.reshape(-1, C)

  # Call normal batchnorm backward with trainsposed and reshaped input
  dx, dgamma, dbeta = batchnorm_backward(dout_flat, cache)

  # Reshape/transpose back the to normal input dimensions
  dx = dx.reshape((N,H,W,C)).transpose(0,3,1,2)
  #############################################################################
  #                             END OF YOUR CODE                              #
  #############################################################################

  return dx, dgamma, dbeta
  

def svm_loss(x, y):
  """
  Computes the loss and gradient using for multiclass SVM classification.

  Inputs:
  - x: Input data, of shape (N, C) where x[i, j] is the score for the jth class
    for the ith input.
  - y: Vector of labels, of shape (N,) where y[i] is the label for x[i] and
    0 <= y[i] < C

  Returns a tuple of:
  - loss: Scalar giving the loss
  - dx: Gradient of the loss with respect to x
  """
  N = x.shape[0]
  correct_class_scores = x[np.arange(N), y]
  margins = np.maximum(0, x - correct_class_scores[:, np.newaxis] + 1.0)
  margins[np.arange(N), y] = 0
  loss = np.sum(margins) / N
  num_pos = np.sum(margins > 0, axis=1)
  dx = np.zeros_like(x)
  dx[margins > 0] = 1
  dx[np.arange(N), y] -= num_pos
  dx /= N
  return loss, dx


def softmax_loss(x, y):
  """
  Computes the loss and gradient for softmax classification.

  Inputs:
  - x: Input data, of shape (N, C) where x[i, j] is the score for the jth class
    for the ith input.
  - y: Vector of labels, of shape (N,) where y[i] is the label for x[i] and
    0 <= y[i] < C

  Returns a tuple of:
  - loss: Scalar giving the loss
  - dx: Gradient of the loss with respect to x
  """
  probs = np.exp(x - np.max(x, axis=1, keepdims=True))
  probs /= np.sum(probs, axis=1, keepdims=True)
  N = x.shape[0]
  loss = -np.sum(np.log(probs[np.arange(N), y])) / N
  dx = probs.copy()
  dx[np.arange(N), y] -= 1
  dx /= N
  return loss, dx
