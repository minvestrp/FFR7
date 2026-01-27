import os
import tempfile
import warnings

# Force matplotlib to use non-GUI backend before any test imports plotting code
try:
    import matplotlib
    matplotlib.use("Agg")
except Exception:
    # matplotlib may not be installed in some environments; ignore
    pass

# Ensure matplotlib writes config into a temp dir (avoid HOME/.config usage / shared locks on CI)
os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp())

# Suppress ResourceWarning related to GUI finalizers (Tkinter/PIL) to avoid noisy unraisableexception warnings
warnings.filterwarnings("ignore", category=ResourceWarning)
