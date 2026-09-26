"""Windows frozen entry for offline collection; never repair or deploy blindly."""
import sys
from offline_update import main

if __name__ == '__main__':
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='replace')
    try:
        raise SystemExit(main())
    except (OSError, ValueError, IndexError) as exc:
        print(f'Operation failed: {exc}', file=sys.stderr)
        raise SystemExit(2)
