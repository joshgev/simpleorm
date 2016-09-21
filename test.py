__author__ = 'jgevirtz'

import simpleorm as orm

class User(orm.Model):
    user_id = orm.Integer(primary=True)
    first_name = orm.String()
    last_name = orm.String()


orm.connect(
    "localhost",
    "root",
    "root",
    "orm_test")

User.create_table()

user1 = User(first_name="Ann", last_name="Smith")
user2 = User(first_name="Bob", last_name="Smith")
user1.save()
user2.save()

one_smith = User.get_one(first_name="Ann")
print (one_smith.first_name)
all_smiths = User.get_many(last_name="Smith")
for s in all_smiths:
    print(s.first_name)

ann = User.get_one(first_name="Ann")
ann.delete()

User.drop_table()
