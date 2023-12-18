from setuptools import setup, find_packages

setup(name='caipiragames',
      version='1.0.0',
      description='The Ultimate Caipira Experience',
      url='https://github.com/CaipirUltron/CaipiraGames',
      author='Matheus Reis',
      author_email = "matheus.ferreira.reis@gmail.com",
      license='GPLv3',
      packages=find_packages(include=['CaipiraGames.*']),
      zip_safe=False,
      install_requires=[ 'numpy', 'pygame', 'pymunk' ])