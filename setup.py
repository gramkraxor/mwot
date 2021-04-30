from pathlib import Path
import setuptools

long_description = Path('README.md').read_text()

setuptools.setup(
    name='mwot',
    version='0.0.0.dev0',
    author='Gramkraxor',
    author_email='gram@krax.dev',
    url='https://github.com/gramkraxor/mwot',
    description='An esolang',
    long_description=long_description,
    long_description_content_type='text/markdown',
    keywords=['esolang', 'esoteric language', 'brainfuck'],
    license='Unlicense',
    classifiers=[
        'License :: OSI Approved :: The Unlicense (Unlicense)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Interpreters',
    ],
    packages=setuptools.find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'mwot = mwot.cli:main',
            'mwot-i-bf = mwot.cli:mwot_i_bf',
            'mwot-x-bf = mwot.cli:mwot_x_bf',
        ],
    },
)
