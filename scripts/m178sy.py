import json


# Formatation Section...
class TTArray:
    def __init__(self,items_type:type):
        self.items_type=items_type
    @property
    def t(self):
        return self.items_type

def xtype(type_,description:str,enum:list=None):
    if description == 'no_desc':
        if type_ == str and enum != None:
            return {"type":"string","enum":enum}
        elif type_ == int and enum != None:
            return {"type":"integer","enum":enum}
        elif type_ == float and enum != None:
            return {"type":"float","enum":enum}
        elif type_ == str:
            return {"type":"string"}
        elif type_ == int:
            return {"type":"integer"}
        elif type_ == float:
            return {"type":"float"}
        elif isinstance(type_,TTArray):
            return {"type":"array","items":type_.t}
        else:
            raise ValueError("Invalid value for xtype.argumentParser")
    if type_ == str and enum != None:
        return {"type":"string","enum":enum,"description":description}
    elif type_ == int and enum != None:
        return {"type":"integer","enum":enum,"description":description}
    elif type == float and enum != None:
        return {"type":"float","enum":enum,"description":description}
    elif type_ == str:
        return {"type":"string","description":description}
    elif type_ == int:
        return {"type":"integer","description":description}
    elif type_ == float:
        return {"type":"float","description":description}
    elif isinstance(type_,TTArray):
        return {"type":"array","description":description,"items":type_.t}
    else:
        raise ValueError("Invalid value for xtype.argumentParser")

def gen_func(func_name:str,func_desc:str,required=all,**kwargs): # example -> gen_func("insert_members",required=["mname","mbudget"],mname=xtype(str,"member name"),mbudget=xtype(int,"member budget in us dollars",enum=[100,200,300,400]),keywords=xtype(TTArray(xtype(str,"no_desc")),"keyword"))
    properties = {}
    for key in kwargs:
        properties[key] = kwargs[key]
    
    return {
        "type": "function",
        "function": {
            "name": func_name,
            "description":func_desc,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required if required != all else list(kwargs.keys()),
                "additionalProperties": False,
            },
        },
    }
def gen_func_response(tool_call_id:str,func_name:str,func_output:json): # out.choices[0].message.tool_calls[n].id
    return {
        "tool_call_id":tool_call_id,
        "role":"tool",
        "name":func_name,
        "content":func_output if isinstance(func_output,str) else json.dumps(func_output)
    }
# ------------------------------------------------------------------------------------------------------------------
# NIGGA I AM M1778
import os
import subprocess
import json
from pathlib import Path
from typing import *
from openai import OpenAI

SYSTEM_PROMPT="""You are the ultimate programmer of all time.
You are participating in a competetion contest of University of Isfahan.

most of the problems you have to solve is algorithm based and need optimized solutions (It doesn't have to be super optimized, just basic solutions)

The files of the problems are provided by user and you have the ability to read, write and even run files to have a test environment.

For example:
    the user gives you a task to solve a algorithm based problem and explanations of it is in a file named "problem1.txt" at /home/Contest/problem1.txt
    You have to read the problem1.txt and understand the logic behind it and there are sample input and sample output that will be given to you, also user provides how the input is given to your program which mostly is come from the `input` function of python (More explanation for inputs will be given to you by user)
    Then you write a file with the solution and algorithm and handle input there and for the same file you make another test file that will be run like "python solution.py | python test_inputs.py" something like this but that's just for user.
    User will give you results and if there are any problems user will provide you context for you to fix the program
"""

def Status(st, sttype, content:str=None):
    return {
        "Status":st,
        "Type":sttype,
        "Content":content
    }

class Funcs:
    def FileExists(filepath:str)->dict:
        try:
            if Path(filepath).exists():
                msg = f"The file '{filepath}' already exists."
            else:
                msg = f"The file '{filepath}' doesn't exists."
            return Status("Success", "Boolean", msg)
        except Exception as err:
            return Status("Error","UnknownError", f"ERR: {err}\nUse external ways to check a file exists")
    def ReadFile(filepath:str)->dict:
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                f.close()
            return Status("Success", "Document", content)
        except Exception as err:
            return Status("Error","UnknownError", f"ERR: {err}\nUse external ways to read a file")
    def WriteFile(filepath:str, content:str)->dict:
        try:
            with open(filepath, 'w') as f:
                f.write(content)
                f.close()
            return Status("Success", "DocumentWriteSuccess", f"Wrote {len(content)} characters to file '{filepath}'.")
        except Exception as err:
            return Status("Error","UnknownError", f"ERR: {err}\nUse external ways to write a file")

    def RunPy(filepath:str)->dict:
        try:
            o = subprocess.getoutput(f'python {filepath}')
            return Status("Success", "Output", o)
        except Exception as err:
            return Status("Error", "UnknownError", f"ERR: {err}")

    def Callback()->dict:
        return Status("Success", "CallbackType", "This is just a placeholder, It's for easier access for you, we're calling you back for analysis after using some tool calls.")

tools = [
    gen_func("ReadFile", "Reads the contents of a file by its filepath", filepath=xtype(str, "the path of the file you want to read")),
    gen_func("WriteFile", "Creates or overwrites a file by the provided filepath and content of the file", filepath=xtype(str, "the path of the file you want to write in"), content=xtype(str, "the content of the file you want to write")),
    gen_func("RunPy", "Runs a python file by its given path and returns the output of the program", filepath=xtype(str, "the path of the python file you want to run")),
    gen_func('FileExists', "Check if a file exists with the given path", filepath=xtype(str, "the path of the file you want to check if exists")),
    gen_func("Callback", "Used for A.I to call itself back when it needs to retrieve data and analyze and call tools again, mostly used after tools like (ReadFile, FileExists)")
]

