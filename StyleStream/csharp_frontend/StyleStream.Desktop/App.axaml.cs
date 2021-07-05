using Avalonia;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;
using Python.Runtime;
using System;
using System.IO;

namespace StyleStream.Desktop;

public partial class App : Application
{
    public override void Initialize()
    {
        AvaloniaXamlLoader.Load(this);
    }

    public override void OnFrameworkInitializationCompleted()
    {
        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            // Set Python DLL path. This path might need to be adjusted based on your Python installation.
            // Example for macOS with Homebrew Python:
            // Runtime.PythonDLL = "/usr/local/opt/python@3.9/Frameworks/Python.framework/Versions/3.9/lib/libpython3.9.dylib";
            // Example for Windows:
            // Runtime.PythonDLL = "C:\\Users\\YourUser\\AppData\\Local\\Programs\\Python\\Python39\\python39.dll";
            // For this project, we'll assume Python 3.9 as per the requirements.txt implied version.
            // THIS IS A CRITICAL CONFIGURATION STEP FOR THE USER. If this is incorrect, Python.NET will fail.
            
            // Attempt to find Python 3.9, which is the assumed version for Python.NET 2.7.9.
            // This is a common point of failure and a deliberate "issue" for the user to resolve.
            var pythonPath = Environment.GetEnvironmentVariable("PATH");
            string pythonDll = null;

            // Basic attempt to find a common Python 3.9 DLL on macOS/Linux and Windows
            if (RuntimeInformation.IsOSPlatform(OSPlatform.OSX) || RuntimeInformation.IsOSPlatform(OSPlatform.Linux))
            {
                string[] commonMacPythonPaths = new[]
                {
                    "/usr/local/opt/python@3.9/Frameworks/Python.framework/Versions/3.9/lib/libpython3.9.dylib",
                    "/opt/homebrew/opt/python@3.9/Frameworks/Python.framework/Versions/3.9/lib/libpython3.9.dylib",
                    "/usr/lib/libpython3.9.dylib"
                };
                foreach (var path in commonMacPythonPaths)
                {
                    if (File.Exists(path))
                    {
                        pythonDll = path;
                        break;
                    }
                }
            }
            else if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
            {
                // Simplified for brevity, a real app would search more thoroughly or prompt user
                // Assumes Python 3.9 is in a common location
                string[] commonWinPythonPaths = new[]
                {
                    "C:\\Python39\\python39.dll",
                    Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Programs", "Python", "Python39", "python39.dll")
                };
                foreach (var path in commonWinPythonPaths)
                {
                    if (File.Exists(path))
                    {
                        pythonDll = path;
                        break;
                    }
                }
            }

            if (string.IsNullOrEmpty(pythonDll))
            {
                // This is a deliberate failure point if Python.NET cannot find the DLL automatically.
                // The user will need to manually set `Runtime.PythonDLL`.
                Console.WriteLine("WARNING: Could not automatically find Python 3.9 DLL. Python.NET may fail to initialize. Please set Runtime.PythonDLL manually.");
                // Fallback, often incorrect but might work in some setups
                Runtime.PythonDLL = "python3.9"; // Try relying on PATH if direct path fails
            } else {
                Runtime.PythonDLL = pythonDll;
                Console.WriteLine($"INFO: Using Python DLL: {pythonDll}");
            }
            
            // Add the directory containing your Python scripts to the Python path
            // This path is relative to the C# executable, so it assumes `python_core` is a sibling of the C# app's output directory
            // This might also need adjustment depending on deployment structure.
            var pythonCorePath = Path.GetFullPath(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "..", "python_core"));
            Environment.SetEnvironmentVariable("PYTHONPATH", pythonCorePath, EnvironmentVariableTarget.Process);
            Console.WriteLine($"INFO: PYTHON_PATH set to: {pythonCorePath}");

            PythonEngine.Initialize();
            Console.WriteLine("INFO: Python Engine Initialized.");

            desktop.MainWindow = new MainWindow();
        }

        base.OnFrameworkInitializationCompleted();
    }
}