import unittest
import re
import fakeredis
# from ..util.Selector_redis import Selector_redis, SelectorRedisNoBaseKeyFoundError,SelectorRedisNoSuggestWordFoundError, SelectorRedisError, SelectorRedisEmptyValue

from py_word_suggest.Selector_redis import *


class Selector_redisTest(unittest.TestCase):
    """Docstring for Selector_redisTest. """

    def setUp(self):
        """ Selector_redis:Set up the fakeredis
        """
        self.redis = fakeredis.FakeRedis()
        self.redis.zadd("Hello",  "Alice", 1)
        self.redis.zadd("Hello", "Bob", 10)

    def tearDown(self):
        self.redis.flushall()

    def test_fetchSuggestedWordsWithScores(self):
        """Selector_redis: Fetch all suggested words of words 'Hello' with scores
        :returns: TODO
        """
        obj = Selector_redis(self.redis)
        x = obj.gen_fetchWords('Hello', withscore=True)
        match = [('Bob'.encode(), 10), ('Alice'.encode(), 1)]
        self.assertListEqual(list(x), match, "Should be [(b'Bob', 10),(b'Alice', 1)]")

    def test_fetchSuggestedWordsWithoutScores(self):
        """Selector_redis: Fetch all suggested words of words 'Hello' without scores
        :returns: TODO
        """
        obj = Selector_redis(self.redis)
        x = obj.gen_fetchWords('Hello')
        match = ['Bob'.encode(), 'Alice'.encode()]
        self.assertListEqual(list(x), match, "Should be ['Bob','Alice']")

    def test_getSuggestedWords(self):
        """Selector_redis: Get all suggested words of words 'Hello'
        :returns: TODO
        """
        obj = Selector_redis(self.redis)
        x = self.redis.zrevrange('Hello', 0, -1)
        match = ['Bob', 'Alice']
        self.assertListEqual(list(obj.gen_suggestWord(*x)), match, "Should be ['Bob','Alice']")

    def test_getInvalidKey(self):
        """Selector_redis: Fetch invalid base key[A]
        :returns: TODO
        """
        obj = Selector_redis(self.redis)
        with self.assertRaises(SelectorRedisNoBaseKeyFoundError) as e:
            obj.gen_fetchWords('NoBaseKey')
        error = str(e.exception)
        self.assertTrue("Error: key \', \'NoBaseKey\', \' does not exists." in error)

    def test_addNewsuggestedWord(self):
        """Selector_redis: Add new suggested word to 'Hello' key
        :returns: TODO

        """
        obj = Selector_redis(self.redis)
        match = ['Bob', 'Alice']
        x = self.redis.zrevrange('Hello', 0, -1)
        self.assertListEqual(list(obj.gen_suggestWord(*x)), match, "Should be ['Bob','Alice']")
        match = ['Bob', 'Max', 'Alice']
        obj.addNewSuggestWord('Hello', 'Max')
        x = self.redis.zrevrange('Hello', 0, -1)
        self.assertListEqual(list(obj.gen_suggestWord(*x)), match, "Should be ['Bob','Max','Alice']")

    def test_removeSuggestedWord(self):
        """Selector_redis: Remove suggested word from 'Hello' key
        :returns: TODO

        """
        obj = Selector_redis(self.redis)
        match = ['Bob']
        obj.removeSuggestWord('Hello', 'Alice')
        x = self.redis.zrevrange('Hello', 0, -1)
        self.assertListEqual(list(obj.gen_suggestWord(*x)), match, "Should be ['Alice']")

    def test_isAvailableConnection(self):
        """Selector_redis: Check if redis server is available
        :returns: TODO
        """
        obj = Selector_redis(self.redis)
        self.assertTrue(obj.is_redis_available())
        with self.assertRaises(Exception):
            o = None
            o.is_redis_available()


    def test_raiseNotConnection(self):
        """Selector_redis: Raise error if redis server is not connected
        :returns: TODO
        """
        with self.assertRaises(Exception):
            obj = Selector_redis()
        with self.assertRaises(Exception):
            obj = Selector_redis(foo)

    def test_checkKeyExist(self):
        """Selector_redis: Check if base 'word' key exists or not exists
        :returns: TODO

        """
        obj = Selector_redis(self.redis)
        exist = obj.existBaseKey('Hello')
        self.assertIs(exist, True)
        # notexist = obj.existBaseKey('How')
        # self.assertIs(notexist, False)

    def test_increaseScoreOfSuggestedWord(self):
        """Selector_redis: Increase score of suggested word
        :returns: TODO

        """
        obj = Selector_redis(self.redis)
        obj.increaseScoreSuggestedWord('Hello', 'Alice')
        scores = obj.gen_fetchWords('Hello', withscore=True)
        match = [('Bob'.encode(), 10),  ('Alice'.encode(), 2)]
        self.assertListEqual(list(scores), match, "Should be [(b'Bob', 10),(b'Alice', 2)]")
        # Increase by 4
        obj.increaseScoreSuggestedWord('Hello', 'Alice', 4)
        scores = obj.gen_fetchWords('Hello', withscore=True)
        match = [('Bob'.encode(), 10),  ('Alice'.encode(), 6)]
        self.assertListEqual(list(scores), match, "Should be [(b'Bob', 10),(b'Alice', 6)]")
        # Increase by -7
        obj.increaseScoreSuggestedWord('Hello', 'Alice', -7)
        scores = obj.gen_fetchWords('Hello', withscore=True)
        match = [('Bob'.encode(), 10),  ('Alice'.encode(), -1)]
        self.assertListEqual(list(scores), match, "Should be [(b'Bob', 10),(b'Alice', -1)]")
        # Increase by string
        with self.assertRaises(TypeError) as e:
            obj.increaseScoreSuggestedWord('Hello', 'Alice', 'l')
        # Increase non existing key
        with self.assertRaises(SelectorRedisNoBaseKeyFoundError) as e:
            obj.increaseScoreSuggestedWord('Hel', 'Alice', 4)
        error = str(e.exception)
        pat = "Error: key 'Hel' does not exists."
        self.assertTrue(pat in error, "'{e} ' should be 'Error: key 'Hel' does not exists.'".format(e=pat))
        # Increase non existing suggested word
        with self.assertRaises(SelectorRedisNoSuggestWordFoundError) as e:
            obj.increaseScoreSuggestedWord('Hello', 'bobby',  4)
        error = str(e.exception)
        pat = "Error: suggested word: 'bobby' does not exists with basekey 'Hello'." 
        self.assertTrue(pat in error, "'{e} ' should be: 'Error: suggested word: 'bobbypat' does not exists with basekey 'Hello.'".format(e=pat))
        # Increase non existing suggested word
        with self.assertRaises(SelectorRedisEmptyValue) as e:
            obj.increaseScoreSuggestedWord('Hello', '', 4)
        error = str(e.exception)
        pat = "^Error in 'increaseScoreSuggestedWord': One of the given arguments .*\, 'Hello', '', 4\)' are empty\.$"
        regex = re.search(pat, error)
        assert regex is not None, "'{e} ' should contain:Error in 'increaseScoreSuggestedWord': One of the given arguments , 'Hello', '', 4\)' are empty .format(e=pat)"
        # Increase suggested word invalid score
        with self.assertRaises(TypeError) as e:
            obj.increaseScoreSuggestedWord('Hello', 'Bob', 'nonvalid')
        error = str(e.exception)
        pat = "^Error: Score 'nonvalid' needs to be an int or a float.$"
        regex = re.search(pat, error)
        assert regex is not None,"'{e}' should contain: Error: Score 'nonvalid' needs to be an int or a float.".format(e=pat)

    def test_checkSuggestedWordExists(self):
        """Selector_redis: Check if suggested word exists or not exists
        :returns: TODO

        """
        obj = Selector_redis(self.redis)
        # list
        data = ['test', 'bla']
        self.assertTrue(obj.containing(data, 'test'))
        # sets$
        self.assertTrue(obj.containing(data, 'test'))
        # Not containing
        self.assertFalse(obj.containing(data, 'hello'))
        # generator
        fetchdata = obj.gen_fetchWords('Hello')
        data = set(obj.gen_suggestWord(*fetchdata))
        self.assertTrue(obj.containing(data, 'Bob'))
        self.assertFalse(obj.containing(data, 'Bobby'))

if __name__ == '__main__':
    unittest.main()
