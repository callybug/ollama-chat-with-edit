'''
TODO:
    hotkey (Ctrl+C) to CANCEL the response generation
    hotkey to write user prompt in $EDITOR
    all the parameter stuff from ollama

    save/load filenames rather than just save.json in
    current location

    streaming text - THE TROUBLE IS just copying what was
    off the example and changing variables, the SAVED RESPONSE
    is DIFFERENT from the STREAMED RESPONSE! so SOD IT
'''

from ollama import chat
from ollama import show
import sys, tempfile, os, json, signal, textwrap
from subprocess import call

PROMPT_SYMBOL = "> "
MULTILINE = ":::"
NEW_LINE = r'\n'
#commands
COMMAND_INITIATE = "/"
PRINT_HELP = ("help","?")
EDIT_RESPONSE = "edit"
REGEN_RESPONSE = "retry"
UNDO_PROMPT = "undo"
PRINT_MESSAGES = "convo"
CLEAR_SCREEN = "clear"
ERASE_CONVO = "erase"
SAVE = "save"
LOAD = "load"
EXIT = "bye"

DEFAULT_MODEL = "mistral-nemo"
EDITOR = os.environ.get('EDITOR', 'vim')
SAVE_FILE = "save.json"

def printHelp():
    print( MULTILINE + NEW_LINE + "\t start multi-line prompt, then")
    print( NEW_LINE + MULTILINE + NEW_LINE + "\t to finish multi-line prompt")
    print( COMMAND_INITIATE + SAVE + "\t saves chat history to json file")
    print( COMMAND_INITIATE + LOAD + "\t loads chat history from json file")
    print( COMMAND_INITIATE + REGEN_RESPONSE + "\t regenerates response from same prompt")
    print( COMMAND_INITIATE + UNDO_PROMPT + "\t deletes last prompt and response, going back one exchange")
    print( COMMAND_INITIATE + EDIT_RESPONSE + "\t edit last response/inference in $EDITOR")
    print( COMMAND_INITIATE + PRINT_MESSAGES + "\t prints out entire conversation as list")
    print( COMMAND_INITIATE + PRINT_HELP[1] + " or " + PRINT_HELP[0] + "\t prints out this help")
    print( COMMAND_INITIATE + CLEAR_SCREEN + "\t clears screen, preserving chat")
    print( COMMAND_INITIATE + ERASE_CONVO + "\t erase all conversation context")
    print( COMMAND_INITIATE + EXIT + "\t exits")

messages = [
#  {
#    'role': 'user',
#    'content': 'Why is the sky blue?',
#  },
#  {
#    'role': 'assistant',
#    'content': "The sky is blue because of the way the Earth's atmosphere scatters sunlight.",
#  },
#  {
#    'role': 'user',
#    'content': '',
#  },
#  {
#    'role': 'assistant',
#    'content': "",
#  },
]

def printwrapped(text):
    #refreshing terminal size in case it's changed
    tty_columns, tty_rows = os.get_terminal_size(0)
    print(\
            "\n".join("\n".join(textwrap.wrap(x, width=tty_columns, break_long_words=True, break_on_hyphens=True)) for x in text.splitlines())\
            )

model_name = DEFAULT_MODEL
lines = []
line = ""

try:
    last_response = (messages[-1]['content'])
    printwrapped(last_response)
except:
    last_response = ""

args = sys.argv[1:]
for pos, arg in enumerate(args):
    if arg == '-m':
        model_name = (args[pos+1])
        pos += 1
        try:
            chat(model_name) #checking if model argument exists in ollama's list
        except:
            printwrapped("model '" + model_name + "' not found. Using '" + DEFAULT_MODEL + "' instead.")
            model_name = DEFAULT_MODEL

def command_check(command):
    global line
    global messages
    if command == REGEN_RESPONSE:
        if messages:
            del messages[-1]
        else:
            print("Nothing to retry.")
            line = ""
    elif command == EXIT:
        sys.exit()
    elif command == ERASE_CONVO:
        messages = []
        line = ""
    elif command in PRINT_HELP:
        printHelp()
        line = ""
    elif command == PRINT_MESSAGES:
        print(messages)
        line = ""
    elif command == UNDO_PROMPT:
        if 4 <= len(messages):
            printwrapped(PROMPT_SYMBOL + messages[-4]['content'] + '\n')
            printwrapped("" + messages[-3]['content'] + '\n')
        if 2 <= len(messages):
            printwrapped("**UNDONE**-----------\n" + PROMPT_SYMBOL + messages[-2]['content'])
            printwrapped("**UNDONE**-----------")
            del messages[-2:]
        else:
            print("Nothing to undo.")
        line = ""
    elif command == EDIT_RESPONSE:
        line_to_edit = (last_response).encode('utf-8')
        if messages: #if there's anything in there
            with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
                tf.write(line_to_edit)
                tf.flush()
                call([EDITOR, tf.name])

                tf.seek(0)
                edited_message = tf.read()
                del messages[-1]
                messages += [
                  {'role': 'assistant', 'content': edited_message.decode("utf-8").rstrip()},
                ]
            print("Response changed to:")
            printwrapped(messages[-1]['content'])
        else:
            printwrapped("No response to edit.")
        line = ""
    elif command == SAVE:
        with open("save.json", 'w') as f:
            json.dump(messages, f)
            line=""
    elif command == LOAD:
        with open("save.json", 'r') as f:
            rangeno=-19
            messages = json.load(f)
            print("...\n(" + str(len(messages)//2-rangeno) +  " exchanges)") #TODO: check this is actually accurate
            print("...")
            for i in range(rangeno,0):
                if i % 2 == 0:
                    print(">", end=" ")
                    printwrapped(messages[i]['content'])
                else:
                    printwrapped(messages[i]['content'] + "\n")
            line=""
    elif command == CLEAR_SCREEN:
        os.system('clear')
        line=""
    else:
        print("Command not found.")
        line = ""

#Program start

print( COMMAND_INITIATE + PRINT_HELP[0] + " or " + COMMAND_INITIATE + PRINT_HELP[1] + " for commands")

while True:
    while line.rstrip() == "":
        line = input(PROMPT_SYMBOL)
        if line.startswith(COMMAND_INITIATE):
            command_check(line[1:])
        elif line == MULTILINE: #shitey multiline input
            while True:
                line = input(' >')
                if line == MULTILINE:
                    break
                else:
                    lines.append(line.rstrip())
        else:
            lines.append(line.rstrip())

    user_input = ("\n".join(lines))

    #add prompt to conversation history
    if user_input != "": #/retry command would produce blank result
        messages += [
          {'role': 'user', 'content': user_input},
        ]

    try:
        response = chat(
          model_name,
          messages=messages
    #      + [
    #        {'role': 'user', 'content': user_input},
    #      ],
        )

    #add response to conversation history
        messages += [
          {'role': 'assistant', 'content': response.message.content},
        ]
        #print the AI's response
        #print(response.message.content + '\n')

        response_to_print = response.message.content + '\n'
        #print response, wrapping text so it doesn't split half-way
        printwrapped(response_to_print)
    except KeyboardInterrupt:
        print("   response cancelled")
        del messages[-1] #delete prompt for cancelled response

    line = ""
    lines = []
    last_response = (messages[-1]['content'])
