from setuptools import setup, find_packages

setup(
    name='FreeFang',
    version='0.3.1',
    author='FreeFang Development Team',
    description='A libre implementation of the Werewolf game, also known as Mafia.',
    packages=find_packages(),
	entry_points={
		'console_scripts': [
			'freefang-server = freefang.main:main',
		],
	},

)

