from datetime import datetime

from copier_templates_extensions import ContextHook


class ContextUpdater(ContextHook):
    def hook(self, context):
        use_src = context["use_src"]
        python_package = context["python_package"]
        return {
            "now": datetime.now(),
            "package_path": f"src/{python_package}" if use_src else python_package,
        }
