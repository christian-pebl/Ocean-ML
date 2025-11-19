"""
Protocol Handler Registration

Registers oceanml:// protocol handler on Windows or macOS
so the browser can launch the desktop app.
"""

import sys
import os
import platform

def register_protocol_windows():
    """Register oceanml:// protocol on Windows"""
    try:
        import winreg
    except ImportError:
        print("❌ winreg module not available. Are you on Windows?")
        return False

    protocol = "oceanml"
    app_name = "Ocean-ML"

    # Get path to current Python executable and this script's directory
    python_exe = sys.executable
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(script_dir, "main.py")

    if not os.path.exists(main_script):
        print(f"❌ Main script not found at: {main_script}")
        return False

    try:
        # Create protocol key
        key_path = f"Software\\Classes\\{protocol}"
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        winreg.SetValue(key, "", winreg.REG_SZ, f"URL:{app_name} Protocol")
        winreg.SetValueEx(key, "URL Protocol", 0, winreg.REG_SZ, "")
        winreg.CloseKey(key)

        # Create command key
        command_path = f"{key_path}\\shell\\open\\command"
        command_key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, command_path)

        # Command to launch the app
        command = f'"{python_exe}" "{main_script}" "%1"'
        winreg.SetValue(command_key, "", winreg.REG_SZ, command)
        winreg.CloseKey(command_key)

        print(f"✅ Protocol handler registered successfully!")
        print(f"   Protocol: {protocol}://")
        print(f"   Command: {command}")
        print(f"\n   Test with: {protocol}://test?video=123&token=abc")

        return True

    except Exception as e:
        print(f"❌ Error registering protocol: {e}")
        return False


def unregister_protocol_windows():
    """Unregister oceanml:// protocol on Windows"""
    try:
        import winreg
    except ImportError:
        print("❌ winreg module not available")
        return False

    protocol = "oceanml"

    try:
        key_path = f"Software\\Classes\\{protocol}"
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, f"{key_path}\\shell\\open\\command")
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, f"{key_path}\\shell\\open")
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, f"{key_path}\\shell")
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)

        print(f"✅ Protocol handler unregistered successfully!")
        return True

    except FileNotFoundError:
        print("⚠️  Protocol handler was not registered")
        return True
    except Exception as e:
        print(f"❌ Error unregistering protocol: {e}")
        return False


def register_protocol_mac():
    """Register oceanml:// protocol on macOS"""
    print("⚠️  macOS protocol registration not yet implemented")
    print("   Please manually register the protocol in Info.plist")
    return False


def main():
    print("=" * 60)
    print("Ocean-ML Protocol Handler Registration")
    print("=" * 60)
    print()

    system = platform.system()

    if len(sys.argv) > 1 and sys.argv[1] == "unregister":
        print("Unregistering protocol handler...")
        if system == "Windows":
            success = unregister_protocol_windows()
        else:
            print(f"❌ Unregister not implemented for {system}")
            success = False
    else:
        print(f"Detected OS: {system}")
        print()

        if system == "Windows":
            print("Registering oceanml:// protocol for Windows...")
            success = register_protocol_windows()
        elif system == "Darwin":
            print("Registering oceanml:// protocol for macOS...")
            success = register_protocol_mac()
        else:
            print(f"❌ Unsupported operating system: {system}")
            success = False

    print()
    print("=" * 60)

    if success:
        print("✅ Registration complete!")
        print()
        print("Next steps:")
        print("1. Test the protocol handler:")
        print("   - Open your browser")
        print("   - Navigate to: oceanml://test?video=123&token=abc")
        print("   - The desktop app should launch")
        print()
        print("2. If it doesn't work:")
        print("   - Try restarting your browser")
        print("   - Check the command is correct")
        print("   - Run this script as administrator")
    else:
        print("❌ Registration failed")
        print()
        print("Troubleshooting:")
        print("- Make sure you're running on Windows or macOS")
        print("- Try running as administrator")
        print("- Check main.py exists in the same directory")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
