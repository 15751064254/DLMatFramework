classdef DeepLearningModel < handle
    %DEEPLEARNINGMODEL Summary of this class goes here
    % References:
    % https://github.com/leonardoaraujosantos/DLMatFramework/blob/master/learn/cs231n/assignment2/cs231n/classifiers/fc_net.py
    % https://github.com/leonardoaraujosantos/DLMatFramework/blob/master/learn/cs231n/assignment2/cs231n/classifiers/cnn.py
    % Ex:
    % layers = LayerContainer();
    % layers <= struct('name','FC_1','type','fc');
    % layers <= struct('name','Relu_1','type','relu');
    % layers <= struct('name','FC_2','type','fc');
    % layers <= struct('name','Softmax','type','softmax');
    % layers.getNumLayers();
    % net = DeepLearningModel(layers)
    
    properties (Access = 'protected')
        layersContainer
        lossFunction
        weightsMap = containers.Map('KeyType','char','ValueType','any');
        BiasMap = containers.Map('KeyType','char','ValueType','any');
        gradWeightsMap = containers.Map('KeyType','char','ValueType','any');
        gradBiasMap = containers.Map('KeyType','char','ValueType','any');
        regEffect = 0;
        isTraining = false;
    end
    
    methods (Access = 'protected')
        function initWeights(obj)
            for idxLayer=2:obj.layersContainer.getNumLayers()
                currLayer = obj.layersContainer.getLayerFromIndex(idxLayer);
                shapeInput = currLayer.getInputLayer().getActivationShape();
                layerName = currLayer.getName();
                if isa(currLayer,'FullyConnected') || isa(currLayer,'ConvolutionLayer')
                    if isa(currLayer,'FullyConnected')
                        fan_in = abs(prod(shapeInput));
                        fan_out = currLayer.getNumOutput();
                        obj.weightsMap(layerName) = single(randn(fan_in,fan_out) / sqrt(fan_in));
                        obj.BiasMap(layerName) = single(zeros(1,currLayer.getNumOutput()));
                    else
                        % Convolution layer
                        fan_in = abs(prod(shapeInput));
                        C = shapeInput(3);
                        [kernel] = currLayer.getFilterSpatialDims();
                        F = currLayer.getNumOutput();
                        obj.weightsMap(layerName) = single(randn(kernel(1),kernel(2),C,F) / sqrt(fan_in));
                        obj.BiasMap(layerName) = single(zeros(F,1));
                    end
                else
                    % Some layers (ie Relu, Softmax) has no parameters
                    obj.weightsMap(layerName) = [];
                    obj.BiasMap(layerName) = [];
                    
                    % On the batchnorm layer the weight(gammas) should be
                    % initialized with ones and the bias(betas) as zeros
                    if isa(currLayer,'BatchNorm') || isa(currLayer,'SpatialBatchNorm')
                        if isa(currLayer,'SpatialBatchNorm')
                            C = shapeInput(3);
                            obj.weightsMap(layerName) = single(ones(1,C));
                            obj.BiasMap(layerName) = single(zeros(1,C));
                        else
                            obj.weightsMap(layerName) = single(ones(1,abs(prod(shapeInput))));
                            obj.BiasMap(layerName) = single(zeros(1,abs(prod(shapeInput))));
                        end
                    end
                end
            end
        end
    end
    
    methods (Access = 'public')
        function obj = DeepLearningModel(layerCont, lossType)
            obj.layersContainer = layerCont;
            obj.lossFunction = LossFactory.GetLoss(lossType);
            %% Initialize weights and biases
            obj.initWeights();
        end
        
        function [scores] = Predict(obj, X)
            % Get input signals coordinates
            [rows,cols,depth,batch] = size(X);
            
            % Iterate forward on the graph
            currInput = X;
            for idxLayer=2:obj.layersContainer.getNumLayers()
                currLayer = obj.layersContainer.getLayerFromIndex(idxLayer);
                layerName = currLayer.getName();
                if isa(currLayer,'Dropout') || isa(currLayer,'BatchNorm') || isa(currLayer,'SpatialBatchNorm')
                    currLayer.IsTraining(obj.isTraining);
                end
                currInput = currLayer.ForwardPropagation(currInput,obj.weightsMap(layerName),obj.BiasMap(layerName));
            end
            scores = currInput;
        end
        
        function [lossVal, gradients] = Loss(obj, X, Y)
            %% Do the forward propagation
            scores = obj.Predict(X);
            
            %% Get loss and gradient of the loss w.r.t to the scores
            [data_loss, grad_loss] = obj.lossFunction.GetLossAndGradients(scores, Y);
            
            %% Backprop
            % Start with gradient of loss w.r.t correct class probability
            % Also to save loop time we get the square sum of the weights
            % to be used on the regularization
            squared_W_reg = [];
            currDout.input = grad_loss;
            % Start by the last layer before Softmax
            for idxLayer=obj.layersContainer.getNumLayers()-1:-1:1
                currLayer = obj.layersContainer.getLayerFromIndex(idxLayer);
                % There is no backprop on the input layer
                if isa(currLayer,'InputLayer')
                    continue;
                end
                layerName = currLayer.getName();
                currDout = currLayer.BackwardPropagation(currDout);
                % Save gradients on parametrizes layers
                if isa(currLayer,'FullyConnected') || isa(currLayer,'BatchNorm') || isa(currLayer,'ConvolutionLayer') || isa(currLayer,'SpatialBatchNorm')
                    obj.gradWeightsMap(layerName) = currDout.weight;
                    obj.gradBiasMap(layerName) = currDout.bias;
                    if (obj.regEffect ~= 0)
                        W_flat = currLayer.getWeights; W_flat = W_flat(:);
                        squared_W_reg(end+1) = 0.5 * obj.regEffect * sum(W_flat .* W_flat);
                    end
                end
            end
            
            %% Calculate regularization part
            reg_loss = sum(squared_W_reg);
            
            %% Return loss (Including regularization part) and gradients
            lossVal = data_loss + reg_loss;
            gradients.weights = obj.gradWeightsMap;
            gradients.bias = obj.gradBiasMap;
        end
        
        function ShowStructure(obj)
            obj.layersContainer.ShowStructure();
        end
        
        % Remember that those maps are passed by reference so the changes
        % made on the map returned by those functions will be affected on
        % this object
        function weights = getWeights(obj)
            weights = obj.weightsMap;
        end
        
        function bias = getBias(obj)
            bias = obj.BiasMap;
        end
        
        function weightsGrad = getWeightsGradients(obj)
            weightsGrad = obj.gradWeightsMap;
        end
        
        function biasGrad = getBiasGradients(obj)
            biasGrad = obj.gradBiasMap;
        end
        
        function layers = getLayers(obj)
            layers = obj.layersContainer.getLayerMap();
        end
        
        function L2Regularization(obj,regVal)
            obj.regEffect = regVal;
        end
        
        function EnableGradientCheck(obj, flag)
            cellLayers = obj.layersContainer.getAllLayers();
            for idxLayer = 1:numel(cellLayers)
                currLayer =  cellLayers{idxLayer};
                currLayer.EnableGradientCheck(flag);
            end
        end
        
        function IsTraining(obj, flag)
            obj.isTraining = flag;
        end
    end
    
end

