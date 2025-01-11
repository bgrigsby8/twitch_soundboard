import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:logger/web.dart';
import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:file_picker/file_picker.dart';
import 'package:path/path.dart' as path;

var logger = Logger();

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        colorScheme:
            ColorScheme.fromSeed(seedColor: Colors.lightGreen.shade900),
        useMaterial3: true,
      ),
      home: const MyHomePage(title: 'Twitch Soundboard Setting'),
    );
  }
}

class PythonProcessManager {
  Process? _pythonProcess;

  /// Start the Python process
  Future<void> start(String executablePath) async {
    try {
      _pythonProcess =
          await Process.start(executablePath, [], runInShell: false);
      final pid = _pythonProcess?.pid;
      if (pid != null) {
        const platformChannel = MethodChannel('com.example.twitchSoundboard');
        await platformChannel.invokeMethod('setPythonPid', pid);
        logger.i('Python process started with PID: $pid');
      }

      _pythonProcess?.stdout.transform(SystemEncoding().decoder).listen((data) {
        logger.i('Python stdout: $data');
      });
      _pythonProcess?.stderr.transform(SystemEncoding().decoder).listen((data) {
        if (data == "No MIDI input ports found.") {
          logger.w('No MIDI input ports found.');
        } else {
          logger.w('Python stderr: $data');
        }
      });
      logger.i('Python process started successfully.');
    } catch (e) {
      logger.w('Failed to start Python process: $e');
    }
  }

  /// Stop the Python process
  void stop() {
    if (_pythonProcess != null) {
      _pythonProcess?.kill();
      logger.i('Python process stopped.');
      _pythonProcess = null;
    }
  }

  /// Restart the Python process
  Future<void> restart(String executablePath) async {
    logger.i('Restarting Python process...');
    stop(); // Stop the existing process
    await start(executablePath); // Start a new process
  }

  /// Check if the Python process is running
  bool isRunning() {
    return _pythonProcess != null && _pythonProcess!.pid > 0;
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> with WidgetsBindingObserver {
  Map<String, dynamic> configurations = {};
  bool _isModified = false; // Track whether changes are made
  final PythonProcessManager _pythonManager =
      PythonProcessManager(); // PythonProcessManager instance

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this); // Add lifecycle observer
    _loadConfigurations();
    _setupAndRunPythonExecutable(); // Start the Python process when the app starts
  }

  @override
  void dispose() {
    logger.i("App is closing...");
    WidgetsBinding.instance.removeObserver(this); // Remove lifecycle observer
    _pythonManager.stop(); // Stop Python process when the app is closed
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    logger.i("App lifecycle state changed: $state");
    if (state == AppLifecycleState.paused ||
        state == AppLifecycleState.detached) {
      _pythonManager
          .stop(); // Stop Python process when app is paused or detached
    }
  }

  Future<void> _setupAndRunPythonExecutable() async {
    try {
      // Get the path to the Python executable
      final executablePath = await _setupPythonExecutable();
      // Start the Python process
      await _pythonManager.start(executablePath);
    } catch (e) {
      logger.w('Error setting up Python executable: $e');
    }
  }

  Future<String> _setupPythonExecutable() async {
    final appDir = await getApplicationDocumentsDirectory();
    final executablePath = '${appDir.path}/twitch-soundboard/pyo_controller';

    // Skip copying if the file already exists
    final pythonExecutable = File(executablePath);
    if (pythonExecutable.existsSync()) {
      logger.i("Python executable already exists at $executablePath");
      return executablePath;
    }

    // Optionally copy the file from assets if needed (this won't run if manually placed)
    final byteData = await rootBundle.load('assets/python/pyo_controller');
    await pythonExecutable.writeAsBytes(byteData.buffer.asUint8List());
    logger.i("Python executable copied to $executablePath");
    return executablePath;
  }

