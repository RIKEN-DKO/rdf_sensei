# %%
%load_ext autoreload
%autoreload 2   

# %%
import os
os.chdir('../synthetiql')
# from sparql.EndpointRiken import Endpoint
from Endpoint import Endpoint
from normalizer import Normalizer 
from configs import ENDPOINT_T_BOX_URL
from vector_index import TBoxIndex,ABoxIndex
from parsers import parser_sentence

# %%
#Normalizer
normalizer = Normalizer()

#T-Box
endpoint_t_box = Endpoint(ENDPOINT_T_BOX_URL)
t_box_index = TBoxIndex(endpoint_t_box,normalizer)

#A-Box
# endpoint_a_box = endpoint_t_box
# a_box_index = ABoxIndex(endpoint_a_box,normalizer)



# %%
# sentence = "Give all phenotypes with abnormal locomotor behavior "
# sentence = "Give me some mouse phenotypes"
sentence = "Give me gene expression of mouse mus musculus"
# sentence = "Give info about mouse mus musculus"
res_tbox = parser_sentence(sentence, t_box_index, endpoint_t_box)
# print(res_tbox)
#ABOX bring more results
# res_abox = parser_sentence(sentence, a_box_index, endpoint_a_box)
# print(res_abox)
# %%
for res in res_tbox:
    # print(res['label'])
    # print(res['content']['?term'])
    # print(res['score'])
    print(res)
    print('---')
#%%
print(res_tbox)

# %%
list_questions = [
    "Which are the human proteins associated with cancer?",
"Give me the list of strains associated to the Escherichia coli taxon and their name",
"Retrieve all proteins involved in pathways involving glycolysis",
"How do I filter for reviewed mouse proteins which carry an N-terminal glycine?"
]
#%%
for question in list_questions:
    print(question)
    res_tbox = parser_sentence(question, t_box_index, endpoint_t_box)
    for res in res_tbox[:3]:
        print(res['label'])
        print(res['content']['?term'])
        print(res['score'])
        print('---')    
# %%
