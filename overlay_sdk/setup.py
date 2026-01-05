from setuptools import setup, find_packages

setup(
    name='overlay_sdk',
    version='1.0.0',
    author='SnayperTihCreator',
    packages=find_packages(),
    data_files=[
        ('', ['oapi.pyi'])
    ],
    package_data={
        'overlay_sdk': ['templates/*', 'templates/**/*', '*.pyi'],
    },
    include_package_data=True,
)