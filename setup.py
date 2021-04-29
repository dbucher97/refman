from setuptools import setup
import setuptools.command.install as install


setup(
    name='refman',
    version='0.1',
    description='Reference Manager automatically generating BibTeX',
    license='GNU',
    packages=['refman'],
    scripts=['bin/ref'],
    author='David Bucher',
    author_email='David.Bucher@gmail.com',
    keywords=['latex', 'bibtex', 'pdf', 'reference', 'doi', 'arxiv', 'isbn'],
    url='https://github.com/dbucher97/refman',
    data_files=[('opt/refman/zsh/', ['zsh/_ref'])]
)
