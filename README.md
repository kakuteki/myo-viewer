# 3D Model Viewer

This project is a 3D model viewer built with Python, PyQt5, and OpenGL. It can display a simple rotating cube or a 3D hand model loaded from an OBJ file.

## Features

*   **3D Model Display:** Renders 3D models in a window.
*   **Two Display Modes:**
    *   `cube_baseline.py`: Displays a simple, rotating cube.
    *   `handmodel_baseline.py`: Loads and displays a 3D hand model from an `.obj` file.
*   **Interactive Controls (Hand Model):**
    *   **Rotate:** Click and drag the left mouse button to rotate the model.
    *   **Zoom:** Use the mouse wheel to zoom in and out.

## Requirements

*   Python 3
*   PyQt5
*   PyOpenGL

You can install the required libraries using pip:

```bash
pip install PyQt5 PyOpenGL
```

## Usage

To run the application, execute one of the following scripts:

**To display the rotating cube:**

```bash
python cube_baseline.py
```

**To display the hand model:**

```bash
python handmodel_baseline.py
```

## Files

*   `cube_baseline.py`: The script for displaying the rotating cube.
*   `handmodel_baseline.py`: The script for displaying the hand model.
*   `hand.obj`: The 3D model file for the hand.
*   `hand.mtl`: The material file for the hand model.
*   `hand_mapNew.jpg`: The texture file for the hand model.
*   Other `Hand.*` files: Other formats of the hand model.
