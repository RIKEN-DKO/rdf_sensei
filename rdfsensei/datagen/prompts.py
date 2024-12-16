prompt_get_sparqls = """
            These are the TBOX and ABOX of a RFD Knowledge graph database

            TBOX:
            ```
            {TBOX}

            ```


            ABOX:

            ```
            {ABOX}
            ```

            I want you suggest question and SPARQL queries pairs to explore this KG considering the TBOX and ABOX. 

            Steps for one question-SPARQL pair:
            1.Choose one and only one row from the TBOX or ABOX. Create a `label2URI` map:
            ```
            'SH B6':rikenbrc_mouse:00220
            ```
            with format `LABEL:URI`. 

            2. Create a question that include the classes/terms LABEL from the `label2URI` map.
            4. Build a SPARQL query that answers the question but use triples with URI from the `label2URI` map. 


            - Repeat until generating {n_questions} question, label2uri, SPARQL queries triplet.  
            - Aim to generate a diverse set of SPARQL queries, do not repeat the same pattern.   
            - I each query include `FROM <{database}>` between `SELECT` and `WHERE`.
            - When using CONTAINS() function use the str() function to ensure the value is treated as a string.
            - Always use prefixes in the SPARQL queries.
            - Format each triplet as follows:
            
            ###<NUMBER>:
            **label2uri:**
            ```
            'CRISPR/Cas9': <http://metadb.riken.jp/terms/xsearch#resource_type_CRISPR>
            ```

            **question:**
            What attributes are associated with the term 'Mus musculus'?
    
            **SPARQL:**
            ```sparql
             PREFIX ...           
             ```

            

        """

prompt_get_sparqls_from_path = """You are provided with the following RDF path in the next format:

Class path:
S_1 P_1 O_1 .
S_2 P_2 O_2 .
...

where S: subject, P: predicate, O: object classes. Notice that O_1 and S_2 are the same since it's a path, it's just continuing.

Then I provide the instance path (the thing we want to retrieve) in turtle format.

Instance path:
s p o .
s p o .
...
#LABELS:
s p o .

After `#LABELS:` it comes the label definitions of some of the instance nodes.

RDF path:
{description}

Using this information:

1. Generate a natural language question that involves these entities and their relationships of the path. The answer must be contained in the path.

2. Provide a SPARQL query that retrieves the path or the data needed to answer the question from the path. Use the appropriate RDF properties and classes, and ensure that the query is compatible with the given RDF data.

Output the question and the SPARQL query as:

**question:**
[Your question here]

**SPARQL:**
```sparql
[Your SPARQL query here]
```
"""


# context/prompts.py

prompt_get_sparqls_from_community = """You are provided with the following RDF path in the next format:

Class path:
S_1 P_1 O_1 .
S_2 P_2 O_2 .
...

where S: subject, P: predicate, O: object classes. Notice that O_1 and S_2 are the same since it's a path, it's just continuing.

Then I provide the instance path (the thing we want to retrieve) in turtle format.

Instance path:
s p o .
s p o .
...
#LABELS:
s p o .

After `#LABELS:` it comes the label definitions of some of the instance nodes.

RDF path:
{description}

Using this information:

1. Generate a natural language question that involves these entities and their relationships of the path. The answer must be contained in the path.

2. Provide a SPARQL query that retrieves the path or the data needed to answer the question from the path. Use the appropriate RDF properties and classes, and ensure that the query is compatible with the given RDF data.

Output the question and the SPARQL query as:

**question:**
[Your question here]

**SPARQL:**
```sparql
[Your SPARQL query here]
"""

prompt_get_sparqls_from_path_questionsvar = """You are provided with the following RDF path in the next format:

Class path:
S_1 P_1 O_1 .
S_2 P_2 O_2 .
...

where S: subject, P: predicate, O: object classes. Notice that O_1 and S_2 are the same since it's a path, it's just continuing.

Then I provide the instance path (the thing we want to retrieve) in turtle format.

Instance path:
s p o .
s p o .
...
#LABELS:
s p o .

After `#LABELS:` it comes the label definitions of some of the instance nodes.

RDF path:
{description}

Using this information:

1. Generate a natural language question that involves these entities and their relationships of the path. The answer must be contained in the path.

2. Provide a SPARQL query that retrieves the path or the data needed to answer the question from the path. Use the appropriate RDF properties and classes, and ensure that the query is compatible with the given RDF data.

Also generate 5 variations of the question.
Each a variation aim to be more 'natural'. For natural
is that it must be more simple, shorter and with less verbosity.
Then it must look more simple without all exact references to the data. E.g
Original question : 'Who's the person that is president of the country USA?' 
User questions:'Who's the president of America?'



Output the question and the SPARQL query as:

**question:**
[question]
[question variation 1]
[question variation 2]
...

**SPARQL:**
```sparql
[Your SPARQL query here]
```
"""


