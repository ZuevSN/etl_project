#etl_project.main.py

import logging
import random
import etl_project.csv_handler as h
from etl_project import filter_func as f
from etl_project import db_loader
from etl_project.decorators import isolated_process

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
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
    passenger_data = h.get_rows('tested.csv',5)
    # print(passenger_data)
    logger.info(h.get_len('tested.csv'))
    filters = [
        (f.minValue,'Age', 30),
        (f.maxValue,'Fare', 7)
    ]
    filtered_passenger_data = h.get_rows('tested.csv',filters=filters)
    # print(filtered_passenger_data)
    fixed_passenger_data = h.get_rows('tested.csv')
    for row in fixed_passenger_data:
        try:
            fare = float(row['Fare'])
            row['col1'] = fare*0.2
        except:
            row['col1'] = 0
    # print(fixed_passenger_data)
    h.write_file('tested111.csv',fixed_passenger_data)    



def main():
    logger.info('Запуск ETL приложения')
    process_sample_data()
    process_csv_data()
    db_loader.loader()
    print("конец")
    logger.info('Остановка ETL приложения')


if __name__=='__main__':
    main()