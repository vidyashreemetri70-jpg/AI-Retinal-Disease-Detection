"""
RetinaScan AI - PyTorch ResNet50 Model Utilities

Loads the trained PyTorch ResNet50 checkpoint and runs predictions
on uploaded retinal fundus images.

CLASS ORDER:
0 - AMD     (Age-related Macular Degeneration)
1 - DR      (Diabetic Retinopathy)
2 - DN      (Diabetic Neuropathy)
3 - MH      (Macular Hole)
4 - ODC     (Optic Disc Cupping)
5 - Normal

Model:
    ResNet50
    Input: 384 x 384
    Trainable layers: layer3, layer4, fc

Checkpoint:
    backend/saved_model/resnet50_experiment11_epoch1.pth
"""

import os
import io

import torch
import torch.nn as nn
from PIL import Image
from torchvision import models, transforms
from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# CLASS DEFINITIONS
# ============================================================

CLASS_NAMES = [
    "AMD",
    "DR",
    "DN",
    "MH",
    "ODC",
    "Normal",
]

NUM_CLASSES = len(CLASS_NAMES)


# ============================================================
# MODEL CONFIGURATION
# ============================================================

MODEL_DIR = os.path.join(
    os.path.dirname(__file__),
    "saved_model"
)

MODEL_FILENAME = os.environ.get(
    "MODEL_FILENAME",
    "resnet50_experiment11_epoch1.pth"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    MODEL_FILENAME
)

# Experiment 11 checkpoint was trained at 384x384
IMAGE_SIZE = (384, 384)

# CPU is used because the current virtual environment
# has PyTorch CPU installed.
DEVICE = torch.device("cpu")


# ============================================================
# MODEL STATE
# ============================================================

_model = None
MODEL_LOADED = False


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

# Standard ImageNet normalization.
#
# IMPORTANT:
# If the Experiment 11 training code used different
# normalization, it should be changed to exactly match it.

_transform = transforms.Compose(
    [
        transforms.Resize(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ]
)


# ============================================================
# BUILD RESNET50
# ============================================================

def _build_model():
    """
    Create the ResNet50 architecture compatible with
    the Experiment 11 checkpoint.

    The checkpoint expects the final classifier to have
    the structure:

        fc.0 -> Dropout
        fc.1 -> Linear

    Therefore, a Sequential classifier is used instead
    of a single Linear layer.
    """

    model = models.resnet50(weights=None)

    # Six retinal disease classes.
    #
    # The checkpoint contains:
    #   fc.1.weight
    #   fc.1.bias
    #
    # Therefore the classifier must be Sequential.
    model.fc = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(
            model.fc.in_features,
            NUM_CLASSES
        )
    )

    return model


# ============================================================
# LOAD MODEL
# ============================================================

