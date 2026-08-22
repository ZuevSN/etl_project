#etl_project.main.py
import random
import etl_project.file as r
from etl_project import filter_func as f

def do_list(n):
    my_list = []
    if n-1>0:
        for i in range(n):
            my_list.append(random.randint(1,10))
    return my_list

def is_even(num):
    if num % 2 == 0:
        return num

def sqr_list(my_list):
    new_list=[]
    for i in my_list:
        new_list.append(i*i)
    return new_list

def ex1():
    my_list = do_list(10)
    my_even_list = list(filter(is_even, my_list))
    my_sqr_list = sqr_list(my_even_list)
    print(my_list)
    print(my_even_list)
    print(my_sqr_list)

def ex2():
    my_list1 = r.get_rows('tested.csv',5)
    print(my_list1)
    print(r.get_len('tested.csv'))
    filters = [
        (f.minValue,'Age', 30),
        (f.maxValue,'Fare', 7)
    ]
    my_list2 = r.get_rows('tested.csv',filters=filters)
    print(my_list2)
    my_list3 = r.get_rows('tested.csv')
    for row in my_list3:
        try:
            fare = float(row['Fare'])
            row['col1'] = fare*0.2
        except:
            row['col1'] = 0
    print(my_list3)
    r.write_file('tested111.csv',my_list3)    

def main():
 ex1()
 ex2()



if __name__=='__main__':
    main()