from pathlib import Path
from subprocess import run

from jinja2 import Template, StrictUndefined

from api import get_all_plugins

template_file = Path("template.html")
output_html_file = Path("public/index.html")

sp = run(["git", "rev-parse", "--verify", "HEAD"], capture_output=True)
commit = sp.stdout.decode().strip()

template = Template(template_file.read_text(), autoescape=True,undefined=StrictUndefined)
output_html_file.write_text(template.render({
    "plugins": get_all_plugins(),
    "commit":commit
}))
