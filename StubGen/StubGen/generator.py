#!/usr/bin/env python3
"""
Генератор stub-пакетов для pip - с умными импортами (не трогаем __init__.py)
"""
import argparse

from .smartStubGenerator import SmartStubGenerator


def main():
    parser = argparse.ArgumentParser(description='Генератор stub-пакетов для pip (умные импорты)')
    parser.add_argument('package', help='Имя пакета для генерации stubs')
    parser.add_argument('-o', '--output', help='Директория для выходного пакета')
    
    args = parser.parse_args()
    
    generator = SmartStubGenerator()
    generator.generate_and_package(args.package, args.output)


if __name__ == "__main__":
    main()
