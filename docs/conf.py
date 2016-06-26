from os.path import join
from datetime import datetime

import sys
import os

# Alabaster theme + mini-extension
sys.path.append(os.path.abspath('_themes'))
html_theme_path = ['_themes']
extensions = ['alabaster']

# Paths relative to invoking conf.py - not this shared file
html_static_path = ['_shared_static']
html_theme = 'alabaster'
html_theme_options = {
    'logo': 'logo.jpg',
    'logo_name': True,
    'logo_text_align': 'center',
    'description': "Simplifying the process of extracting data from XML, so you can get on with more useful stuff",
    'github_user': 'spurin',
    'github_repo': 'xmldataset',
    'github_type': 'star',
    'github_banner': True,
    'travis_button': True,

    'link': '#3782BE',
    'link_hover': '#3782BE',
}
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'searchbox.html',
        'donate.html',
    ]
}

# Regular settings
project = 'xmldataset'
year = datetime.now().year
copyright = '%d James Spurin' % year
master_doc = 'index'
templates_path = ['_templates']
exclude_trees = ['_build']
source_suffix = '.rst'
default_role = 'obj'
