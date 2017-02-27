import ricecake
from setuptools import setup

setup(name='ricecake',
	version='0.1',
	description='Ricecooker dependent package to upload file structure to Kolibri',
	url='http://github.com/msaxe/',
	author='Mark Saxer',
	author_email='masaxer@cox.net',
	license='MIT',
	packages=['ricecake'],
	install_requires=[
		'ricecooker',
		'configparser',
	],
	entry_points={
		'console_scripts': [
			'ricecake=ricecake.cli:main'
		]
	},
	zip_safe=False
)