def _load_model():
    """
    Load the PyTorch checkpoint.

    The checkpoint contains:
        epoch
        model_state_dict
        optimizer_state_dict
        metrics
        config
    """

    global _model, MODEL_LOADED

    # Already loaded
    if _model is not None:
        return _model

    # Check model file
    if not os.path.exists(MODEL_PATH):
        print(
            f"[model_utils] ERROR: model file not found:\n"
            f"    {MODEL_PATH}"
        )

        MODEL_LOADED = False
        return None

    try:

        print(
            f"[model_utils] Loading PyTorch model:\n"
            f"    {MODEL_PATH}"
        )

        # ----------------------------------------------------
        # Create architecture
        # ----------------------------------------------------

        model = _build_model()

        # ----------------------------------------------------
        # Load checkpoint
        # ----------------------------------------------------

        checkpoint = torch.load(
            MODEL_PATH,
            map_location=DEVICE
        )

        # ----------------------------------------------------
        # Extract model state
        # ----------------------------------------------------

        if isinstance(checkpoint, dict):

            if "model_state_dict" in checkpoint:

                state_dict = checkpoint["model_state_dict"]

            else:

                # Compatibility with a plain state_dict
                state_dict = checkpoint

        else:

            raise ValueError(
                "Unsupported checkpoint format."
            )

        # ----------------------------------------------------
        # Load weights
        # ----------------------------------------------------

        model.load_state_dict(
            state_dict,
            strict=True
        )

        # ----------------------------------------------------
        # Evaluation mode
        # ----------------------------------------------------

        model.to(DEVICE)
        model.eval()

        _model = model
        MODEL_LOADED = True

        # ----------------------------------------------------
        # Print checkpoint information
        # ----------------------------------------------------

        epoch = (
            checkpoint.get(
                "epoch",
                "unknown"
            )
            if isinstance(checkpoint, dict)
            else "unknown"
        )

        metrics = (
            checkpoint.get(
                "metrics",
                {}
            )
            if isinstance(checkpoint, dict)
            else {}
        )

        config = (
            checkpoint.get(
                "config",
                {}
            )
            if isinstance(checkpoint, dict)
            else {}
        )

        print(
            "[model_utils] Model loaded successfully."
        )

        print(
            f"[model_utils] Architecture: "
            f"{config.get('architecture', 'ResNet50')}"
        )

        print(
            f"[model_utils] Resolution: "
            f"{config.get('resolution', '384x384')}"
        )

        print(
            f"[model_utils] Checkpoint epoch: {epoch}"
        )

        if metrics:

            accuracy = metrics.get(
                "accuracy"
            )

            if accuracy is not None:

                print(
                    f"[model_utils] Checkpoint accuracy: "
                    f"{accuracy * 100:.2f}%"
                )

        return _model

    except Exception as e:

        print(
            f"[model_utils] ERROR loading PyTorch model: {e}"
        )

        MODEL_LOADED = False
        _model = None

        return None


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def _preprocess(image_bytes: bytes):
    """
    Convert uploaded image bytes into a PyTorch tensor.

    Output shape:
        [1, 3, 384, 384]
    """

    try:

        image = Image.open(
            io.BytesIO(image_bytes)
        ).convert("RGB")

    except Exception as e:

        raise ValueError(
            f"Unable to read uploaded image: {e}"
        )

    # Apply training-compatible preprocessing
    tensor = _transform(image)

    # Add batch dimension
    tensor = tensor.unsqueeze(0)

    # CPU
    tensor = tensor.to(DEVICE)

    return tensor


# ============================================================
# PREDICTION
# ============================================================

def predict_image(image_bytes: bytes):
    """
    Run prediction on an uploaded retinal fundus image.

    Returns:
        predicted_class_name : str
        confidence_percent   : float
        probabilities        : dict
    """

    # --------------------------------------------------------
    # Load model
    # --------------------------------------------------------

    model = _load_model()

    if model is None:

        raise RuntimeError(
            "RetinaScan AI model could not be loaded. "
            "Check the model file and backend configuration."
        )

    # --------------------------------------------------------
    # Preprocess
    # --------------------------------------------------------

    input_tensor = _preprocess(
        image_bytes
    )

    # --------------------------------------------------------
    # Inference
    # --------------------------------------------------------

    with torch.no_grad():

        logits = model(
            input_tensor
        )

        # Convert logits to probabilities
        probabilities_tensor = torch.softmax(
            logits,
            dim=1
        )

    # --------------------------------------------------------
    # Convert to NumPy
    # --------------------------------------------------------

    probabilities = (
        probabilities_tensor[0]
        .cpu()
        .numpy()
    )

    # --------------------------------------------------------
    # Predicted class
    # --------------------------------------------------------

    predicted_idx = int(
        probabilities.argmax()
    )

    predicted_class = CLASS_NAMES[
        predicted_idx
    ]

    # --------------------------------------------------------
    # Confidence
    # --------------------------------------------------------

    confidence = round(
        float(
            probabilities[predicted_idx]
        ) * 100,
        2
    )

    # --------------------------------------------------------
    # All class probabilities
    # --------------------------------------------------------

    probability_dict = {
        CLASS_NAMES[i]: round(
            float(probabilities[i]) * 100,
            2
        )
        for i in range(NUM_CLASSES)
    }

    return (
        predicted_class,
        confidence,
        probability_dict
    )


# ============================================================
# MODEL STATUS
# ============================================================

def is_model_loaded():
    """
    Returns True if the trained model was loaded successfully.
    """

    return MODEL_LOADED


# ============================================================
# LOAD MODEL AT STARTUP
# ============================================================

_load_model()