  @override
  Widget build(BuildContext context) {
    final List<String> keys = configurations.keys.toList();

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: configurations.isEmpty
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(10.0),
                  child: Image.asset(
                    'assets/images/soundboard_map.jpg',
                    fit: BoxFit.cover,
                    width: double.infinity,
                    height: 200,
                  ),
                ),
                Expanded(
                  child: ListView.builder(
                    itemCount: keys.length,
                    itemBuilder: (context, index) {
                      final key = keys[index];
                      final value = configurations[key];

                      // Determine if the key represents a sound or an effect
                      final isSound = value is Map<String, dynamic> &&
                          value.containsKey("sound");
                      final isEffect = value is Map<String, dynamic> &&
                          value.containsKey("effect");

                      return Card(
                        margin: const EdgeInsets.symmetric(
                            horizontal: 10, vertical: 5),
                        child: Padding(
                          padding: const EdgeInsets.all(10.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                "Key: $key",
                                style: Theme.of(context).textTheme.bodySmall,
                              ),
                              const SizedBox(height: 10),
                              if (isSound) ...[
                                ElevatedButton(
                                  onPressed: () async {
                                    final result =
                                        await FilePicker.platform.pickFiles(
                                      type: FileType.custom,
                                      allowedExtensions: ['mp3', 'wav', 'ogg'],
                                    );
                                    logger.i("Selected file: ${result?.files}");
                                    if (result != null &&
                                        result.files.single.path != null) {
                                      logger.i(
                                          "Selected file path: ${result.files.single.path}");
                                      final selectedFile =
                                          File(result.files.single.path!);
                                      logger.i("Selected file: $selectedFile");
                                      final appDir =
                                          await getApplicationDocumentsDirectory();
                                      final soundDir = Directory(path.join(
                                          appDir.path,
                                          "twitch-soundboard/sounds"));

                                      // Ensure the sounds directory exists
                                      if (!soundDir.existsSync()) {
                                        soundDir.createSync(recursive: true);
                                      }

                                      // Copy file to sounds directory
                                      final newPath = path.join(soundDir.path,
                                          path.basename(selectedFile.path));
                                      logger.i(
                                          "Copying file $selectedFile to: $newPath");
                                      await selectedFile.copy(newPath);

                                      // Update configuration
                                      setState(() {
                                        configurations[key]["sound"] =
                                            "sounds/${path.basename(newPath)}";
                                        _isModified = true;
                                      });

                                      ScaffoldMessenger.of(context)
                                          .showSnackBar(
                                        const SnackBar(
                                            content: Text(
                                                "Sound file selected and copied!")),
                                      );
                                    }
                                  },
                                  child: const Text("Select Sound File"),
                                ),
                                if (value["sound"] != null)
                                  Text(
                                    "Current File: ${value["sound"]}",
                                    style:
                                        Theme.of(context).textTheme.bodySmall,
                                  ),
                              ],
                              if (isEffect) ...[
                                DropdownButtonFormField<String>(
                                  value: value["effect"],
                                  decoration: const InputDecoration(
                                    labelText: "Select Effect",
                                    border: OutlineInputBorder(),
                                  ),
                                  items: const [
                                    DropdownMenuItem(
                                        value: "reverb", child: Text("Reverb")),
                                    DropdownMenuItem(
                                        value: "harmonizer",
                                        child: Text("Harmonizer")),
                                    DropdownMenuItem(
                                        value: "freq_shift",
                                        child: Text("Freq Shift")),
                                    DropdownMenuItem(
                                        value: "chorus", child: Text("Chorus")),
                                    DropdownMenuItem(
                                        value: "distortion",
                                        child: Text("Distortion")),
                                    DropdownMenuItem(
                                        value: "delay", child: Text("Delay"))
                                  ],
                                  onChanged: (newValue) {
                                    setState(() {
                                      configurations[key]["effect"] = newValue!;
                                      _isModified = true; // Mark as modified
                                    });
                                  },
                                ),
                              ],
                              if (!isSound && !isEffect)
                                TextFormField(
                                  initialValue: value.toString(),
                                  decoration: const InputDecoration(
                                    labelText: "Device Name",
                                    border: OutlineInputBorder(),
                                  ),
                                  onChanged: (newValue) {
                                    setState(() {
                                      configurations[key] = newValue;
                                      _isModified = true; // Mark as modified
                                    });
                                  },
                                ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.all(10.0),
                  child: ElevatedButton(
                    onPressed: _isModified
                        ? () async {
                            await _saveConfigurations();
                            setState(() {
                              _isModified = false; // Reset modification flag
                            });
                            final executablePath =
                                await _setupPythonExecutable();
                            await _pythonManager.restart(executablePath);
                          }
                        : null, // Disable the button if no changes
                    child: const Text("Save Changes"),
                  ),
                ),
              ],
            ),
    );
  }

  Future<void> _loadConfigurations() async {
    final directory = await getApplicationDocumentsDirectory();
    logger.i("Directory path: ${directory.path}");
    final file =
        File('${directory.path}/twitch-soundboard/configurations.json');

    // Load the configurations
    final content = await file.readAsString();
    logger.i("Loaded configurations: $content");
    setState(() {
      configurations = jsonDecode(content) as Map<String, dynamic>;
    });
  }

  Future<void> _saveConfigurations() async {
    final directory = await getApplicationDocumentsDirectory();
    final file =
        File('${directory.path}/twitch-soundboard/configurations.json');
    logger.i(file.openRead().toString());
    logger.i(file.path);
    logger.i("Saving configurations: $configurations");
    await file.writeAsString(jsonEncode(configurations));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text("Configurations saved!")),
    );
  }
}
