from transformers import pipeline
import json
import ast

model_name = "Qwen/Qwen2.5-3B-Instruct"
pipe = pipeline("text-generation", model=model_name, device=0, max_new_tokens=1024)

INTENTS = {
  "intent": "product_search | compare | recommendation | cart_action | purchase | jibberish | unknown",
  "category": "string | None",
  "filters": {
    "price_min": "number | None",
    "price_max": "number | None",
    "brand": "string[] | None",
    "attributes": "string[] | None"
  },
  "items_for_comparison": "string[] | None",
  "cart_action": "add | remove | empty | show | None"
}

ITEMLIST = {"items": "string[] | None"}

def set_query(QUERY, existing_conversation=None, prompt=None):

    persona = f"""You are a helpful assisstant."""

    prompt = prompt or f"""
    You are an intent parser.

    Return ONLY valid JSON in this exact format:
    {INTENTS}

    If no intent matches, use None.

    User input:
    "{QUERY}"
    """

    messages = existing_conversation or [{"role": "system", "content": persona}]
    messages.append({"role": "user", "content": prompt})

    return messages

def intent_parse(query, existing_conversation=None):
    prompt = set_query(query, existing_conversation)
    output = pipe(prompt)
    output_dict = ast.literal_eval(output[0]['generated_text'][-1]['content'])

    if 'category' not in output_dict:
        output_dict['category'] = None

    if 'filters' not in output_dict or output_dict['filters']==None:
        output_dict['filters'] = dict()

    if 'items_for_comparison' not in output_dict:
        output_dict['items_for_comparison'] = None

    for i in ["price_min", "price_max", "brand", "attributes"]:
        if i not in output_dict['filters']:
            output_dict['filters'][i] = None

    return output_dict, output[0]['generated_text']

def item_parse(query, existing_conversation=None):

    p = f"""
        You are an intent parser.

        Your task is to return a list of items given a User input.

        Return ONLY valid JSON in this exact format:
        {ITEMLIST}

        If no intent matches, use None.

        User input:
        "{query}"
        """

    prompt = set_query(query, existing_conversation, prompt=p)
    output = pipe(prompt)
    output_dict = ast.literal_eval(output[0]['generated_text'][-1]['content'])

    return output_dict, output[0]['generated_text']

def summarize(query, existing_conversation=None):

    p = f"""
        Your task is to compare a series of items from a User input.

        You should evaluate the pros and cons of each item and summarize your findings in an easily digestible manner.

        User input:
        "{query}"
        """

    prompt = set_query(query, existing_conversation, prompt=p)
    output = pipe(prompt)
    summary = output[0]['generated_text'][-1]['content']

    return summary, output[0]['generated_text']

if __name__ == "__main__":
    existing_conversation = None

    while True:
        query = input("Enter Prompt Here: ")
        prompt = set_query(query, existing_conversation)

        output, existing_conversation = intent_parse(query, existing_conversation)
        print(output)

        with open("conversation.txt", 'w') as f:
            f.write(str(existing_conversation))