def run_func(func_name:str, **kwargs)->dict:
    return json.dumps(getattr(Funcs, func_name)(**kwargs))

class M1778Sync:
    def __init__(self,Client:OpenAI):
        self.client:OpenAI = Client
        self.messages = []
        self.tools = tools
    
    def complete(self, model:str):
        return self.client.chat.completions.create(
            model=model,
            messages=self.messages,
            tools=self.tools,
            tool_choice='auto',
            temperature=0.2
        )
    def system_message(self, content:str)->bool:
        self.messages.append({'role':'system','content':content})
        return True
    def user_message(self, content:str)->bool:
        self.messages.append({'role':'user','content':content})
        return True
    def assistant_message(self, content:str)->bool:
        self.messages.append({'role':'assistant', 'content':content})
        return True

    def handle(self, response:Any):
        ...

class LLMHandler:
    def __init__(self):
        ...
    def get_input(self,callback):
        ge = input("User: ")
        callback(ge)
    def print_assistant(self, content:str):
        print("Assistant: ", content)
    

def nvidia():
    global endpoint, model, client
    endpoint = "https://integrate.api.nvidia.com/v1"
    model = 'qwen/qwen3-coder-480b-a35b-instruct'
    client = OpenAI(base_url=endpoint, api_key="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")

def groq():
    global endpoint, model, client
    endpoint = "https://api.groq.com/openai/v1"
    model = "moonshotai/kimi-k2-instruct-0905"
    client = OpenAI(base_url=endpoint, api_key="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")

def cohere():
    global endpoint, model, client
    endpoint = "https://api.cohere.ai/compatibility/v1"
    model = "command-a-03-2025"
    client = OpenAI(base_url=endpoint, api_key="pqSgRiVhxvRLcFzeIis09B9GS6pRyhGi9MrfGkst")

def cloudflare():
    global endpoint, model, client
    endpoint = "https://api.cloudflare.com/client/v4/accounts/727e6364298844f3b9b365632a11cd4a/ai/v1"
    model = "@cf/meta/llama-4-scout-17b-16e-instruct"
    client = OpenAI(base_url=endpoint, api_key="euINGyt45TVKK2N2lJHGSJHa664vNXwwT0bKbeoT")

print("""1. Nvidia
2. Groq
3. Cohere
4. Cloudflare""")

cli = int(input("Choose a client:"))

if cli == 1:
    endpoint = "https://integrate.api.nvidia.com/v1"
    model = 'qwen/qwen3-coder-480b-a35b-instruct'
    client = OpenAI(base_url=endpoint, api_key="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")
elif cli == 2:
    endpoint = "https://api.groq.com/openai/v1"
    model = "moonshotai/kimi-k2-instruct-0905"
    client = OpenAI(base_url=endpoint, api_key="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")
elif cli == 3:
    endpoint = "https://api.cohere.ai/compatibility/v1"
    model = "command-a-03-2025"
    client = OpenAI(base_url=endpoint, api_key="pqSgRiVhxvRLcFzeIis09B9GS6pRyhGi9MrfGkst")
elif cli == 4:
    endpoint = "https://api.cloudflare.com/client/v4/accounts/727e6364298844f3b9b365632a11cd4a/ai/v1"
    model = "@cf/meta/llama-4-scout-17b-16e-instruct"
    client = OpenAI(base_url=endpoint, api_key="euINGyt45TVKK2N2lJHGSJHa664vNXwwT0bKbeoT")
else:
    raise TypeError("WTF")

m = M1778Sync(client)
m.system_message(SYSTEM_PROMPT)

llm = LLMHandler()

def agent_mode():
    while True:
        llm.get_input(m.user_message)
        def call():
            completion = m.complete(model)
            if completion.choices:
                if completion.choices[0].finish_reason == 'tool_calls':
                    message = completion.choices[0].message
                    m.assistant_message(message.content)
                    llm.print_assistant(message.content)
                    tool_calls = message.tool_calls
                    for tool_call in tool_calls:
                        if tool_call.type == 'function':
                            function = tool_call.function
                            args = json.loads(function.arguments)
                            name = function.name
                            output = run_func(name, **args)
                            m.messages.append({"tool_call_id": tool_call.id,
                                "role": "tool", 
                                "name": name,
                                "content": output})
                            if name == "Callback":
                                call()
                elif completion.choices[0]:
                    message = completion.choices[0].message
                    m.assistant_message(message.content)
                    llm.print_assistant(message.content)
                else:
                    print("GAY")
            else:
                print("BRoooo")
        call()
def normal_mode():
    while True:
        llm.get_input(m.user_message)
        completion = m.complete(model)
        if completion.choices:
            message = completion.choices[0].message
            m.assistant_message(message.content)
            llm.print_assistant(message.content)
        else:
            print("Brooo")

if __name__ == "__main__":
    print("1. Normal mode\n2. Agent mode\n\n")
    if int(input("Which one do you want: ")) == 2:
        agent_mode()
    else:
        normal_mode()