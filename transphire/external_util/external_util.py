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


def check_return(number, type_return, type_entry, return_value):
    if type_return is None:
        assert return_value is type_return
    else:
        assert isinstance(return_value, type_return)

    if number == 1:
        if type_entry is None:
            assert return_value is type_entry
        else:
            assert isinstance(return_value, type_entry)
    else:
        dtypes = []
        if isinstance(type_entry, list):
            dtypes.extend(type_entry)
        else:
            dtypes.extend([type_entry for _ in range(number)])
        assert len(dtypes) == number

        for value, entry in zip(return_value, dtypes):
            if entry is None:
                assert value is None
            else:
                assert isinstance(value, entry)


def check_interface(parent_instance):
    def check_arguments(func):
        def wrap(*args, **kwargs):
            self = args[0]
            func_name = args[1]
            args = args[2:]

            test_name = re.match(r'.*\.([^ ]+) .*', str(func)).group(1).split('__')[0]
            method = getattr(parent_instance, test_name)
            number, type_return, type_entry = method(*args, **kwargs)
            return_value = func(self, static_args=args, static_kwargs=kwargs, name=func_name)

            check_return(
                number=number,
                type_return=type_return,
                type_entry=type_entry,
                return_value=return_value
                )

            return return_value
        return wrap
    return check_arguments
