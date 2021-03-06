classdef Sigmoid < BaseLayer
    %Sigmoid Summary of this class goes here
    % Reference: https://github.com/leonardoaraujosantos/DLMatFramework/blob/master/learn/cs231n/assignment2/cs231n/layers.py
    
    properties (Access = 'protected')
        weights
        biases
        activations
        config
        previousInput
        name
        index
        activationShape
        inputLayer
    end
    
    methods (Access = 'public')
        function [obj] = Sigmoid(name, index, inLayer)
            obj.name = name;
            obj.index = index;
            obj.inputLayer = inLayer;
            % Relu does not change the shape of it's output
            obj.activationShape = obj.inputLayer.getActivationShape();
        end
        
        function [activations] = ForwardPropagation(obj, input, weights, bias)
            obj.previousInput = input;
            activations = (1./(1+exp(-input)));
            obj.activations = activations;
        end
        
        function [gradient] = BackwardPropagation(obj, dout)
            dout = dout.input;
            t = (1./(1+exp(-obj.previousInput)));
            d_sigm  = (t .* (1 - t));
            dx = dout .* d_sigm;
            gradient.input = dx;
            
            if obj.doGradientCheck
                evalGrad = obj.EvalBackpropNumerically(dout);
                diff_Input = sum(abs(evalGrad.input(:) - gradient.input(:)));                
                diff_vec = [diff_Input]; 
                diff = sum(diff_vec);
                if diff > 0.0001
                    msgError = sprintf('%s gradient failed!\n',obj.name);
                    error(msgError);
                else
                    %fprintf('%s gradient passed!\n',obj.name);
                end
            end
        end
        
        function gradient = EvalBackpropNumerically(obj, dout)
            % Fully connected layers has 3 inputs so we have 3 gradients
            sigm_x = @(x) obj.ForwardPropagation(x,obj.weights, obj.biases);            
            
            % Evaluate
            gradient.input = GradientCheck.Eval(sigm_x,obj.previousInput, dout);            
        end
    end
    
end

