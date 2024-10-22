from setuptools import setup, find_packages

setup(name='CaipiraGames',
      version='1.0.0',
      description='ProjectAxis',
      url='https://github.com/CaipirUltron/CaipiraGames',
      author='Matheus Reis',
      license='GPLv3',
      packages=find_packages(include=['classes.*','images.*','other.*']),
      zip_safe=False,
      install_requires=[ 'numpy', 'pygame' ])