prompt_get_sparqls_from_path_questionsvar_el = """You are provided with the following RDF path in the next format:

Class path:
S_1 P_1 O_1 .
S_2 P_2 O_2 .
...

where S: subject, P: predicate, O: object classes. Notice that O_1 and S_2 are the same since it's a path, it's just continuing.

Then I provide the instance path (the thing we want to retrieve) in turtle format.

Instance path:
s p o .
s p o .
...
#LABELS:
s p o .

After `#LABELS:` it comes the label definitions of some of the instance nodes.

RDF path:
{description}

Using this information:

1. Generate a natural language question that involves these entities and their relationships of the path. The answer must be contained in the path.
- **Entity Highlighting**: Surround each entity in the question with `<<` and `>>` to make them easily identifiable.
2. Provide a SPARQL query that retrieves the path or the data needed to answer the question from the path. Use the appropriate RDF properties and classes, and ensure that the query is compatible with the given RDF data.

3. **Generate 5 variations of the question**:

   - Aim for increased naturalness by making questions simpler, shorter, and less verbose.
   - **Use synonyms** for the entities in the variations to introduce more variability.

4. **Provide an Entity-to-URI Mapping**:

   - List each entity mentioned in the questions along with their corresponding URIs from the RDF data.

5. **Provide a SPARQL query template**:

   - Create another version of the SPARQL query where entities are replaced with placeholders (e.g., `?entity1`, `?entity2`). This template can be filled in with the actual entities later.


Output the question and the SPARQL query as:

**question:**
[question]
[question variation 1]
[question variation 2]
...

**SPARQL:**

[Your SPARQL query here]


**Entity to URI Mapping:**

<<Entity 1>>: <URI 1>
<<Entity 2>>: <URI 2>
...


**SPARQL Template:**

[Your SPARQL query template with placeholders here]

**Example output:**

**question:**
 1. What are the species present in Bgee and their <<scientific>>E_1 and <<common names>>E_2?
 2. Get the species in Bgee with it's <<scientific name>>E_1 and <<common name>>E_2?
...

**SPARQL:**

   SELECT ?occupationLabel WHERE {{
     ex:JohnDoe ex:hasOccupation ?occupation .
     ?occupation rdfs:label ?occupationLabel .
   }}


**Entity to URI Mapping:**

   E_1: ex:JohnDoe
   E_2: ex:SoftwareEngineer


**SPARQL Template:**

   PREFIX up: <http://purl.uniprot.org/core/> 
   SELECT ?species ?sci_name ?common_name 
   {{  ?species a up:Taxon .   
      ?species <<E_1>> ?sci_name .  
      ?species up:rank up:Species .    
      OPTIONAL {{ ?species <<E_2>> ?common_name . }} 

   }}



"""

prompt_get_sparqls_from_path_questionsvar_examples = """You are provided with the following RDF path in the next format:

Class path:
S_1 P_1 O_1 .
S_2 P_2 O_2 .
...

where S: subject, P: predicate, O: object classes. Notice that O_1 and S_2 are the same since it's a path, it's just continuing.

Then I provide the instance path (the thing we want to retrieve) in turtle format.

Instance path:
s p o .
s p o .
...
#LABELS:
s p o .

After `#LABELS:` it comes the label definitions of some of the instance nodes.

RDF path:
{description}

Using this information:

1. Generate a natural language question that involves these entities and their relationships of the path. The answer must be contained in the path.

2. Provide a SPARQL query that retrieves the path or the data needed to answer the question from the path. Use the appropriate RDF properties and classes, and ensure that the query is compatible with the given RDF data.

Also generate 5 variations of the question.
Each a variation aim to be more 'natural'. For natural
is that it must look like an user create the questions
Then it must look more simple without all exact references to the data. E.g
Original question : 'Who's the person that is president of the country USA?' 
User questions:'Who's the president of America?'

Original question : 'Who's the person that is president of the country USA?' 
User question: "What's ReactionSide synonym? "

We are providing example question and SPARQL pairs queries to guide you in the type of pairs we want.
{examples}


Output the question and the SPARQL query as:

**question:**
[question]
[question variation 1]
[question variation 2]
...

**SPARQL:**
```sparql
[Your SPARQL query here]
```
"""


prompt_rating_questions = """
You are an evaluator tasked with determining how well each question can be answered using the provided data(SPARQL RESULTS).

**Instructions:**
- For each question, assign a rating based on the following scale:  
  - **0**: The data have nothing that can be used as answer for the question.  
  - **1**: It's possible that the questions and data are related.  
  - **2**: The question can be minimally answered; most required information is missing.  
  - **3**: The question can be partially answered from the data but lacks some information.  
  - **4**: The question can be answered from the data.  

  
**SPARQL:**
{sparql}
**SPARQL RESULTS:**
{data}

**Questions:**
{questions}

**Output Format:**
Question 1:
- **Rating**: X

Question 2:
- **Rating**: X

...
---

**Tips for Effective Evaluation:**
- **Focus on the Data**: Ensure that you consider only the information provided in the data section when evaluating each question.
- **Data format**: The data is in a structured format(JSON) and can be used to answer the questions:
**Questions:**
1. What are the species present in Bgee?
1. Which are the species present in Bgee?

**SPARQL:**

**SPARQL RESULTS:**


Then also consider the SPARQL RESULTS field like `species` in the data section to answer the questions. URI like
`http://purl.uniprot.org/taxonomy/7994` are aceptable answers.
- **Questions**: Most questions are related and variations of each other.
- **Be Concise**: Keep explanations brief and to the point to maintain clarity.
- **Consistency**: Apply the rating criteria consistently across all questions.
"""

# ---

# **Example Usage:**
# Suppose we have the following data and questions.

# **Data:**


# **Questions:**
# 1. "What is the capital city of France?"
# 2. "What are the digits of Pi?"


# **Expected Output:**
# Question 1:
# - **Rating**: 2

# Question 2:
# - **Rating**: 0
