# -*- coding: utf-8 -*-
import PIL

### general configuration ###

needs_sphinx = '1.0'

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode',
              'sphinx.ext.intersphinx']
intersphinx_mapping = {'http://docs.python.org/2/': None}

source_suffix = '.rst'
templates_path = ['_templates']
#source_encoding = 'utf-8-sig'
master_doc = 'index'

project = u'Pillow (PIL fork)'
copyright = (u'1997-2011 by Secret Labs AB,'
             u' 1995-2011 by Fredrik Lundh, 2010-2013 Alex Clark')

# The short X.Y version.
version = PIL.PILLOW_VERSION
# The full version, including alpha/beta/rc tags.
release = version

# currently excluding autodoc'd plugs
exclude_patterns = ['_build', 'plugins.rst']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

### HTML output ###

#from better import better_theme_path
#html_theme_path = [better_theme_path]
#html_theme = 'better'

html_title = "Pillow v{release} (PIL fork)".format(release=release)
html_short_title = "Home"
html_static_path = ['_static']

html_theme_options = {}

html_sidebars = {
    '**': ['localtoc.html', 'sourcelink.html', 'sidebarhelp.html',
           'searchbox.html'],
    'index': ['globaltoc.html', 'sidebarhelp.html', 'searchbox.html'],
}

# Output file base name for HTML help builder.
htmlhelp_basename = 'Pillowdoc'


### LaTeX output (RtD PDF output as well) ###

latex_elements = {}

latex_documents = [
    ('index', 'Pillow.tex', u'Pillow (PIL fork) Documentation', u'Author',
     'manual'),
]


# skip_api_docs setting will skip PIL.rst if True. Used for working on the
# guides; makes livereload basically instantaneous.
def setup(app):
    app.add_config_value('skip_api_docs', False, True)

skip_api_docs = False

if skip_api_docs:
    exclude_patterns += ['PIL.rst']
