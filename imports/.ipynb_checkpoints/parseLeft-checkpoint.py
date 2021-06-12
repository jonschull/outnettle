#!/usr/bin/env python
# coding: utf-8

# In[1]:


graphString="""id a
	label a multi word label
	linkto b
    linkto c
    linkto d
id b
	linkto
	label b
options 
    nodes
		color pink
		color red
		color border red
		borderWidth 10
"""

graphString="""id a
	linkto b c d
"""


# In[2]:


#https://github.com/clarketm/mergedeep/tree/master/mergedeep
from collections import Counter
from collections.abc import Mapping
from copy import deepcopy
from enum import Enum
from functools import reduce, partial
from typing import MutableMapping



class Strategy(Enum):
    # Replace `destination` item with one from `source` (default).
    REPLACE = 0
    # Combine `list`, `tuple`, `set`, or `Counter` types into one collection.
    ADDITIVE = 1
    # Alias to: `TYPESAFE_REPLACE`
    TYPESAFE = 2
    # Raise `TypeError` when `destination` and `source` types differ. Otherwise, perform a `REPLACE` merge.
    TYPESAFE_REPLACE = 3
    # Raise `TypeError` when `destination` and `source` types differ. Otherwise, perform a `ADDITIVE` merge.
    TYPESAFE_ADDITIVE = 4


def _handle_merge_replace(destination, source, key):
    if isinstance(destination[key], Counter) and isinstance(source[key], Counter):
        # Merge both destination and source `Counter` as if they were a standard dict.
        _deepmerge(destination[key], source[key])
    else:
        # If a key exists in both objects and the values are `different`, the value from the `source` object will be used.
        destination[key] = deepcopy(source[key])


def _handle_merge_additive(destination, source, key):
    # Values are combined into one long collection.
    if isinstance(destination[key], list) and isinstance(source[key], list):
        # Extend destination if both destination and source are `list` type.
        destination[key].extend(deepcopy(source[key]))
    elif isinstance(destination[key], set) and isinstance(source[key], set):
        # Update destination if both destination and source are `set` type.
        destination[key].update(deepcopy(source[key]))
    elif isinstance(destination[key], tuple) and isinstance(source[key], tuple):
        # Update destination if both destination and source are `tuple` type.
        destination[key] = destination[key] + deepcopy(source[key])
    elif isinstance(destination[key], Counter) and isinstance(source[key], Counter):
        # Update destination if both destination and source are `Counter` type.
        destination[key].update(deepcopy(source[key]))
    else:
        _handle_merge[Strategy.REPLACE](destination, source, key)


def _handle_merge_typesafe(destination, source, key, strategy):
    # Raise a TypeError if the destination and source types differ.
    if type(destination[key]) is not type(source[key]):
        raise TypeError(
            f'destination type: {type(destination[key])} differs from source type: {type(source[key])} for key: "{key}"'
        )
    else:
        _handle_merge[strategy](destination, source, key)


_handle_merge = {
    Strategy.REPLACE: _handle_merge_replace,
    Strategy.ADDITIVE: _handle_merge_additive,
    Strategy.TYPESAFE: partial(_handle_merge_typesafe, strategy=Strategy.REPLACE),
    Strategy.TYPESAFE_REPLACE: partial(_handle_merge_typesafe, strategy=Strategy.REPLACE),
    Strategy.TYPESAFE_ADDITIVE: partial(_handle_merge_typesafe, strategy=Strategy.ADDITIVE),
}


def _is_recursive_merge(a, b):
    both_mapping = isinstance(a, Mapping) and isinstance(b, Mapping)
    both_counter = isinstance(a, Counter) and isinstance(b, Counter)
    return both_mapping and not both_counter


def _deepmerge(dst, src, strategy=Strategy.REPLACE):
    for key in src:
        if key in dst:
            if _is_recursive_merge(dst[key], src[key]):
                # If the key for both `dst` and `src` are both Mapping types (e.g. dict), then recurse.
                _deepmerge(dst[key], src[key], strategy)
            elif dst[key] is src[key]:
                # If a key exists in both objects and the values are `same`, the value from the `dst` object will be used.
                pass
            else:
                _handle_merge.get(strategy)(dst, src, key)
        else:
            # If the key exists only in `src`, the value from the `src` object will be used.
            dst[key] = deepcopy(src[key])
    return dst


def merge(destination: MutableMapping, *sources: Mapping, strategy: Strategy = Strategy.REPLACE) -> MutableMapping:
    """
    A deep merge function for 🐍.

    :param destination: The destination mapping.
    :param sources: The source mappings.
    :param strategy: The merge strategy.
    :return:
    """
    return reduce(partial(_deepmerge, strategy=strategy), sources, destination)

