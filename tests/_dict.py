import unittest
from tie_py import tie_pyify
from tie_py import Action
from collections import defaultdict

class TestTiePyDicts(unittest.TestCase):
    '''
    runs tests on:

    '''
    callback = None

    def setUp(self):
        '''
        Called before every test function, must set static obj
        in the test function itself
        '''
        def callback(owner, path, value, action):
            path = list(path) 
            self.assertTrue(callback.owner is owner)
            
            #follows the path down
            v = owner
            while len(path) > 0:
                k = path.pop(0)
                if k in v:
                    v = v[k]
                else:
                    v = None
                    break

            if action == Action.SET:
                self.assertTrue(value is v)
            elif action == Action.DELETE:
                self.assertTrue(value is None)
                self.assertTrue(len(path) == 0)
            else:
                self.assertTrue(False)
    
            self.callback.count[action] += 1

        self.callback = callback
        self.callback.count = defaultdict(lambda: 0) #default, all actions have been called 0 times

    def assert_count(self, action, expected_count):
        '''
        asserts the count is correct for a given action
        '''
        self.assertEqual(self.callback.count[action], expected_count)

    def test_one_layered_pre_initialized(self):
        '''
        Testing one subscriber on a dictionary that's already
        been made before hand (no new keys)
        '''
        x = {"A": 1, "B": 2, "C": 3}
        x = tie_pyify(x)
        self.callback.owner = x
        s_id = x.subscribe(self.callback)

        x["A"] = 0
        self.assert_count(Action.SET, 1)

        x["B"] = 4
        self.assert_count(Action.SET, 2)

        x["C"] = -100
        self.assert_count(Action.SET, 3)

        x["A"] += 1
        self.assert_count(Action.SET, 4)

        #unsubscribing
        x.unsubscribe(s_id)
        x["B"] = 25
        self.assert_count(Action.SET, 4)

    def test_one_layered_initially_empty(self):
        '''
        Testing one subscriber on a dictionary that's empty
        and new items will be added to it
        '''
        x = tie_pyify({})
        self.callback.owner = x
        s_id = x.subscribe(self.callback)

        x["A"] = 0
        self.assert_count(Action.SET, 1)

        x["B"] = 4
        self.assert_count(Action.SET, 2)

        x["C"] = -100
        self.assert_count(Action.SET, 3)

        x["A"] += 1
        self.assert_count(Action.SET, 4)

        #unsubscribing
        x.unsubscribe(s_id)
        x["B"] = 25
        x["D"] = 98
        self.assert_count(Action.SET, 4)

    def test_one_layered_with_multiple_subscribers(self):
        '''
        Testing multiple subscribers on a dictionary
        '''
        x = tie_pyify({})
        self.callback.owner = x
        sub_count = 10 #must be larger than 3
        ids = [x.subscribe(self.callback) for _ in range(sub_count)]
        
        x["A"] = 0
        self.assert_count(Action.SET, sub_count)

        x["B"] = 4
        self.assert_count(Action.SET, 2*sub_count)

        x["C"] = -100
        self.assert_count(Action.SET, 3*sub_count)

        x["A"] += 1
        self.assert_count(Action.SET, 4*sub_count)

        #partially unsubscribing (removing 3 items)
        for i in range(sub_count - (sub_count - 3)):
            x.unsubscribe(ids.pop())

        x["B"] = 25
        self.assert_count(Action.SET, 4*sub_count + (sub_count - 3))

        #completely unsubscribing
        for s_id in ids:
            x.unsubscribe(s_id)

        x["D"] = 98
        self.assert_count(
            Action.SET,
            4*sub_count + (sub_count - 3))

    def test_one_layered_delete_operation(self):
        '''
        Testing delete operation to ensure the appropriate item gets published

        You shouldn't get a callback for deleting an item, though all of those items and it's
        children should be unsubscribed
        '''
        x = {"A": 1, "B": 2, "C": 3}
        x = tie_pyify(x)
        self.callback.owner = x
        s_id = x.subscribe(self.callback)

        del x["A"]
        self.assert_count(Action.DELETE, 1)
        self.assert_count(Action.SET, 0)
        self.assertTrue("A" not in x)

        del x["B"]
        self.assert_count(Action.DELETE, 2)
        self.assertTrue("B" not in x)

        #unsubscribing
        x.unsubscribe(s_id)

        del x["C"]
        self.assert_count(Action.DELETE, 2)
        self.assertTrue("C" not in x)

    def test_multi_layered_general(self):
        '''
        Testing a multilevel dictionary
        '''
        x = {"A": {"B": 1, "C": {"D": 10}, }, "E": {"F": 30}}
        x = tie_pyify(x)
        self.callback.owner = x
        s_id = x.subscribe(self.callback)

        x["A"]["B"] = 10
        self.assert_count(Action.SET, 1)
        x["A"]["C"]["D"] = 25
        self.assert_count(Action.SET, 2)

        m = x["A"]
        m["B"] = 35
        self.assertEqual(x["A"]["B"], 35)
        self.assert_count(Action.SET, 3)

        m["B"] = {"GREG": 28}
        self.assertEqual(x["A"]["B"], m["B"])
        self.assert_count(Action.SET, 4)

        m["B"]["GREG"] = 29
        self.assertEqual(x["A"]["B"]["GREG"], m["B"]["GREG"])
        self.assert_count(Action.SET, 5)

        g = m
        m = {}
        m["NO"] = "YES"
        self.assert_count(Action.SET, 5)

        g["NO"] = "YES"
        self.assert_count(Action.SET, 6)

        g["NO"] = "YES"
        self.assert_count(Action.SET, 6)

        x["A"]["NO"] = "Maybe"
        self.assert_count(Action.SET, 7)

        x["E"]["F"] = "39"
        self.assert_count(Action.SET, 8)

        x.unsubscribe(s_id)

        x["E"]["F"] = "12"
        self.assert_count(Action.SET, 8)

    def test_multi_layered_delete_operation(self):
        x = {"A": {"B": 1, "C": {"D": 10, "G": 32}, "J": 67}, "E": {"F": 30}}
        x = tie_pyify(x)
        self.callback.owner = x
        s_id = x.subscribe(self.callback)

        del x["A"]["B"]
        self.assert_count(Action.DELETE, 1)
        self.assertTrue("B" not in x["A"])

        x["A"]["C"]["D"] = 98
        self.assert_count(Action.SET, 1)

        b = x["A"]
        del x["A"]
        self.assert_count(Action.DELETE, 2)
        self.assertTrue("A" not in x)

        b["D"] = 97
        self.assert_count(Action.SET, 1)

        x.unsubscribe(s_id)

    def test_in_object_dict_moves(self):
        x = {"A": {"B": 1, "C": {"D": 10, "G": 32}, "J": 67}, "E": {"F": 30}}
        x = tie_pyify(x)
        self.callback.owner = x
        s_id = x.subscribe(self.callback)

        m = x["A"]["C"]
        x["H"] = 98
        self.assert_count(Action.SET, 1)

        x["H"] = m
        self.assert_count(Action.SET, 2)

        x["H"]["D"] = 99
        self.assert_count(Action.SET, 3)

        x["A"]["C"] = 45
        self.assert_count(Action.SET, 4)

        x["H"]["D"] = 73
        self.assert_count(Action.SET, 5)

        x["N"] = 42
        self.assert_count(Action.SET, 6)

	#challenge problem
        x["N"] = x
        self.assert_count(Action.SET, 7)
        x["N"]["N"]["N"]["N"] = 10
        self.assert_count(Action.SET, 8)

        #even more challenging
        x["A"]["B"] = x
        self.assert_count(Action.SET, 9)
        x["A"]["B"]["A"]["B"] = 29
        self.assert_count(Action.SET, 10)

        x.unsubscribe(s_id)

    def test_multiple_keys_to_same_object(self):
        x = {"A": {"B": 1, "C": {"D": 10, "G": 32}, "J": 67}, "E": {"F": 30}}
        x = tie_pyify(x)
        self.callback.owner = x
        s_id = x.subscribe(self.callback)

        m = x["A"]["C"]
        x["H"] = 98
        self.assert_count(Action.SET, 1)

        x["H"] = m
        self.assert_count(Action.SET, 2)
 
        x["H"]["D"] = 99
        self.assert_count(Action.SET, 3)

        del x["H"]
        x["A"]["C"]["D"] = 120
        self.assert_count(Action.SET, 4)
    
    def test_in_object_dict_moves_with_multiple_callbacks(self):
        x = {"A": {"B": 1, "C": {"D": 10, "G": 32}, "J": 67}, "E": {"F": 30}}
        x = tie_pyify(x)
        self.callback.owner = x
        s_id = x.subscribe(self.callback)

        def callback_1(owner, path, value, action):
            self.assertTrue(callback_1.owner is owner)
            v = owner
            path = list(path)
            while len(path) > 0:
                k = path.pop(0)
                if k in v:
                    v = v[k]
                else:
                    v = None
                    break
            if action == Action.SET:
                self.assertTrue(value is v)
            elif action == Action.DELETE:
                self.assertTrue(value is None)
                self.assertTrue(len(path) == 0)
            else:
                self.assertTrue(False)
            callback_1.count[action] += 1
        callback_1.count = defaultdict(lambda: 0)

        def assert_count_1(action, expected_count):
            self.assertEqual(callback_1.count[action], expected_count)


        m = {"Z": 1}
        m = tie_pyify(m)
        callback_1.owner = m
        m_id = m.subscribe(callback_1)
        m["L"] = {"T": 98}
        assert_count_1(Action.SET, 1)

        x["A"]["J"] = m
        self.assert_count(Action.SET, 1)
        assert_count_1(Action.SET, 1)
        self.assertTrue(x["A"]["J"] == m)

        m["L"]["T"] = 99
        self.assert_count(Action.SET, 2)
        assert_count_1(Action.SET, 2)
