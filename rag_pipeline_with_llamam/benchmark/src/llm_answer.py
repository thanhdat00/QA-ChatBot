from langchain_community.llms import Ollama
import pandas as pd
llm_model =  Ollama(model="qwen2.5:latest")

def rag_pipeline(query: str, list_context: list[str]):
    ## Search query

    context = [f"""
               - context {context}
               ---
               """ for context in list_context]

    prompt_formatted = '''
        You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question or history of the chat. If you don't know the answer, just say that you don't know. Please answer using Vietnames. Use three sentences maximum and keep the answer concise.
        Question: {question}
        Context: {context}
        Answer:

        '''.format(
        question=query, context=context)

    llm_res = llm_model.invoke(prompt_formatted)
    print(llm_res)

def get_llm_response(file_path: str):
    df = pd.read_parquet(file_path)
    df = df[:100]
    for index, row in df.iterrows():
        question = row['question']
        context = row['context']
        llm_answer = rag_pipeline(question, context)
        df.at[index, 'llm_answer'] = llm_answer

    df.to_csv("response_llm.csv", index=False)