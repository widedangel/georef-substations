# coding: utf-8

# In[1]:


## Copyright 2015 Tom Brown (FIAS, brown@fias.uni-frankfurt.de)

## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 3 of the
## License, or (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.



# make the code as Python 3 compatible as possible
from __future__ import print_function, division



import pandas as pd

import numpy as np

import os


get_ipython().magic(u'matplotlib inline')

import matplotlib.pyplot as plt

from mpl_toolkits.basemap import Basemap




# In[2]:

entsoe_folder_name = "entsoe-data/"
matched_folder_name = "matched-data/"
osm_folder_name = "osm-data/"


# In[3]:

ucte = pd.read_excel(entsoe_folder_name + 'RGCE_dataset_2030_Level1.xlsx', sheet=0)

ucte.rename(columns={"Node  Name" : "name", " Area Name" : "country_code"},inplace=True)

print(ucte.columns)


# In[4]:

matched = pd.read_csv(matched_folder_name + "ucte-nodes.csv",encoding="utf8",index_col=0)


# In[5]:

ucte = pd.concat([ucte,matched],axis=1)
print(ucte)


# In[6]:

ucte_lines = pd.read_excel(entsoe_folder_name + 'RGCE_dataset_2030_Level1.xlsx', sheetname="Lines")
ucte_lines.rename(columns={"From Node  Name and voltage" : "from_node", "To Node  Name and voltage" : "to_node"},inplace=True)


ucte_lines.columns


# In[8]:

#these are voltages found in the model

voltages = [220,400,380,232,225,500,320,750]

for name in ucte_lines["from_node"]:
    if int(float(name[-6:])) not in voltages:
        print(name[-6:])


# In[9]:


#match the line to/froms to the nodes table

ucte_lines["from_id"] = np.nan
ucte_lines["to_id"] = np.nan

for item in ["from","to"]:

    for k,name in ucte_lines[item + "_node"].iteritems():
        parsed = name[:-6].strip()

        found = ucte[ucte["name"] == parsed]

        if len(found) > 0:
            ucte_lines.loc[k,item+"_id"] = found.index[0]
        else:
            print(parsed,"not found")


# In[194]:

osm = pd.read_csv(osm_folder_name + "ways_as_substations-151203-1503-with_countries.csv",index_col=0,encoding="utf8")

osm.set_index('way_id',inplace=True)

osm["osm_name"] = osm["name"]

osm["osm_way_id"] = osm.index
osm.columns


# In[195]:

ucte = pd.merge(ucte,osm.loc[:,["osm_way_id","ref","operator","longitude","latitude","osm_name"]],how="left",on="osm_way_id")
print(ucte.columns,ucte.shape)


# In[196]:

#country-specific parsing functions

def parse_at(name):
    if name[:2] == "O-":
        name = name[2:]
    if "/" in name:
        name = name[:name.index("/")]
    #remove numbers
    for i in range(10):
        name = name.replace(str(i),"")
    return name

parsing = {"AT": parse_at}


# In[197]:

#make a suggestion for OSM way match, based on parsed_name

def suggest(parsed_name,country_code):
    osm_c = osm[osm["country_code"] == country_code]
    names = osm_c["name"]

    n_matches = names[names.apply(lambda s: parsed_name.lower() in s.lower())]

    refs = osm_c["ref"]

    r_matches = refs[refs.apply(lambda s: parsed_name.lower() in str(s).lower())]

    return pd.concat([osm_c.loc[n_matches.index],osm_c.loc[r_matches.index]])


# In[198]:

#go through all of a country's nodes and make suggestions

country_code = "AT"
for name in ucte[ucte["country_code"] == country_code]["name"]:
    parsed_name = parsing[country_code](name)
    print("\n"*3)
    print(name,parsed_name)
    suggestions = suggest(parsed_name,country_code)
    print(suggestions[["name","ref","operator","latitude","longitude"]])


# In[199]:

#look at individual tricky ones

parsed_name = u"südb"
country_code = "AT"
answer = suggest(parsed_name,country_code)

print(answer[["name","ref","operator","latitude","longitude"]])


# In[200]:


#find nodes connect to node

def connected_to(tso_name):

    f = lambda n: tso_name in n

    return ucte_lines[ucte_lines.from_node.map(f) | ucte_lines.to_node.map(f)]


# In[201]:

tso_name = "O-DUERN"

connected_to(tso_name)


# In[248]:

fig,ax = plt.subplots(1,1)

fig.set_size_inches((7,7))

x1 = 5
x2 = 20
y1 = 45
y2 = 55


bmap = Basemap(resolution='i',projection='merc',llcrnrlat=y1,urcrnrlat=y2,llcrnrlon=x1,urcrnrlon=x2,ax=ax)

bmap.drawcountries()
bmap.drawcoastlines()

selection = ucte[ucte["longitude"].notnull()]

for i,row in ucte_lines.iterrows():

    if pd.isnull(row["from_id"]) or row["from_id"] not in selection.index or pd.isnull(row["to_id"]) or row["to_id"] not in selection.index:
        continue


    lon = [selection["longitude"][row[item+"_id"]] for item in ["from","to"]]
    lat = [selection["latitude"][row[item+"_id"]] for item in ["from","to"]]

    x,y = bmap(lon,lat)

    color = "g"
    alpha = 0.7
    width =  1.2

    bmap.plot(x,y,color,alpha=alpha,linewidth=width)


x,y = bmap(selection["longitude"].values,selection["latitude"].values)

bmap.scatter(x,y,color="r",s=20)


fig.tight_layout()


file_name = "matched-data/europe.pdf"

print("file saved to",file_name)

fig.savefig(file_name)

plt.show()



# In[ ]:




# In[3]:

def preprocess(x):
    x = unicode(x)
    try:
        x = x[x.index('-')+1:]
    except ValueError:
        pass

    try:
        x = x[:x.index('/')]
    except ValueError:
        pass

    try:
        x = x[:x.index('_')]
    except ValueError:
        pass
    try:
        x = x[:x.index('-')]
    except ValueError:
        pass
    return x


# In[ ]:




# In[80]:

de_e = ucte[ucte["country_code"] == "DE"]["name"]

de_e = de_e.map(preprocess)

de_o = osm[osm["country_code"] == "DE"]

print de_e.shape,de_o.shape


# In[80]:

de_o_not_null_ref = de_o[de_o["ref"].notnull()]
count = 0
for i,r in de_o_not_null_ref.iterrows():
    ref = r["ref"]
    #chuck out integers
    try:
        int(ref)
        continue
    except:
        pass

    matches = [s for s in de_e if s[:len(ref)] == ref]
    if len(matches) > 0:
        print ref,matches,r["name"]
        count +=1
print count


# In[75]:

de_e[de_e.apply(lambda s: "CONN" in s)]


# In[ ]:
