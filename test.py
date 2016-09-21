__author__ = 'jgevirtz'

import simpleorm as orm

class User(orm.Model):
    __table__ = "users"

    user_id = orm.Integer(primary=True)
    name = orm.String()


orm.connect(
    "localhost",
    "root",
    "root",
    "orm_test")

User.create_table()

user = User(name="Josh")
user.save()
print(user.user_id)
user.delete()

User.drop_table()
