import shutil
from pathlib import Path


# Clean up after installing for local development
def clean():
    # Get the current directory
    base_dir = Path.cwd()

    # Directories and patterns to clean
    cleanup_patterns = [
        'build',
        'dist',
        '*.egg-info',
        '__pycache__',
        '.eggs',
        '.pytest_cache'
    ]

    # Clean directories
    for pattern in cleanup_patterns:
        for path in base_dir.glob(pattern):
            try:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                print(f"Removed: {path}")
            except Exception as e:
                print(f"Could not remove {path}: {e}")

    # Remove compiled Python files
    for path in base_dir.rglob('*.py[co]'):
        try:
            path.unlink()
            print(f"Removed compiled file: {path}")
        except Exception as e:
            print(f"Could not remove {path}: {e}")


if __name__ == '__main__':
    clean()
