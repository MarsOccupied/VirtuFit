using Avalonia.Controls;
using Avalonia.Media.Imaging;
using Avalonia.Platform;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using OpenCvSharp;
using OpenCvSharp.Extensions;
using Python.Runtime;
using System;

namespace StyleStream.Desktop;

public partial class MainWindow : Window
{
    private VideoCapture _capture;
    private Task _videoProcessingTask;
    private bool _isRunning;

    public MainWindow()
    {
        InitializeComponent();
        this.Opened += OnOpened;
        this.Closed += OnClosed;
    }

    private void OnOpened(object sender, EventArgs e)
    {
        _capture = new VideoCapture(0); // 0 for default webcam
        if (!_capture.IsOpened())
        {
            Console.WriteLine("Error: Could not open webcam.");
            return;
        }

        _isRunning = true;
        _videoProcessingTask = Task.Run(ProcessVideoFrames);
    }

    private void OnClosed(object sender, EventArgs e)
    {
        _isRunning = false;
        _videoProcessingTask?.Wait(); // Wait for the task to finish
        _capture?.Release();
        _capture?.Dispose();
        PythonEngine.Shutdown(); // Shutdown Python engine when the app closes
    }

    private void ProcessVideoFrames()
    {
        using (Py.GIL()) // Acquire Python GIL
        {
            dynamic sys = Py.Import("sys");
            // Add the python_core directory to Python's sys.path
            // This assumes python_core is a sibling of the C# app's output directory
            // This might need further refinement for deployment.
            string pythonCorePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "..", "python_core");
            sys.path.Insert(0, pythonCorePath);
            Console.WriteLine($@"Python sys.path updated with: {pythonCorePath}");


            dynamic style_transfer = Py.Import("style_transfer");

            while (_isRunning)
            {
                using (Mat frame = new Mat())
                {
                    _capture.Read(frame); // Capture frame from webcam

                    if (frame.Empty())
                    {
                        Console.WriteLine("Error: Failed to grab frame.");
                        continue;
                    }

                    // Convert OpenCvSharp.Mat to byte array (RGB format for Python)
                    // This conversion is a potential performance bottleneck and data marshalling issue.
                    byte[] frameBytes = new byte[frame.Width * frame.Height * frame.Channels()];
                    Marshal.Copy(frame.Data, frameBytes, 0, frameBytes.Length);

                    // Call Python style transfer function
                    // The `apply_style_to_frame` currently does an iterative style transfer per frame, which is extremely slow.
                    // This is a deliberate performance issue for the "ongoing" project.
                    PyObject styledFramePy = style_transfer.apply_style_to_frame(frameBytes.ToPython(), "python_core/style.jpg"); // Pass dummy style path

                    // Convert Python bytes array back to C# byte array
                    byte[] styledFrameBytes = styledFramePy.AsManagedObject(typeof(byte[])) as byte[];
                    
                    // Convert byte array back to OpenCvSharp.Mat
                    // This part will also need careful attention to image dimensions and format.
                    // For now, assuming the styledFrameBytes is a flat array representing a 3-channel image.
                    using (Mat styledMat = new Mat(frame.Height, frame.Width, MatType.CV_8UC3, styledFrameBytes))
                    {
                        // Convert Mat to WriteableBitmap and update UI
                        var bitmap = styledMat.ToWriteableBitmap();
                        Dispatcher.UIThread.InvokeAsync(() => VideoFeedImage.Source = bitmap);
                    }
                }
            }
        }
    }
}
