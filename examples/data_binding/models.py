"""
Created on Apr 28, 2017

@author: jrm
"""
from atom.api import Atom, ContainerList, Unicode, Int, Enum, Bool, observe


class Employee(Atom):

    name = Unicode()
    age = Int()
    gender = Enum("", "male", "female")
    current = Bool()
    
    @observe('name', 'age', 'gender', 'current')
    def _log_change(self, change):
        pass


class Company(Atom):

    employees = ContainerList(Employee, default=[
        Employee(name="John Doe", age=54, gender="male", current=True),
        Employee(name="Jill Smith", age=37, gender="female", current=True),
        Employee(name="Brian Jones", age=22, gender="male", current=True),
        Employee(name="Bob Jones", age=62, gender="male", current=False),
    ])