def split(data, value=2):
    """recursively turn a set of words into a nested dict
    https://stackoverflow.com/questions/52349884/create-a-nested-dictionary-using-recursion-python
    """
    if data:
        head, *tail = data  # This is a nicer way of doing head, tail = data[0], data[1:]
        return {head: split(tail,value)}
    else:
        return value  
        # this returns the value to the previous split() 
        #    which sets it in the line above by calling itself and returns the datastructure
        #    now that data is None, the complete dataStructure is returned back up through call stack
        #    to the original call.  
        # It's way over my head!
    


def fixV(s):
    """
    deal with non-string values
    """
    if s in ['True', 'true']: return True
    if s in ['False', 'false']: return False
    try: # to convert to a number
        return(int(s))
    except:
        return s #then just return as is

def makeOpt(line = 'nodes color background red'):
    """
    prepare string for split
    """
    words = line.split()
    value = fixV(words.pop())
        
    return split(words, value)


TESTING=False
if TESTING:
    d1 = makeOpt('nodes color background red')
    d2 = makeOpt('nodes color border green')
    d3 = makeOpt('nodes shape box')
    options = merge(d1,d2,d3)
    print(options)

    options = merge(options, makeOpt('nodes borderWidth 12'))

    print(options)


# In[ ]:





# In[ ]:





# In[3]:


graphString="""id a
	label a multi word label /more than one line
	linkto  b
id b
	label b
defaults edges
		color pink
		color red
		color border red
		borderWidth 10
defaults nodes
		color pink
		color red
		color border red
		borderWidth 10"""

#note: use of defaults 
#note: no blank linktos


# In[4]:


import string
def getChunks(graphString=graphString):
    """
    break graphString at non-indented lines
    """
    #put break signal in non-indented lines
    lines=graphString.split('\n') 
    for i,line in enumerate(lines):
        if line.strip():
            if line[0] in string.ascii_letters: 
                lines[i] = '@@' + line

                
    #rejoin them 
    withBreaks = '\n'.join(lines)
    splitAtBreaks =  withBreaks.split('@@')

    return [line for line in splitAtBreaks if line.strip()] #return non-null ines

getChunks()


# In[5]:


print(getChunks()[0])


# In[6]:


def classify(chunks):
    nodeLines=[]
    optionLines=[]
    for chunk in chunks:
        if chunk.startswith('id'):
            nodeLines.append(chunk)
        else:
            optionLines.append(chunk)   

    return nodeLines, optionLines

nodeLines, optionLines = classify(getChunks())
nodeLines, optionLines


# In[7]:


def nodesFromNodeLines(nodeLines):
    print('nodeLines in:', nodeLines)
    nodes=[]
    for nodeLine in nodeLines: 
        node = {}
        for phrase in nodeLine.split('\n'):
            phraseStripped = phrase.strip()
            if phraseStripped:
                if phraseStripped.startswith('linkto'):
                    node['linkto'] = phrase.replace('linkto','').strip() #linkto a b c should not be makeOpted
                elif phraseStripped.startswith('label '):
                    node['label']=phraseStripped.split('label ',1)[1].replace('/','\n')
                else:
                    try:
                        node = merge(node, makeOpt(phrase))
                    except:
                        print('?'+phrase)
        nodes.append(node)
    return nodes # finito!

nodes = nodesFromNodeLines(nodeLines)
nodes


# In[8]:


nodesFromNodeLines(['id Welcome\n\t label test'])


# In[9]:


def optionsFromOptionLines(optionLines):
    options = {}
    for optionLine in optionLines:
        optionSet={}
        phrases = optionLine.split('\n')
        if len(phrases[0].split(' '))<2: 
            return {}
        kind = phrases.pop(0).split(' ')[1].strip() #presumes two words; keep 'edge' discard 'default' 

        for phrase in phrases:
            if len(phrase.split(' '))>1: #will fail
                try:
                    optionSet = merge(optionSet, (makeOpt(phrase)))
                except:
                    print('.'+phrase,end='')
                    return {}
                    

        options[kind] = optionSet
    return options
optionsFromOptionLines(optionLines)


# In[10]:


def nodesEdgesOptions(graphString=graphString):
    
    chunks = getChunks(graphString)
    nodeLines, optionLines = classify(chunks)
    
    nodes    = nodesFromNodeLines( nodeLines )
    options  = optionsFromOptionLines( optionLines)

    edges = []
    for node in nodes:
        if 'linkto' in node.keys():
            for linkto in node['linkto'].split(' '):
                edges.append( {'from':node['id'], 'to':linkto} )

    return nodes, edges, options


nodesEdgesOptions()


# In[11]:


import subprocess
if subprocess.run.__doc__:
    cmd = 'jupyter nbconvert --to python parseLeft.ipynb'
    subprocess.run(cmd.split(' '))


# In[ ]:





# In[ ]:




