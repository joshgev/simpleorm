__author__ = 'jgevirtz'

import MySQLdb as mysql

DROP_TABLE_TEMPLATE = "DROP TABLE `{}`"
INSERT_TEMPLATE = "INSERT INTO `{table}`({flist}) VALUES ({vlist})"
DELETE_TEMPLATE = "DELETE FROM `{table}` WHERE `{column}`=%s"
SELECT_TEMPLATE = "SELECT {flist} FROM `{table}` WHERE `{column}`=%s"

_db = None

def connect(host, user, pword, db):
    """
    Form a connection to the MySQL database.
    :return: None
    """
    global _db
    _db = mysql.connect(host=host,
                   user=user,
                   passwd=pword,
                   db=db)

class _Field(object):
    """
    Base class for model fields, which correspond to table columns.
    """
    def __init__(self, name, primary=False):
        """
        Initializer for field.

        :param name: the column name as it will exist in the MySQL DB
        :param primary: whether this is a primary key or not
        :return: None
        """
        self.name = name
        self.primary = primary
        self.clazz = None

    def type(self):
        """
        Returns the type of the MySQL column that should be used to represent
        this column. Look at String and Field for examples.

        :return: a string
        """
        raise NotImplemented()

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return "Field:{}".format(self.type())




class String(_Field):
    """
    A string field
    """

    def type(self):
        return "TEXT"


class Integer(_Field):
    """
    An integer field
    """
    def type(self):
        return "BIGINT"


class _ModelMeta(type):
    """
    Metaclass for Model objects.  The only functionality provided by this metaclass
    is the scanning of fields defined on Models; knowledge of which fields
    are defined on each model is important for a number of operations including
    creating a Model's associated field.
    """
    def __new__(cls, name, bases, dict):
        """
        The __new__ method is the method used by Python when creating an object.  Since
        we will use _ModelMeta as a metaclass, the objects getting created will be classes
        (remember, everything is an object in Python :]).

        We are interested in creating classes with two pre-set attributes: _fields, which
        is a list of fields declared on a Model and _primary, which is the primary field
        (as defined by the the "primary" keyword argument in the Field __init__ method).
        As an example of what this means, suppose we declare a class using this metaclass:

        class Example(object, metclass=_ModelMeta):
            id = Integer("id", primary=True)
            name = String("name")
            def __init__(self):
                # In this method, we automatically have self._fields and
                self._primary.  The former is a list containing an instance
                of String and an instance of Integer.  The latter is the instance
                of Integer.

                ...

        """

        # This if aborts our special logic if no __table__ is defined on the class.
        # The assumption is that if __table__ is not defined, we are currently calling
        # __new__ on the Model class, not one of its subclasses.  The easiest way to
        # understand what is going on is to comment this statement out and seeing what
        # happens: you should get an assertion error.
        if '__table__' not in dict:
            return super(_ModelMeta, cls).__new__(cls, name, bases, dict)

        # Gather fields and determine the primary key
        fields = [v for k, v in dict.items() if isinstance(v, _Field)]
        primary = [f for f in fields if f.primary]

        # There should only be one primary key
        assert len(primary) == 1, len(primary)

        # This dict represents the attributes that will be set on the newly created object.
        dict['_fields'] = fields
        dict['_primary'] = primary[0]
        return super(_ModelMeta, cls).__new__(cls, name, bases, dict)


