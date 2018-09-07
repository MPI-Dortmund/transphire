"""
    TranSPHIRE is supposed to help with the cryo-EM data collection
    Copyright (C) 2017 Markus Stabrin

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


import re
import abc
import inspect


def check_interface(parent_instance):
    """
    Decorator that passes the parent instance for sanity checks.
    """
    def check_existence(func):
        """
        Decorator that passes the function to execute it.
        """
        def wrap(*args, **kwargs):
            """
            Execute the actual function after checking the existence in the interface class.
            """
            func_name = args[1]
            new_args = args[1:]

            try:
                getattr(parent_instance, func_name)()
            except AttributeError as e:
                function_names = '\n'.join(sorted(list(inspect.getmembers(parent_instance)[0][1])))
                raise AttributeError(f'Interface instance "{parent_instance}" does not yet have a method named "{func_name}": Choose\n{function_names}') from e

            return_value = func(args[0], *new_args, **kwargs)
            return return_value
        return wrap
    return check_existence


class InterfaceClass(abc.ABC):
    """
    Abstract interface class.
    It does not allow creation of an instance.

    Inherits:
    abc.ABC
    """

    @staticmethod
    @abc.abstractmethod
    def get_content():
        """
        Returns the content entry of the external program.
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def get_type():
        """
        Returns the type entry of the external program.

        For example:
        software, motion, ctf, picking, compress, ...
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def get_name():
        """
        Returns the name entry of the external program.

        For example:
        EPU, MotionCor2, CTER, crYOLO, ...
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def get_version():
        """
        Returns the version entry of the external program.

        For example:
        1.11, 1.1.1, 1.0.0, ...
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def get_pre_first_command():
        """
        Returns the command that will be executed before the first command.
        """
        pass


    @staticmethod
    @abc.abstractmethod
    def get_first_command():
        """
        Returns the command that will be executed as the first command.
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def get_post_first_command():
        """
        Returns the command that will be executed after the first command.
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def get_pre_second_command():
        """
        Returns the command that will be executed before the second command.
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def get_second_command():
        """
        Returns the command that will be executed as the second command.
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def get_post_second_command():
        """
        Returns the command that will be executed after the second command.
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def get_pre_third_command():
        """
        Returns the command that will be executed before the third command.
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def get_third_command():
        """
        Returns the command that will be executed as the third command.
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def get_post_third_command():
        """
        Returns the command that will be executed after the third command.
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def get_pre_final_command():
        """
        Returns the command that will be executed before the final command.
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def get_final_command():
        """
        Returns the command that will be executed as the final command.
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def get_post_final_command():
        """
        Returns the command that will be executed after the final command.
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def get_import_data():
        """
        Returns the command that will import the data.
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def get_output_files():
        """
        Returns the suffixes of the output file for sanity checks.
        """
        pass


class TemplateClass(object):
    """
    TemplateClass

    It wraps the settings of the software.

    Inherits:
    object
    """

    def __init__(self, external_dict):
        self.external_dict = external_dict

    @check_interface(InterfaceClass)
    def run_step(self, name):
        """
        Return the value of the external_dict.

        Arguments:
        external_dict: Dictionary containing the program information.

        Returns:
        Value of the dictionar key.
        """
        return self.external_dict[name]
