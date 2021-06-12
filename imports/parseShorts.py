#!/usr/bin/env python
# coding: utf-8

# In[1]:


shortStrings = """test
	one 
	two
"""


# In[2]:


def newNode(line):
    return dict( id=None,
                    depth = len(line) - len(line.lstrip()),
                    linkto='',
                    parent=None,
                    parentid=None,
                    label=None,
                    raw=line)


# In[3]:


IDs = set([str(i) for i in range(1000)][1:])

def assignID(preNode,line,lineID, addenda, assignedIDs):
        if addenda: #CURRENTLY MUST BE MANUALLY INSERTED /ID ZERO
            IDfromAddenda = addenda.split('ID ')
            if len(IDfromAddenda)>1:
                lineID = IDfromAddenda[1].split(' ')[0]
        else:
            if lineID==-1 or (lineID in assignedIDs):
                lineID = list(IDs - assignedIDs)[0]
        # use lineID
        preNode['id']= str(lineID)
        assignedIDs.add(lineID)
        return preNode, assignedIDs


# In[4]:



def makePreNodes(shortStrings=shortStrings):
    assignedIDs = set()

    #########
    #shortStrings = editor.getValue()
    #########x
    lines=shortStrings.split('\n')
    #print('lines', lines)

    preNodes = [newNode(line) for line in lines if line.strip()]
    # compute parents
    for i in range(len(preNodes)):
        my = preNodes[i]
        if i>0: #first guy has no parent
            for j in range(i+1):
                if preNodes[i-j]['depth'] < my['depth']: #found parent
                    preNodes[i]['parent'] = preNodes[i-j]  #parents
                    break # We now know our parent

    for i,preNode in enumerate(preNodes):
        line=preNode['raw']

        #### extract components for future use.
        if '/' in line: #split off addenda
            line, addenda = line[:line.find('/')], line[line.find('/')+1 :]
            addenda=addenda.strip()
        else:
            addenda = ''

        if ':' in line: #split off linktos
            line, linkto = line[:line.find(':')], line[line.find(':')+1 :]
            #linkto=linkto.split()
        else:
            linkto=''

        words = line.strip().split(' ')
        if len(words) == 1: #one word Labels become IDs
            lineID = words[0].strip()
        else:
            lineID = -1
            #preNode['ADDENDA']= '/ID ' + lineID

        #### use line and components carefully
        preNode['label']=line.strip()

        if preNode['parent']:  #since parent precedes child, parent ID is available for use
            preNode['parentID'] = preNode['parent']['id']

        ####assign ID and update assignedIDs
        preNode, assignedIDs = assignID(preNode,line,lineID, addenda, assignedIDs)

        #Linktos #aggregate linktos for when we get out of the loop
        if preNode['parent']:
            preNode['parent']['linkto'] += ' ' + preNode['id'] #works
        if linkto:
            preNode['linkto'] += ' ' + linkto
        #preNode['addenda'] = niceRep(preNode, goodKeys='id label linkto title borderWidth'.split(' '))

    linktos=set() #collect all the linktos for all the nodes
    for preNode in preNodes:
        for target in preNode['linkto'].split(' '):
            linktos.add(target)

    #collect all explicit IDs for all the  nodes
    namedNodes=set([node['id']for node in preNodes])

    #create nodes that were mentioned in linktos but not explicitly named
    for ID in linktos-namedNodes: #the linktos that need to be named
        if ID:
            newPreNode = newNode(ID)
            newPreNode['id']=ID
            newPreNode['label']= ID
            preNodes.append(newPreNode)
                         
    return preNodes

makePreNodes()


# In[5]:


def niceRep(preNode, goodKeys = 'id label linkto parent addenda'.split(' ')):
    ret=[]
    for k,v in preNode.items():
        if k in goodKeys: #this is needed for filtering preNodes
            if type(v)==type({}):
                for k2,v in v.items():
                    ret.append(f'{k} {k2} {v}')
            else:
                ret.append(f'{k} {v}')
    return '/' + '  /'.join(ret)


# In[6]:


"""
id a
	label a
	linkto  b
	color
	('border', 'red') ('background', 'lime')
id b
	label b"""


# In[7]:


def niceReps(mergedNodes):
    newLines=[]
    for mergedNode in mergedNodes:
        newLine = niceRep(mergedNode, goodKeys='id label linkto title color borderWidth shape font background x y'.split(' '))
        newLine= newLine.replace('/','\n')
        newLines.append(newLine)
    return newLines


# In[8]:


def splice(preNodes, priorNodes=[]):
    """interweave nodes and preNodes before sending to fillLeft"""
    newNodes=preNodes
    mergedNodes=[]

    oldNodes = {} #a dict of diagrammed nodes, indexed by ID, but now with upper case keys
    for _ in  priorNodes:
        oldNodes[_['id']]= _

    if oldNodes:
        for newNode in newNodes:
            if newNode['id'] in oldNodes: #merge new shorthand values into oldNode
                mergedNode = oldNodes[newNode['id']] | newNode  #MERGE
                mergedNodes.append(mergedNode)
            else:
                mergedNodes.append(newNode)
    if not oldNodes:
        mergedNodes = oldNodes

    newLines = niceReps(mergedNodes)
    return newLines


# In[ ]:





# In[9]:


import subprocess
if subprocess.run.__doc__:
    cmd = 'jupyter nbconvert --to python parseShorts.ipynb'
    subprocess.run(cmd.split(' '))


# In[ ]:




