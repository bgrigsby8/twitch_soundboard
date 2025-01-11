import Cocoa
import FlutterMacOS

@main
class AppDelegate: FlutterAppDelegate {
  var pythonPid: Int32?

  override func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
    return true
  }

  override func applicationSupportsSecureRestorableState(_ app: NSApplication) -> Bool {
    return true
  }

  override func applicationWillTerminate(_ notification: Notification) {
    // Perform cleanup before the app quits
    print("App is terminating...")
    if let pid = pythonPid {
      kill(pid, SIGTERM) // Send SIGTERM to the Python process
      print("Python process with PID \(pid) terminated.")
    }
  }

  override func applicationDidFinishLaunching(_ notification: Notification) {
    let controller: FlutterViewController = mainFlutterWindow?.contentViewController as! FlutterViewController
    let channel = FlutterMethodChannel(name: "com.example.twitchSoundboard",
                                      binaryMessenger: controller.engine.binaryMessenger)
    
    channel.setMethodCallHandler { [weak self] (call: FlutterMethodCall, result: @escaping FlutterResult) in
      if call.method == "setPythonPid" {
        if let args = call.arguments as? Int32 {
          self?.pythonPid = args
          result("PID set to \(args)")
        } else {
          result(FlutterError(code: "INVALID_ARGUMENT", message: "Expected Int32 for PID", details: nil))
        }
      } else {
        result(FlutterMethodNotImplemented)
      }
    }
  }
}
