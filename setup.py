from setuptools import setup, find_packages

# try:
#     import pypandoc
#     l_d = pypandoc.convert('README.md', )
# except ModuleNotFoundError:
l_d = ''

# Get the version.
version: dict = {}
with open("version.py") as fp:
    exec(fp.read(), version)
setup(
    name='pastastore',
    version=version['__version__'],
    description='pastastore module by Artesia',
    long_description=l_d,
    url='https://artesia-water.nl',
    author='Artesia',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    platforms='Windows, Mac OS-X',
    install_requires=['numpy>=1.15', 'pandas>=0.24', "tqdm",
                      "pastas>=0.13", "arctic"],
    packages=find_packages(exclude=[]),
    include_package_data=True,
)
