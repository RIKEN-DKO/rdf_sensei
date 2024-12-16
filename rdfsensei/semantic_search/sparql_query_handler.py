import re
import warnings
from dotenv import load_dotenv

load_dotenv()

class SPARQLQueryHandler:
    def __init__(self, endpoint, llm_strategy, model_name="gpt-3.5-turbo-16k", messages_nl=None):
        self.endpoint = endpoint
        self.llm_strategy = llm_strategy
        self.model_name = model_name
        self.messages_nl = messages_nl

    def processQuery(self, user_question, sparql_query, temperature=0.7):
        # Execute the SPARQL query and get the results
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            try:
                question_formulated, query_results = self.endpoint.struct_result_query(sparql_query)
            except Exception as e:
                print("Error executing SPARQL query:", e)
                return {
                    'answer': "I'm sorry, I cannot retrieve information at this time.",
                    'question': user_question,
                    'sparql': sparql_query,
                    'results': None
                }

        # Prepare the prompt for the LLM with the user question, SPARQL query, and results
        prompt = f"""
        User question: "{user_question}"
        SPARQL query:
        ```sparql
        {sparql_query}
        ```
        JSON result set:
        ```json
        {query_results}
        ```
        Please provide a helpful and concise answer to the user's question based on the SPARQL results.
        """

        # Add the prompt to the NL messages (if a context manager is used)
        if self.messages_nl:
            self.messages_nl.add({"role": "user", "content": prompt})
            completion = self.llm_strategy.create_completion(
                model_name=self.model_name, 
                messages=self.messages_nl.to_list(), 
                temperature=temperature
            )
        else:
            # If no messages_nl context is provided, just use a simple prompt
            completion = self.llm_strategy.create_completion(
                model_name=self.model_name, 
                messages=[{"role":"user", "content": prompt}], 
                temperature=temperature
            )

        # Extract the answer from the completion
        answer = completion.choices[0].message.content.strip()

        # Optionally store the answer in the messages context
        if self.messages_nl:
            self.messages_nl.add({"role": "assistant", "content": answer})

        return {
            'answer': answer,
            'question': user_question,
            'sparql': sparql_query,
            'results': query_results
        }

    @staticmethod
    def extractSPARQL(text):
        searchSPARQL = re.search("```(.|\n)*```", text)
        if searchSPARQL is None:
            return ''
        start, end = searchSPARQL.span()
        sparql = text[start:end]
        sparql = sparql.replace("```sparql", "").replace("```", "")
        return sparql

    @staticmethod
    def printAnswer(llmAnswer):
        if llmAnswer['sparql'] is not None:
            finalAnswer = f"""User: {llmAnswer['question']}\nGPT: {llmAnswer['answer']}\n\nSPARQL:\n{llmAnswer['sparql']}\n-------------------------------------------------------------\n"""
        else:
            finalAnswer = f"""User: {llmAnswer['question']}\nGPT: {llmAnswer['answer']}\n-------------------------------------------------------------\n"""
        print(finalAnswer)
