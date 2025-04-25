# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'MovieBot'
copyright = '2025, Novikov D.V., Polyakova V.V, Prepelitsa P.P.'
author = 'Novikov D.V., Polyakova V.V, Prepelitsa P.P.'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx_rtd_theme',
    'sphinx.ext.autosummary',  # Добавьте это
    'sphinx_autodoc_typehints'  # Если установили этот пакет
]

# Пути к коду (ваш вариант правильный для вашей структуры)
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

# Тема
html_theme = 'sphinx_rtd_theme'

# Дополнительные настройки
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}


templates_path = ['_templates']
exclude_patterns = []

language = 'ru'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
