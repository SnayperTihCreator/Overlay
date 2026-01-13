import os
import sys
import modulegraph.modulegraph as mg

# Пути
search_paths = sys.path
base_path = os.path.abspath(os.getcwd())
entry_point = os.path.join(base_path, 'src', 'overlay.py')

graph = mg.ModuleGraph(search_paths)
graph.run_script(entry_point)

himpr = ["json", "psutil", "cProfile", "xml.etree.ElementTree", "requests", "numpy", "colorama", "PySide6.QtCharts"]

print(f"\n{'Модуль':<25} | {'Кто импортировал (родитель)'}")
print("-" * 80)

for target in himpr:
    node = graph.findNode(target)
    if node:
        # Получаем список всех модулей, которые импортируют этот target
        # get_edges(node)[1] — это входящие связи (referrers)
        referrers = graph.get_edges(node)[1]
        
        if not referrers:
            # Такое бывает, если это точка входа или built-in без явных связей
            print(f"{target:<25} | Напрямую в {os.path.basename(entry_point)} (или точка входа)")
            continue
        
        for ref in referrers:
            # Фильтруем, чтобы показывать в основном твои файлы (из папки src)
            # или важные пакеты, а не гору стандартных либ
            ref_id = ref.identifier
            ref_file = getattr(ref, 'filename', 'Built-in')
            
            # Делаем путь относительным для красоты
            if ref_file and os.path.isabs(str(ref_file)):
                ref_file = os.path.relpath(ref_file, base_path)
            
            print(f"{target:<25} | {ref_id:<30} [Файл: {ref_file}]")
    else:
        print(f"{target:<25} | --- НЕ ИСПОЛЬЗУЕТСЯ В КОДЕ ---")