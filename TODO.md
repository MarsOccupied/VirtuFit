# StyleStream - Project TODO and Known Issues

This document outlines the remaining tasks and identified issues for the "StyleStream" project, which is currently approximately 70% complete. The goal is to provide a clear roadmap for further development and highlight areas that require attention for a production-ready application.

## I. Remaining Features (To Be Implemented)

1.  **Fast Feed-Forward Network for Style Transfer:**
    *   Replace the slow, iterative style transfer in `python_core/style_transfer.py` with a pre-trained, fast feed-forward neural network for real-time performance (e.g., Johnson et al. or AdaIN models).
    *   This will involve loading a pre-trained `.pth` or `.pt` model and implementing its inference pass.

2.  **Style Arsenal and Selection UI:**
    *   Bundle 10-15 pre-trained fast styles within the application.
    *   Implement a UI in the C# frontend (`MainWindow.axaml`, `MainWindow.axaml.cs`) for users to browse and select different styles.

3.  **Style Intensity Slider and Blend Modes:**
    *   Add a slider control to adjust the intensity or strength of the applied style.
    *   Implement different blend modes for mixing styles.

4.  **Custom Style Training Mode:**
    *   Develop a feature where users can upload their own style images to fine-tune a quick model.
    *   This will require a simplified training loop in Python and a corresponding UI in C# for image input and progress display.

5.  **Temporal Consistency:**
    *   Implement algorithms (e.g., optical flow-based smoothing) to reduce flickering and improve temporal consistency in styled video.

6.  **Resolution Upscaling Options:**
    *   Provide options to upscale the resolution of the styled output.

7.  **Dark Mode UI:**
    *   Implement a dark mode theme for the Avalonia UI.

8.  **Gallery of User-Created Styles:**
    *   Create a mechanism to save and load user-trained custom styles.

9.  **Batch Processing:**
    *   Add functionality to batch process folders of images or videos.

10. **Slow-Motion Replay with Style Transitions:**
    *   Implement features for slow-motion playback and smooth transitions between styles.

11. **Export Styled Videos:**
    *   Enable users to export their styled video streams to common video formats.

12. **FPS Counter:**
    *   Integrate an FPS counter in the UI to monitor real-time performance.

## II. Known Issues and Areas for Debugging/Optimization

1.  **Critical: OpenCvSharp Runtime for macOS (or other non-Windows OS):**
    *   **Issue:** The current C# project includes `OpenCvSharp4.runtime.win` in `StyleStream.Desktop.csproj`. This is incorrect for macOS (and other non-Windows operating systems) and will lead to runtime errors.
    *   **Resolution:** The user needs to remove `OpenCvSharp4.runtime.win` and add the appropriate runtime package for their OS (e.g., `OpenCvSharp4.runtime.osx` for macOS, `OpenCvSharp4.runtime.linux` for Linux).

2.  **Critical: Python.NET DLL Path Configuration:**
    *   **Issue:** The `Runtime.PythonDLL` path in `App.axaml.cs` is a heuristic and might not correctly locate the Python 3.9 DLL on the user's system, leading to Python.NET initialization failures.
    *   **Resolution:** The user will likely need to manually adjust the `Runtime.PythonDLL` string in `App.axaml.cs` to the absolute path of their specific Python 3.9 DLL (e.g., `/usr/local/opt/python@3.9/Frameworks/Python.framework/Versions/3.9/lib/libpython3.9.dylib` on Homebrew macOS, or `C:\Users\YourUser\AppData\Local\Programs\Python\Python39\python39.dll` on Windows).

3.  **Major Performance Bottleneck: Iterative Style Transfer Per Frame:**
    *   **Issue:** The `apply_style_to_frame` function in `python_core/style_transfer.py` currently performs a full, albeit short (e.g., 2 steps), iterative style transfer for *every single video frame*. This is computationally very expensive and will result in extremely low FPS (likely <1 FPS) and is not suitable for real-time applications.
    *   **Resolution:** This needs to be replaced with an inference pass of a fast, pre-trained feed-forward style transfer network. The `trained_model` parameter in `apply_style_to_frame` is currently unused and should eventually hold this pre-trained model.

4.  **Image Data Marshalling and Conversion:**
    *   **Issue:** The conversion of image data between `OpenCvSharp.Mat` (C#), `byte[]` (C#), and NumPy arrays/Python objects, and back, can be error-prone regarding data formats (e.g., BGR vs. RGB), dimensions, and memory alignment. There's a risk of incorrect image display (e.g., color shifts, distorted images) or crashes due to improper buffer handling.
    *   **Resolution:** Thorough testing of the image conversion pipeline and careful attention to `MatType`, array sizes, and pixel formats are required. Potentially use `NumPy.NET` or a similar library for more direct NumPy array handling between C# and Python.

5.  **Hardcoded Style Image Path:**
    *   **Issue:** The `style.jpg` path is currently hardcoded within the C# `MainWindow.axaml.cs` and Python `style_transfer.py` for `apply_style_to_frame`.
    *   **Resolution:** This should be made dynamic, allowing users to select their desired style image through the UI.

6.  **Python Environment Management:**
    *   **Issue:** The Python environment (dependencies from `requirements.txt`) needs to be set up correctly by the user. If PyTorch, OpenCV, etc., are not installed or are not accessible to Python.NET, the application will fail.
    *   **Resolution:** The user needs to ensure they have an activated Python 3.9 environment with all dependencies installed (`pip install -r requirements.txt`).

7.  **Resource Management (C#):**
    *   **Issue:** While `_capture.Release()` and `_capture.Dispose()` are called, careful consideration of memory management, especially with the frequent creation and disposal of `Mat` objects and `WriteableBitmap` instances, is needed to prevent memory leaks in a long-running application.
    *   **Resolution:** Profile memory usage and ensure all `IDisposable` resources are correctly disposed of.

8.  **UI Thread Responsiveness:**
    *   **Issue:** Although image updates are marshaled to the UI thread, the overall responsiveness of the UI might be affected by the heavy background video processing. If the `ProcessVideoFrames` loop takes too long, the UI could become sluggish.
    *   **Resolution:** Optimize the `ProcessVideoFrames` loop (especially the style transfer part), consider using a dedicated rendering thread, and ensure UI updates are batched or throttled if necessary.

