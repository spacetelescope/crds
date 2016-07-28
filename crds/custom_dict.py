"""This module defines dictionary-like clasess of various forms nominally used to support
CRDS mappings:

TransformedDict --   generic MutableMapping with key and value transforms
    Derived from discussion at http://stackoverflow.com/questions/3387691/python-how-to-perfectly-override-a-dict

LazyFileTree   --  Demand loaded network of files (aka CRDS context)

"""

import collections

# =============================================================================

class TransformedDict(collections.MutableMapping):

    """A dictionary that applies an arbitrary key and value altering functions
    before accessing the keys and values.
    """
    
    def __init__(self, *args, **keys):
        self._store = dict()
        self.update(dict(*args, **keys))  # use the free update to set keys

    def transform_key(self, key):
        """Abstract pass-thru key transformation,  override needed."""
        return key

    def transform_value(self, value):
        """Abstract pass-thru value transformation,  override as needed."""
        return value

    def __getitem__(self, key):
        return self._store[self.transform_key(key)]

    def __setitem__(self, key, value):
        self._store[self.transform_key(key)] = self.transform_value(value)

    def __delitem__(self, key):
        del self._store[self.transform_key(key)]

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def get(self, key, default=None):
        """Returns either value associated with `key` or transformed `default` value."""
        transformed_key = self.transform_key(key)
        value = self._store.get(transformed_key, default)
        return self.transform_value(value)
    
    def __repr__(self):
        """
        >>> TransformedDict([("this","THAT"), ("ANOTHER", "(ESCAPED)")])
        TransformedDict({'this': 'THAT', 'ANOTHER': '(ESCAPED)'})
        """
        return self.__class__.__name__ + "({})".format(repr({ key: self[key] for key in self }))

# =============================================================================

class LazyFileTree(collections.MutableMapping):
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

    special_values_set = ()   # Override in sub-classes as needed

    def __init__(self, selector, **keys):
        super(LazyFileTree, self).__init__()
        self._selector = selector
        self._loaded = {}
        self._keys = keys

    @classmethod
    def is_special_value(cls, value):
        """Returns True IFF `value` is a string in cls.special_values_set.
        Nominally this means the value has no recursive load operation, it's
        a literal.
        """
        return isinstance(value, str) and value in cls.special_values_set
        
    def __getitem__(self, name):
        if name in self._selector:
            try:
                self._loaded[name]
            except KeyError:
                if self.is_special_value(self._selector[name]):
                    self._loaded[name] = self._selector[name]
                else:
                    self._loaded[name] = self._loader(name, **self._keys)
            return self._loaded[name]
        else:
            raise KeyError(name)

    def __setitem__(self, name, value):
        self._loaded[name] = value   # disregards self._selector??

    def __delitem__(self, name):
        del self._loaded[name]
        del self._selector[name]

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
        
        >>> LazyFileTree({"this" : "OMIT", "that":"something.imap"}).normal_keys()
        ['that']

        NOTE:  Does not require full load.
        """
        return sorted([key for key in self.keys() if not self.is_special_value(self._selector[key])])

    def special_keys(self):
        """Each of these keys has a corresponding values which IS special.
        
        >>> LazyFileTree({"this" : "OMIT", "that":"something.imap"}).special_keys()
        ['this']

        NOTE:  Does not require full load.
        """
        return sorted([key for key in self.keys() if self.is_special_value(self._selector[key]) ]) 

    def values(self):
        """Return all the values of this LazyFileTree,  implicitly loading them all.

        NOTE:  REQUIRES FULL LOAD
        """
        return [self[name] for name in self.keys()]  

    def normal_values(self):
        """Normal values exclude the special values like N/A but can include exotic values like tuples or dicsts.
        
        >>> LazyFileTree({"this" : "N/A", "that":"something.imap"}).normal_values()
        ['something.imap']

        NOTE:  REQUIRES FULL LOAD
        """
        return [ self[key] for key in self.normal_keys() ]

    def special_values(self):
        """These are values which must be trapped and reformatted in the Mapping classes.
        
        >>> LazyFileTree({"this" : "N/A", "that":"something.imap"}).special_values()
        ['N/A']
        """
        return [ self[key] for key in self.special_keys() ]

    def items(self):
        """Return all the items of this LazyFileTree, implicitly loading all values.

        NOTE:  REQUIRES FULL LOAD
        """
        return self._items(self.keys())

    def normal_items(self):
        """
        >>> list(LazyFileTree({"this" : "N/A", "that":"something.imap"}).normal_items())
        [('that', 'something.imap')]
        """
        return self._items(self.normal_keys)

    def special_items(self):
        """
        >>> list(LazyFileTree({"this" : "N/A", "that":"something.imap"}).special_items())
        [('this', 'N/A')]
        """
        return self._items(self.special_keys())
    
    def _items(self, keys):
        """Constructs item list taken from self based on `keys`."""
        return [ (key, self[key]) for key in keys ]

