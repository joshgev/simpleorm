__author__ = 'jgevirtz'

import simpleorm as orm

class User(orm.Model):
    __table__ = "users"

    id = orm.Integer('id', primary=True)
    name = orm.String("name")


orm.connect(
    "localhost",
    "root",
    "root",
    "orm_test")

User.create_table()

user = User(id=1, name="Josh")
user.save()
user.delete()

User.drop_table()
