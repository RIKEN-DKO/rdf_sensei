from setuptools import setup, find_packages

setup(
    name='rdfsensei',  # Lowercase for pip installation
    version='0.1.0',
    description='A tool for querying RDF databases',
    author='JC. Rangel',
    author_email='jcrangel@protonmail.com',
    packages=find_packages(include=['rdfsensei', 'rdfsensei.*']),
    install_requires=[
        # List your dependencies here
        'requests',  # Example dependency
    ],
    entry_points={
        'console_scripts': [
            'rikenquery=rikenquery.main:main',  # Update with your entry point
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
