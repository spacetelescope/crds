"""This module defines dictionary-like clasess of various forms nominally used to support
CRDS mappings:

TransformedDict --   generic MutableMapping with key and value transforms
    Derived from discussion at http://stackoverflow.com/questions/3387691/python-how-to-perfectly-override-a-dict

LazyFileDict   --  Demand loaded network of files (aka CRDS context)

"""

import collections

# =============================================================================

class TransformedDict(dict):

    """A dictionary that applies an arbitrary key and value altering functions
    before accessing the keys and values.
    """
    
    def __init__(self, initializer=()):
        super(TransformedDict, self).update(
            { self.transform_key(key): self.transform_value(val) 
              for (key, val) in dict(initializer).items() })

    def transform_key(self, key):
        """Abstract pass-thru key transformation,  override needed."""
        return key

    def transform_value(self, value):
        """Abstract pass-thru value transformation,  override as needed."""
        return value

    def __getitem__(self, key):
        return super(TransformedDict, self).__getitem__(self.transform_key(key))

    def __setitem__(self, key, value):
        super(TransformedDict, self).__setitem__(self.transform_key(key), self.transform_value(value))

    def __delitem__(self, key):
        super(TransformedDict, self).__delitem__(self.transform_key(key))

    def __contains__(self, key):
        return super(TransformedDict, self).__contains__(self.transform_key(key))

    def get(self, key, default=None):
        """Returns either value associated with `key` or transformed `default` value."""
        tkey = self.transform_key(key)
        if tkey in self:
            return self.transformed_value(tkey)
        else:
            return default
    
    def __repr__(self):
        """
        >>> TransformedDict([("this","THAT"), ("ANOTHER", "(ESCAPED)")])
        TransformedDict({'this': 'THAT', 'ANOTHER': '(ESCAPED)'})
        """
        return self.__class__.__name__ + "({})".format(self.items())

# =============================================================================

class LazyFileDict(TransformedDict):
    """Instantiates a graph of inter-referencing files (like CRDS Mappings) on
     demand basis as particular paths are accessed.

    Manages selections for higher level mappings like .pmaps and .imaps which
    refer to other mapping files.  Loads submappings on a demand basis rather
    than exhaustively at startup.  This is motivated by a need to minimize file
    operations in web/cloud applications and highly concurrent environments
    like calibration pipelines.  It opens the potential for only loading a
    single instrument under a given context.

    Values included in special_values_set are excluded from nested loading
    and kept as literals,  e.g. N/A 
    """

    special_values_set = set()   # Override in sub-classes as needed

    loader = None   # must be set to callable that loads subtree file.

    def __init__(self, selector, load_keys):
        super(LazyFileDict, self).__init__()
        self._selector = {self.transform_key(key): value for (key, value) in dict(selector).items()}
        self._load_keys = load_keys
        assert self.loader is not None, "Subclasses must define 'cls.loader'"

    @classmethod
    def is_special_value(cls, value):
        """Returns True IFF `value` is a string in cls.special_values_set.
        Nominally this means the value has no recursive load operation, it's
        a literal.
        """
        return isinstance(value, str) and value in cls.special_values_set
        
    def __getitem__(self, name):
        name = self.transform_key(name)
        if name in self._selector:
            try:
                val = super(LazyFileDict, self).__getitem__(name)
            except KeyError:
                if self.is_special_value(self._selector[name]):
                    val = self._selector[name]
                else:
                    val = self.loader(self._selector[name], **self._load_keys)
                super(LazyFileDict, self).__setitem__(name, val)
            return val
        else:
            raise KeyError(name)

    def __setitem__(self, name, value):
        name = self.transform_key(name)
        self._selector[name] = value.filename
        super(LazyFileDict, self).__setitem__(name, value)

    def __delitem__(self, name):
        name = self.transform_key(name)
        del self._selector[name]
        super(LazyFileDict, self).__delitem__(name)

    def __contains__(self, key):
        return self.transform_key(key) in self.keys()

    def __iter__(self):
        return iter(self.keys())

    def __len__(self):
        return len(self._selector)

    def keys(self):
        """
        NOTE:  does not require full load
        """
        return self._selector.keys()

    def normal_keys(self):
        """Each of these keys has a corresponding value which IS NOT special.
        
        NOTE:  Does not require full load.
        """
        return sorted([key for key in self.keys() if not self.is_special_value(self._selector[key])])

    def special_keys(self):
        """Each of these keys has a corresponding values which IS special.
        
        NOTE:  Does not require full load.
        """
        return sorted([key for key in self.keys() if self.is_special_value(self._selector[key]) ]) 

    def values(self):
        """Return all the values of this LazyFileDict,  implicitly loading them all.

        NOTE:  REQUIRES FULL LOAD
        """
        return [self[name] for name in self.keys()]  

    def normal_values(self):
        """Normal values exclude the special values like N/A but can include exotic values like tuples or dicsts.
        
        NOTE:  REQUIRES FULL LOAD
        """
        return [ self[key] for key in self.normal_keys() ]

    def special_values(self):
        """These are values which must be trapped and reformatted in the Mapping classes."""
        return [ self[key] for key in self.special_keys() ]

    def items(self):
        """Return all the items of this LazyFileDict, implicitly loading all values.

        NOTE:  REQUIRES FULL LOAD
        """
        return self._items(self.keys())

    def normal_items(self):
        """Return only those items that have recursively loaded values.

        NOTE:  REQUIRES FULL LOAD
        """
        return self._items(self.normal_keys())

    def special_items(self):
        """Return only those items that have exempt literal values with no recursive loading."""
        return self._items(self.special_keys())
    
    def _items(self, keys):
        """Constructs item list taken from self based on `keys`."""
        return [ (key, self[key]) for key in keys ]

