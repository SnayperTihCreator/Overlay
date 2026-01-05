from datetime import date
from functools import wraps


def limit_calls_per_day(max_calls=3, debug=False):
    def decorator(func):
        call_count = 0
        last_call_date = None
        last_result = None  # Храним последний результат
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal call_count, last_call_date, last_result
            
            # Если debug=True, игнорируем ограничения
            if debug:
                last_result = func(*args, **kwargs)
                return last_result
            
            today = date.today()
            
            # Сброс счётчика, если дата изменилась
            if last_call_date != today:
                call_count = 0
                last_call_date = today
            
            # Если лимит исчерпан, возвращаем последний результат
            if call_count >= max_calls:
                return last_result
            
            call_count += 1
            last_result = func(*args, **kwargs)  # Обновляем кеш
            return last_result
        
        return wrapper
    
    return decorator
