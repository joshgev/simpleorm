# simpleorm

Simpleorm is just an small toy MySQL ORM that was written for educational purposes.  Popular Python ORMs like SQLAlchemy 
and Django's ORM are both feature-rich ORMs that might seem  magical to beggining Python programmers.  This sample is meant 
to demonstrate how this magic is implemented in the back end.  In particular, this sample ORM provides an easy-to-understand 
example of meta programming in Python via metaclasses.

This is by no means mean to be a production-ready system.  It is just a toy!

# Requirements

The only requirement for this package is mysqlclient.

# Installation
To install, use pip:

```
pip install git+git://github.com/joshgev/simpleorm
```

# Example

This package requires access to a working MySQL server.  This example assumes a MySQL server to be running on 
localhost witha database named "orm_test" and username/password both set to "root."

```python
import simpleorm as orm

# Connect ORM to the database server
orm.connect(
    "localhost",
    "root",
    "root",
    "orm_test")
```

If the database doesn't already have the schema installed, we can do it with our ORM:
```python
User.create_table()
```

Let's define a model to represent a user in some system
```python
class User(orm.Model):
    user_id = orm.Integer(primary=True)
    first_name = orm.String()
    last_name = orm.String()
    
```

Now we can use our model to create and save users:

```python
user1 = User(first_name="Ann", last_name="Smith")
user2 = User(first_name="Bob", last_name="Smith")
user1.save()
user2.save()
```

Of course, we can load users from the database:

```python
one_smith = User.get_one(first_name="Ann")
all_smiths = User.get_many(last_name="Smith")
```
Finally, we can delete a user:
```python
ann = User.get_one(first_name="Ann")
ann.delete()
```

Optionally, we can destroy the schema through the ORM:
```python
User.drop_table()
```
