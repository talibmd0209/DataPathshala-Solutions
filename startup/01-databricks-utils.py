"""
Adds Databricks-style notebook conveniences on top of plain Jupyter:

  - display(df)          -> rich HTML table for Spark & pandas DataFrames
  - display(fig)          -> passthrough for matplotlib/plotly figures
  - dbutils.fs.*          -> local-filesystem-backed file utilities
  - dbutils.widgets.*     -> simple parameter widgets (ipywidgets-based)
  - dbutils.notebook.exit/run
  - %run ./other_notebook -> run another .ipynb's cells in this namespace
"""
import os
import shutil
import json
from IPython.display import display as _ipy_display, HTML
from IPython.core.magic import register_line_magic
from IPython import get_ipython

MAX_ROWS = 5 # same default cap Databricks' display() uses


# ---------------------------------------------------------------------------
# display()
# ---------------------------------------------------------------------------
def display(obj=None, *args, **kwargs):
    """Databricks-style display(). Renders Spark / pandas DataFrames as a
    scrollable HTML table; falls back to IPython's default display for
    anything else (plots, widgets, plain objects)."""
    try:
        from pyspark.sql import DataFrame as SparkDataFrame
    except ImportError:
        SparkDataFrame = ()

    try:
        import pandas as pd
    except ImportError:
        pd = None

    if SparkDataFrame and isinstance(obj, SparkDataFrame):
        total = obj.count()
        pdf = obj.limit(MAX_ROWS).toPandas()
        _render_table(pdf, total_rows=total, shown_rows=len(pdf))
        return

    if pd is not None and isinstance(obj, pd.DataFrame):
        truncated = obj.head(MAX_ROWS)
        _render_table(truncated, total_rows=len(obj), shown_rows=len(truncated))
        return

    # matplotlib figure, plotly figure, list, dict, etc. -> default behavior
    _ipy_display(obj, *args, **kwargs)


def _render_table(pdf, total_rows, shown_rows):
    note = ""
    if total_rows > shown_rows:
        note = (
            f"<div style='color:#888;font-size:12px;margin-top:4px;'>"
            f"Showing {shown_rows} of {total_rows} rows.</div>"
        )
    html = pdf.to_html(notebook=True, max_rows=MAX_ROWS)
    _ipy_display(HTML(f"<div style='overflow:auto'>{html}</div>{note}"))


# ---------------------------------------------------------------------------
# dbutils
# ---------------------------------------------------------------------------
class _FSUtils:
    """Local-filesystem stand-in for dbutils.fs. Paths behave like plain
    POSIX paths (no dbfs:/ prefix needed, but it's stripped if present)."""

    @staticmethod
    def _clean(path):
        return path.replace("dbfs:", "", 1) if path.startswith("dbfs:") else path

    def ls(self, path):
        path = self._clean(path)
        entries = []
        for name in sorted(os.listdir(path)):
            full = os.path.join(path, name)
            entries.append({
                "path": full,
                "name": name + ("/" if os.path.isdir(full) else ""),
                "size": os.path.getsize(full) if os.path.isfile(full) else 0,
                "isDir": os.path.isdir(full),
            })
        return entries

    def mkdirs(self, path):
        os.makedirs(self._clean(path), exist_ok=True)
        return True

    def rm(self, path, recurse=False):
        path = self._clean(path)
        if os.path.isdir(path):
            if recurse:
                shutil.rmtree(path)
            else:
                os.rmdir(path)
        elif os.path.exists(path):
            os.remove(path)
        return True

    def cp(self, src, dst, recurse=False):
        src, dst = self._clean(src), self._clean(dst)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=recurse)
        else:
            shutil.copy(src, dst)
        return True

    def mv(self, src, dst):
        shutil.move(self._clean(src), self._clean(dst))
        return True

    def put(self, path, contents, overwrite=False):
        path = self._clean(path)
        if os.path.exists(path) and not overwrite:
            raise FileExistsError(f"{path} already exists; pass overwrite=True")
        with open(path, "w") as f:
            f.write(contents)
        return True

    def head(self, path, maxBytes=65536):
        with open(self._clean(path), "r") as f:
            return f.read(maxBytes)


class _WidgetsUtils:
    """Minimal dbutils.widgets replacement backed by a plain dict + ipywidgets."""

    def __init__(self):
        self._values = {}

    def text(self, name, defaultValue="", label=None):
        self._values.setdefault(name, defaultValue)
        self._render(name)

    def dropdown(self, name, defaultValue, choices, label=None):
        self._values.setdefault(name, defaultValue)
        self._render(name, choices=choices)

    def get(self, name):
        if name not in self._values:
            raise KeyError(f"No widget named '{name}'")
        return self._values[name]

    def remove(self, name):
        self._values.pop(name, None)

    def removeAll(self):
        self._values.clear()

    def _render(self, name, choices=None):
        try:
            import ipywidgets as w
        except ImportError:
            return
        if choices:
            widget = w.Dropdown(options=choices, value=self._values[name], description=name)
        else:
            widget = w.Text(value=self._values[name], description=name)

        def _on_change(change):
            if change["name"] == "value":
                self._values[name] = change["new"]

        widget.observe(_on_change, names="value")
        _ipy_display(widget)


class _NotebookExit(Exception):
    def __init__(self, value):
        self.value = value
        super().__init__(f"Notebook exited with: {value}")


class _NotebookUtils:
    def exit(self, value=""):
        raise _NotebookExit(value)

    def run(self, path, timeout_seconds=0, arguments=None):
        """Runs another .ipynb notebook's cells in a fresh namespace and
        returns whatever the sub-notebook passed to dbutils.notebook.exit()."""
        ip = get_ipython()
        ns = {"dbutils": dbutils, "display": display}
        ns.update(arguments or {})
        nb_path = path if path.endswith(".ipynb") else path + ".ipynb"
        with open(nb_path) as f:
            nb = json.load(f)
        result = None
        try:
            for cell in nb.get("cells", []):
                if cell.get("cell_type") == "code":
                    src = "".join(cell.get("source", []))
                    exec(compile(src, nb_path, "exec"), ns)
        except _NotebookExit as e:
            result = e.value
        return result


class _DBUtils:
    def __init__(self):
        self.fs = _FSUtils()
        self.widgets = _WidgetsUtils()
        self.notebook = _NotebookUtils()

    def help(self, module=None):
        print("Available: dbutils.fs, dbutils.widgets, dbutils.notebook")


dbutils = _DBUtils()


# ---------------------------------------------------------------------------
# %run magic -> run another notebook inline, Databricks-style
# ---------------------------------------------------------------------------
@register_line_magic
def run_notebook(line):
    """Usage: %run_notebook ./helpers.ipynb"""
    path = line.strip()
    if not path.endswith(".ipynb"):
        path += ".ipynb"
    ip = get_ipython()
    with open(path) as f:
        nb = json.load(f)
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            src = "".join(cell.get("source", []))
            ip.run_cell(src)


# Push everything into the user's global namespace explicitly, in case this
# file is executed in a scope that isn't automatically merged.
get_ipython().user_ns.update({
    "display": display,
    "dbutils": dbutils,
})

print("Databricks-style helpers ready: display(), dbutils.fs/widgets/notebook, %run_notebook")
