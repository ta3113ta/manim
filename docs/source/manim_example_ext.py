from docutils import nodes
from docutils.parsers.rst import directives, Directive

import jinja2
import os


class skip_manim_node(nodes.Admonition, nodes.Element):
    pass


def visit(self, node, name=""):
    self.visit_admonition(node, name)


def depart(self, node):
    self.depart_admonition(node)


class ManimExampleDirective(Directive):
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    option_spec = {
        "hide_code": bool,
        "media": str,
    }
    final_argument_whitespace = True

    def run(self):
        hide_code = "hide_code" in self.options
        scene_name = self.arguments[0]
        media_file_name = self.options["media"]

        source_block = [
            ".. code-block:: python",
            "",
            *[f"    {line}" for line in self.content],
        ]
        source_block = "\n".join(source_block)

        state_machine = self.state_machine
        document = state_machine.document

        is_video = not any(
            media_file_name.endswith(ext) for ext in [".png", ".jpg", ".gif"]
        )
        rendered_template = jinja2.Template(TEMPLATE).render(
            scene_name=scene_name,
            scene_name_lowercase=scene_name.lower(),
            hide_code=hide_code,
            is_video=is_video,
            media_file_name=media_file_name,
            source_block=source_block,
        )
        state_machine.insert_input(
            rendered_template.split("\n"), source=document.attributes["source"]
        )

        return []


def setup(app):
    app.add_node(skip_manim_node, html=(visit, depart))

    setup.app = app
    setup.config = app.config
    setup.confdir = app.confdir

    app.add_directive("manim-example", ManimExampleDirective)

    return {"parallel_read_safe": False, "parallel_write_safe": True}


TEMPLATE = r"""
{% if not hide_code %}

.. raw:: html

    <div class="manim-example">

{% endif %}

{% if is_video %}
.. raw:: html

    <video id="{{ scene_name_lowercase }}" class="manim-video" controls loop autoplay src="{{ media_file_name }}"></video>
{% else %}
.. image:: {{ media_file_name }}
    :align: center
    :name: {{ scene_name_lowercase }}
{% endif %}

{% if not hide_code %}
.. raw:: html

    <h5 class="example-header">{{ scene_name }}<a class="headerlink" href="#{{ scene_name_lowercase }}">¶</a></h5>

{{ source_block }}
{% endif %}

.. raw:: html

    </div>
"""