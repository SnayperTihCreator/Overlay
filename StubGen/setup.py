from setuptools import setup, find_packages
import os


def find_stub_files(name):
    """Находит все stub-файлы в пакете"""
    stubs = []
    for root, dirs, files in os.walk(name):
        for file in files:
            if file.endswith('.pyi'):
                stubs.append(os.path.relpath(os.path.join(root, file), name))
    return stubs


setup(
    name="StubGen",
    version="0.1.0",
    description="Генератор и упаковщик stub-файлов для установки через pip",
    author="SnayperTihCreator",
    author_email="your.email@example.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    entry_points={
        'console_scripts': [
            'StubGen=StubGen.generator:main',
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7+",
    ],
)
