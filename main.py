import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

try:
    from gui.app_window import AppWindow
    # We also need to ensure the database module is loaded so initialization runs
    import data.database
except ImportError as e:
    print(f"Error during initial imports: {e}")
    print("Ensure file structure is correct and all __init__.py files exist.")
    sys.exit(1)

def main():
    try:
        # The database initialization now happens automatically when data.database is imported.
        print("Starting NexusTask AI...")
        app = AppWindow()
        app.mainloop()
        print("NexusTask AI closed.")
    except Exception as e:
        print(f"Unexpected error running the application: {e}")
        # Consider adding more robust error logging for production
        sys.exit(1)

if __name__ == "__main__":
    main()