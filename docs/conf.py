"""Sphinx configuration for the Gecko documentation."""

from gecko import __version__

# -- Project information -----------------------------------------------------

project = "Gecko"
author = "Caltech Optical Observatories"
copyright = "Caltech Optical Observatories"
release = __version__
version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinxarg.ext",
    "sphinx.ext.githubpages",
]

source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

myst_enable_extensions = ["colon_fence", "deflist"]
myst_heading_anchors = 3

autodoc_member_order = "bysource"
autodoc_default_options = {"members": True, "show-inheritance": True}
napoleon_google_docstring = True
napoleon_numpy_docstring = False

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

# Strip "$ " prompts when copying shell examples.
copybutton_prompt_text = r"\$ "
copybutton_prompt_is_regexp = True

# -- HTML output -------------------------------------------------------------

html_theme = "shibuya"
html_title = "Gecko"
html_baseurl = "https://caltechopticalobservatories.github.io/gecko/"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_copy_source = False
html_show_sourcelink = False

html_theme_options = {
    "accent_color": "grass",
    "github_url": "https://github.com/CaltechOpticalObservatories/gecko",
    "nav_links": [
        {"title": "Install", "url": "installation"},
        {"title": "Operator guide", "url": "operator-guide"},
        {"title": "Configuration", "url": "configuration"},
        {"title": "Issues", "url": "https://github.com/CaltechOpticalObservatories/gecko/issues"},
    ],
    "globaltoc_expand_depth": 1,
}

# Enables the "Edit this page" link.
html_context = {
    "source_type": "github",
    "source_user": "CaltechOpticalObservatories",
    "source_repo": "gecko",
    "source_version": "main",
    "source_docs_path": "/docs/",
}
