import torch
import logging

logger = logging.getLogger(__name__)

def enable_channels_last(model):
    """
    Sets the model memory format to channels_last for better CPU performance.
    """
    if model is not None:
        model.to(memory_format=torch.channels_last)
        logger.info("Enabled channels_last memory format for model.")
    return model

def apply_torch_compile(model):
    """
    Applies torch.compile to the model if available (PyTorch 2.0+).
    """
    try:
        if hasattr(torch, 'compile'):
            model = torch.compile(model)
            logger.info("Applied torch.compile to model.")
    except Exception as e:
        logger.warning(f"Could not apply torch.compile: {e}")
    return model

def onnx_export_stub():
    """
    Stub for future ONNX export functionality.
    """
    logger.info("ONNX export stub called. Functionality not yet implemented.")
    pass

def set_cpu_optimizations():
    """
    Sets global CPU-specific optimizations for PyTorch.
    """
    # Set precision for matrix multiplications
    if hasattr(torch, 'set_float32_matmul_precision'):
        torch.set_float32_matmul_precision("medium")
        logger.info("Set float32 matmul precision to 'medium'.")
    
    # Use multiple threads if available
    if torch.get_num_threads() > 1:
        logger.info(f"PyTorch using {torch.get_num_threads()} threads.")
    
    logger.info("Global CPU optimizations applied.")
