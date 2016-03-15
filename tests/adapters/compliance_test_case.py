from unittest import SkipTest

from tests import available_models
from tests.adapters.configured_test_case import ConfiguredTestCase
import sys


def _wrap_tests_with_not_implemented_tolerance(test_class):
    for method in dir(test_class):
        if method.startswith("test_"):
            _wrap_test_method(method, test_class)
    print(dir(test_class))
    return test_class


def _wrap_test_method(method, test_class):
    old_method = getattr(test_class, method)

    def wrapper(obj):
        try:
            old_method(obj)
        except NotImplementedError:
            raise SkipTest("Method is not implemented")
    wrapper.__name__ = method
    setattr(test_class, method, wrapper)


class AutoRegisteringClasse(type):
    def __new__(mcs, name, bases, attrs):
        test_class = type.__new__(mcs, name, bases, attrs)
        if bases[0].__name__ == "ComplianceTestCase":
            test_class.__test__ = False
            for _specs in available_models:
                class_name = "{}{}".format(_specs["switch_descriptor"].model.capitalize(), name)
                new_test_class = type(class_name, (test_class,), {"__test__": True, "switch_specs": _specs})
                setattr(sys.modules[test_class.__module__], class_name, _wrap_tests_with_not_implemented_tolerance(new_test_class))
        return test_class


class ComplianceTestCase(ConfiguredTestCase):
    __metaclass__ = AutoRegisteringClasse

