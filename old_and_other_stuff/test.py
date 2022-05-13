
import random
import sqlite3
from datetime import timedelta, datetime

"""print(datetime.strptime("20/30/3/1/1/2022", '%S/%M/%H/%d/%m/%Y').strftime('%H:%M %d-%m-%Y'))"""
""" #print(datetime.strptime("20/30/3/1/1/2022", '%S/%M/%H/%d/%m/%Y') < datetime.strptime("20/30/3/1/1/2023", '%S/%M/%H/%d/%m/%Y') )
print(datetime.min , datetime.min < datetime.strptime("20/30/3/1/1/2023", '%S/%M/%H/%d/%m/%Y') ) """

"""
#print(type(datetime.utcnow() - datetime.utcnow()))
#print(type(datetime.utcnow()))


base = sqlite3.connect('./bases_863462268402532363/863462268402532363_shop.db')
#base = sqlite3.connect('.db')
cur = base.cursor() """
""" 
cur.execute('CREATE TABLE test(id INTEGER PRIMARY KEY AUTOINCREMENT, role INTEGER)')
base.commit() 

for i in range(1, 15):
    cur.execute(
        'INSERT INTO test(id, role) VALUES(?, ?)',
        (
            None,
            random.choice([1, 2, 4])
        )
    )
    base.commit()  """

""" for i in range(1, 15):
    cur.execute(
        'INSERT INTO shop(item_id, role_id, seller_id, price, date) VALUES(?, ?, ?, ?, ?)',
        (
            i,
            879139230201294868,
            705117706009051177,
            random.choice([100, 200, 300]),
            (
                datetime.utcnow()+timedelta(
                    hours=3,
                    minutes=random.choice(range(1, 59))
                )
            ).strftime('%S/%M/%H/%d/%m/%Y')
        )
    )
    base.commit() """
""" roles = [(972494065088200745, 100), (972494061569179718, 200), (972493931860353084, 300), (879139230201294868, 400)]
cur.executemany('INSERT INTO server_roles VALUES(?, ?)', roles)
base.commit() """


""" item_ids = [2, 3, 5]
free_id = 1
while(free_id < len(item_ids) + 1 and free_id == item_ids[free_id-1]):
        free_id += 1
print(free_id) """


"""print(type(base), type(cur)) 




    #time.sleep(0.1) """
""" for r in cur.execute('select memb_id from users').fetchall():
    print(str(type(r[0])) == "<class 'NoneType'>") """
""" dates = cur.execute('select date from shop').fetchall()
# date = dates[0]
# print(date)
# new_date = datetime.strptime(date, '%S/%M/%H/%d/%m/%Y')
# print(new_date.second)
# print(new_date.minute)
# print(new_date.hour)
# print(new_date.day)
# print(new_date.month)
# print(new_date.year)

# print(new_date)
# print(new_date.strftime('%H:%M %d-%m-%Y'))

print(datetime.strptime(dates[0][0], '%S/%M/%H/%d/%m/%Y'), datetime.strptime(dates[1][0], '%S/%M/%H/%d/%m/%Y'))
print(datetime.strptime(dates[0][0], '%S/%M/%H/%d/%m/%Y') > datetime.strptime(dates[1][0], '%S/%M/%H/%d/%m/%Y'))
 """

""" cur.close()
base.close()    """

"""
items = [1, 2, 3, 4, 5, 6, 7]
for i in zip(range(4), items):
    print(i)
"""