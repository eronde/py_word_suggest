import re
import pytest
from py_word_suggest.Selector import *

@pytest.fixture(scope='session')
def bigrams():
    b = {'I':[['am',1],['want', 10], ['like', 5]]}
    bigrams = Selector(b)
    return bigrams

@pytest.mark.parametrize("testInput,sortTypeOutput",
            [
            (None,['am','want','like']),
            (True,['want','like','am']),
            (False,['am','like','want'])
            ]
        )

def test_genSuggestedWords(bigrams, testInput, sortTypeOutput):
    """Selector: Generate suggested words object"""
    gen = bigrams.gen_suggestWord('I',sort=testInput)
    for testValue, generatedValue in zip(gen, sortTypeOutput):
        assert testValue == generatedValue

@pytest.mark.parametrize("testInput,sortTypeOutput",
            [
            (None,['am','want','like']),
            (True,['want','like','am']),
            (False,['am','like','want'])
            ]
        )
def test_setSuggestedWords(bigrams, testInput, sortTypeOutput):
    """Selector: Set list of suggested word to object"""
    bigrams.set_suggestedWords('I',sort=testInput)
    assert list(bigrams._suggestWords) == sortTypeOutput
    assert bigrams._suggestWords == None

def test_setSelectedBigram(bigrams):
    """Selector: Set Suggested bigram (values of basekey) to object"""
    assert bigrams._selectedBigram == None
    bigramValues = [['am',1],['want', 10], ['like', 5]]   
    bigrams.set_bigram('I')
    assert bigrams._selectedBigram == bigramValues
    with pytest.raises(SelectorNoBaseKeyFoundError) as e:
        bigrams.set_bigram('NoBaseKey==')
    assert str(e.value) == "Error: key, \'NoBaseKey==\' does not exists." 

def test_setSelectedBaseKey(bigrams):
    """Selector: Set Suggested basekey (key) to object"""
    assert bigrams._selectedBaseKey == None
    basekey='I'
    bigrams.set_baseKey(basekey)
    assert bigrams._selectedBaseKey == basekey

    with pytest.raises(SelectorNoBaseKeyFoundError) as e:
        bigrams.set_baseKey('NoBaseKey==')
    assert str(e.value) == "Error: key, \'NoBaseKey==\' does not exists." 

def test_checkKeyExist(bigrams):
    """Selector: Check if base 'word' key exists or not exists
    :returns: TODO

        """
    exist = bigrams.existBaseKey('I')
    assert exist == True
    notexist = bigrams.existBaseKey('How')
    assert notexist == False

def test_setBigramToObject(bigrams):
    """Selector: Set bigram values to bigram object
    :returns: TODO
    """
    assert bigrams._selectedBigram == None
    bigrams.set_bigram('I')
    bigramValues = [['am',1],['want', 10], ['like', 5]]
    assert bigrams._selectedBigram == bigramValues
    
    with pytest.raises(SelectorNoBaseKeyFoundError) as e:
        bigrams.set_bigram('NoKey')
    assert str(e.value) == "Error: key, \'NoKey\' does not exists." 
    assert bigrams._selectedBigram == None

@pytest.mark.parametrize("testInput,expectedOutput,errorState",
            [
                ('I', ('I',), False),
                ('love', ('I','love'), False),
                ('Python', ('I','love','Python'), False),
                (9, "Error: lookupEntree, '9' needs to be a string.", True),
                ('String with space', "Error: lookupEntree, 'String with space' needs to be a string.", True)
                ])
def test_addLookup(bigrams, testInput, expectedOutput, errorState):
    """Selector: Get bigrams of what the user has lookup
    :returns: TODO
        """
    if  errorState is False:
        bigrams.addBigramLookup(testInput)
        assert bigrams._lookups == expectedOutput
    else:
        with pytest.raises(SelectorNoBaseKeyFoundError) as e:
            bigrams.addBigramLookup(testInput)
            assert str(e.value) == expectedOutput
# with pytest.raises(SelectorNoBaseKeyFoundError) as e:
    #     bigrams.addBigramLookup       bigrams.set_bigram('NoKey')
    # assert str(e.value) == "Error: key, \'NoKey\' does not exists." 
