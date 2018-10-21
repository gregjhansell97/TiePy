import tie_py._factory
from tie_py._base import TiePyBase

def tie_pyify(obj, callbacks={}):
    class_ = obj.__class__
    class TiePyList(TiePyBase, class_):
        '''
        assumes class_ inherits from dictionary, blends in TiePyBase to create a
        TiePyList. Monitoring catered to lists
        '''

        '''
        ABSTRACT INHERITED FUNCTIONS
        '''
        def _copy(self, obj):
            self.extend(obj)
        def append(self, v):
            print("appendingn")
            print(v)
            class_.append(self, v)
        def extend(self, l):
            print("extending:")
            print(l)
            class_.extend(self, l)
        def _get_keys(self):
            return self.keys()
        def _get_values(self):
            return self.values()
        def __iadd__(self, l):
            print("adding")
            print(l)
            class_.__iadd__(self, l)
        def __setitem__(self, index, value):
            print("setting")
            print(index)
            print(value)
            class_.__setitem__(self, index, value)

        # '''
        # MAGIC METHODS
        # '''
        # def __getitem__(self, key):
        #     '''
        #     wrapper for get item class, adds object from key to the _chain
        #
        #     Args:
        #         key: the key to the value
        #     '''
        #     item = class_.__getitem__(self, key)
        #     if issubclass(item.__class__, TiePyBase) and self not in item._chain:
        #         item._chain.append(self)
        #     return item
        #
        # def __setitem__(self, key, value):
        #     '''
        #     wrapper for set item class, invokes callbacks if needed
        #
        #     Args:
        #         key: the key to access the value
        #         value: the value being assigned
        #     '''
        #     #if key doesn't change then don't do anything
        #     if value not in self._chain and value is not self:
        #         if key in self:
        #             if self[key] is value:
        #                 return value
        #
        #         callbacks = {} #copy of callbacks generated for child class
        #         for id_ in self._callbacks.keys():
        #             owner, keys, cb = self._callbacks[id_]
        #             callbacks[id_] = (owner, keys + [key], cb)
        #         value = tie_py._factory.tie_pyify(
        #             value,
        #             callbacks = callbacks)
        #     r = class_.__setitem__(
        #         self,
        #         key,
        #         value)
        #     self._run_callbacks(value, key)
        #
        #     return r
        #
        # def __delitem__(self, key):
        #     '''
        #     wrapper for the delete items, unsubscribes common ids
        #     from it
        #
        #     Args:
        #         key: the key that is being deleted
        #     '''
        #     if issubclass(self[key].__class__, TiePyBase):
        #         ids = list(self._callbacks.keys())
        #         self[key]._unsubscribe(ids)
        #
        #     return class_.__delitem__(self, key)

    return TiePyList(obj, callbacks=callbacks)