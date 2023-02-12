from datetime import datetime
from pathlib import Path
from subprocess import run

from jinja2 import Template, StrictUndefined

from api import get_all_plugins

template_file = Path("template.html")

sp = run(["git", "rev-parse", "--verify", "HEAD"], capture_output=True)
commit = sp.stdout.decode().strip()

for majorversion in [4, 5]:
    output_html_file = Path(f"public/{majorversion}/index.html")

    plugins, supported, unsupported = get_all_plugins(majorversion)
    template = Template(template_file.read_text(), autoescape=True, undefined=StrictUndefined)
    output_html_file.write_text(template.render({
        "plugins": plugins,
        "commit": commit,
        "now": datetime.now(),
        "supported": supported,
        "unsupported": unsupported,
        "majorversion": majorversion,
        "fraction": supported / (supported + unsupported) * 100
    }))