class Model(object, metaclass=_ModelMeta):
    """
    This is the superclass for models.  An example of this class might look like this:

    class User(Model):
        __table__ = "users"

        id = Integer("id", primary=True)
        first_name = String("fname")
        last_name = String("lname")
        age = Integer("age")

    """

    def __init__(self, **kwargs):
        """
        Keys in the kwargs dict should be field names of fields declared on this model.
        The values should be values for those.  Using the example User model defined above,
        for example, calling __init__ might look like this:

        user = User(first_name="John", last_name="Smith", age=27)
        """

        # Make sure all specified attributes are part of this model
        attributes = set(kwargs.keys())
        field_names = set(f.name for f in self._fields)
        assert attributes & field_names == attributes

        # Save the values for later use, e.g. when saving the model using Model.save()
        self.values = kwargs

    @classmethod
    def create_table(cls):
        """
        Create a table corresponding to this model.
        """
        cursor = _db.cursor()
        sql = "CREATE TABLE `{}` ".format(cls.__table__)
        field_list = []
        for f in cls._fields:
            if f.primary:
                field_list.append("`{}` {} NOT NULL AUTO_INCREMENT".format(f.name, f.type()))
            else:
                field_list.append("`{}` {}".format(f.name, f.type()))

        field_list.append("PRIMARY KEY (`{}`)".format(cls._primary.name))

        field_list = ",".join(field_list)
        sql = "{} ({})".format(sql, field_list)
        cursor.execute(sql)
        cursor.close()
        _db.commit()

    @classmethod
    def drop_table(cls):
        """
        Drop the table represented by this model.
        """
        cursor = _db.cursor()
        sql = DROP_TABLE_TEMPLATE.format(cls.__table__)
        cursor.execute(sql)
        cursor.close()
        _db.commit()

    @classmethod
    def _get(cls, **kwargs):
        """
        Do an SQL SELECT and return the results as a list of instances of this Model. This
        method shouldn't be used by non-member methods.  Instead, the methods get_one
        and get_many are provided for use.

        Using the User model defined above, calling User._get(first_name="John") will result
        in a list User instances represnting all users in the database whose first name is "John."

        Note that this method only allows one test in the WHERE clause (i.e., we can't find users
        whose first name is "John" and whose age is 20).
        """

        # Make sure that they attribute we are searching on is actually defined on this model.
        assert len(kwargs) == 1
        k, v = [(k, v) for k, v in kwargs.items()][0]
        f = _Field(k)
        assert f in cls._fields

        flist = ",".join(str(f.name) for f in cls._fields)
        sql = SELECT_TEMPLATE.format(flist=flist, table=cls.__table__, column=k)
        print(sql)
        cursor = _db.cursor()
        cursor.execute(sql, [v])
        results = []
        for row in cursor:
            kwargs = dict((k.name, v) for k, v in zip(cls._fields, row))
            results.append(cls(**kwargs))
        return results

    @classmethod
    def get_one(cls, **kwargs):
        return cls._get(**kwargs)[0]

    @classmethod
    def get_many(cls, **kwargs):
        return cls._get(**kwargs)

    def __getattribute__(self, item):
        """
        Values for model instances are stored in a dict: self.values (set in the __init__ method).
        To access these values in a clean way (as opposed to model.values['first_name'])
        we have to do a bit of work.  The most natural way to access model values is probably:

        model.field1

        where model is an instance of a subclass of Model and field1 is a _Field declared on that model.

        However, since field1 is a declared on the model, calling model.field1 without some
        special mechanism will result in an instance of a _Field subclass, which is useless.

        This method solves this problem. When an attribute of a model instance is requested,
        a check is made to determine whether the requested attribute is a _Field.  If it is
        the corresponding value from self.values is returned.  Otherwise, the object's attribute
        is returned normally.
        """
        if not isinstance(object.__getattribute__(self, item), _Field):
            return object.__getattribute__(self, item)
        return self.values.get(item, None)

    def save(self):
        """
        Perform an SQL insert.
        """
        fields = self.values.keys()
        values = [self.values[k] for k in fields]

        field_list = ",".join(["`{}`".format(f) for f in fields])
        values_list = ",".join(["%s"] * len(fields))
        sql = INSERT_TEMPLATE.format(table=self.__table__, flist=field_list, vlist=values_list)

        cursor = _db.cursor()
        cursor.execute(sql, values)
        cursor.close()
        _db.commit()

    def delete(self):
        """
        Delete instance's corresponding row.
        """
        primary = object.__getattribute__(self, '_primary')
        sql = DELETE_TEMPLATE.format(
            table=self.__table__,
            column=primary.name)
        cursor = _db.cursor()
        cursor.execute(sql, [self.values[primary.name]])

