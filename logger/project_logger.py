import logging

def configure_logging(level=logging.INFO):
    '''Функция для настройки и конфигурации логера для проекта'''
    logging.basicConfig(
    level=level,#задаем уровень отображения логгеров(здесь от дебага и выше)
    format='[%(asctime)s] #%(levelname)-8s %(filename)s:'
           '%(lineno)d - %(name)s - %(message)s'
)

