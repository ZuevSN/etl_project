#etl_project.main.py

import logging
import random
import etl_project.csv_handler as h
from etl_project import filter_func as f
from etl_project import db_loader
from etl_project.decorators import isolated_process
from etl_project.config import AppConfig

DEFAULTS={}

conf = AppConfig(DEFAULTS)

logging.basicConfig(
    level=conf.get('LEVEL_LOG'),
    format=conf.get('FORMAT_LOG'),
    datefmt=conf.get('DATE_FMT')
)

logger = logging.getLogger(__name__)

def do_list(n):
    my_list = []
    if n-1>0:
        for i in range(n):
            my_list.append(random.randint(1,10))
    return my_list

def is_even(num):
    return num % 2 == 0

def sqr_list(my_list):
    new_list=[]
    for i in my_list:
        new_list.append(i*i)
    return new_list

@isolated_process("Обработка простого списка")
def process_sample_data():
    my_list = do_list(10)
    my_even_list = list(filter(is_even, my_list))
    my_sqr_list = sqr_list(my_even_list)
    logger.info(my_list)
    logger.info(my_even_list)
    logger.info(my_sqr_list)

@isolated_process("Загрузка, обработка, выгрузка csv")
def process_csv_data():
    logger.info(h.get_len('tested.csv'))
    filters = [
        (f.minValue,'Age', 30),
        (f.maxValue,'Fare', 7)
    ]
    filtered_passenger_data = h.get_rows('tested.csv',filters=filters)
    h.write_file('filtered_tested.csv',filtered_passenger_data) 
    fixed_passenger_data = h.get_rows('tested.csv')
    for row in fixed_passenger_data:
        fare = to_float(row['Fare'])
        row['Tax'] = fare*0.2
    h.write_file('tested111.csv',fixed_passenger_data)    

def to_float(value):
    return value if isinstance(value,(float,int)) and not isinstance(value,bool) else 0
    

def main():
    logger.info('Запуск ETL приложения')
    process_sample_data()
    process_csv_data()
    db_loader.loader(conf.get('DATABASE_URL'))
    process_sample_data()
    logger.info('Остановка ETL приложения')


if __name__=='__main__':
    main()