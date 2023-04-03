def year(request):
    """Добавляет переменную с текущим годом."""
    import datetime
    return {
        'year': datetime.datetime.now().year,
    }
