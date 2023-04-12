import os
import json
import openai
import imghdr
import dotenv
import shutil
import requests
def isLs(ls):
    if type(ls) is list:
        return True
    return False
def isDict(ls):
    if type(ls) is dict:
        return True
    return False
def isStr(ls):
    if type(ls) is str:
        return True
    return False
def getOpenAiKey():
    dotenv.load_dotenv()
    return os.getenv("OPENAI_API_KEY")
def pen(x,p):
  with open(p, 'w',encoding='UTF-8') as f:
    f.write(str(x))
    return p
def reader(x):
  with open(x, 'r',encoding='UTF-8') as f:
    return f.read()
def readLoadDump(x):
    dumpIt(loadIt(reader(x)),x)
def jsIt(js):
    return str(js).replace("'",'"')
def tryJs(js):
    try:
        js = json.loads(js)
    except:
        js = js
    return js
def loadIt(js):
    if isDict(js):
        return js
    jsN = js
    if isStr(jsN):
        jsN = tryJs(jsN)
    if not isDict(jsN):
        jsN = tryJs(jsIt(jsN))
    return jsN
def dumpIt(x):
    return json.dumps(x)
def getChoose():
    return 'chooseInit.py'
def getKeys(js):
    return list(loadIt(js).keys())
def jsFill(js):
    js = loadIt(js)
    jsN,keys = initialResp(),getKeys(js)
    for k in range(0,len(keys)):
        jsN[keys[k]] = js[keys[k]]
    return jsN
def chooseInit(path):
    ls = list(loadIt(reader(getChoose())).keys())
    type = ls[int(input('choose prompt:\n'+mkLsQuery(ls)))]
    if type == 'custom':
        type = createCustomInit()
    init = loadIt(reader(getChoose()))[type]
    init['dirMap'] = getDirMap(path)
    return init
def createCustomInit():
    init,doc = input("what to call this selection?"),jsIt(reader(getChoose()))
    doc[init] = {"goal":input("what are we doing?: "),"name":input("what is the project name: "),"description":input("describe a little about your project: "),"notes":input("any notes?: "),'dirMap':""}
    pen(json.dumps(doc),'chooseInit.py')
    return init
def getDirMap(path):
    return create_directory_map(path)
def mkLsQuery(ls):
    n = ''
    input(ls)
    for k in range(0,len(ls)):
        n = n + '\n'+str(k)+') '+ls[k]
    return n+'\n'
def changeGlob(x,y):
    globals()[x]=y
    return y
def getInitialPrompt(js):
     return f"""
Hi there, this is a project named {js['name']}, which is {js['description']}. The goal right now is {js["goal"]}. There are {len(js['dirMap'])} files in the directory, and I am going to query you with portions until the entire map has been fed. Please respond accordingly as per the context of the goal. The directory map is: {js['dirMap']}.

As for responses, they will be expected to be in JSON format with the keys as follows:

1) botNotation - If at any point in time you need to preserve notes that you feel would aid in the goal for yourself, respond with that note. This will be continually fed back to you through the process, so zero notes are always preferred but obviously not required.

2) goalResponse - This will be in JSON format, such as {{'dirMap': {{'note': '','num':int(dirMap#)}}}}.

3) reassess - This is simply a bool statement. If you feel that the goal is untenable or cannot be met, respond with True and a reason stated in the botNotation remarks, otherwise, False will be fine.

4) revision - if the goal calls for revision or the revision key in the JSON prompt is True, you will need to revise the content that was sent, if no revision is neccisary or otherwise not called for return the revision key as False; otherwise return the fully revised content instead 

5) general - this will be anything that does not fit into the category of the first 3 keys

all responses will need to be in json format under either of the 5 keys

Is there anything you'd like to add or relay about this before we go forward? (please initiate the json responses immediately
"""
def getInitTokSize():
    return f"""
This is a preliminary before the feed starts. Please return the following JSON with your preferences:
{{'desiredTokenSize': '', 'maxTokenSiez': ''}}
If it is not definitive, respond with the default of 2046.
"""
def checkReassess(resp):
    if resp['reassess'] == True or resp['botNotation'] != '':
        input(['reassess: ',resp['reassess'],resp['botNotation']])
    return False
def checkGeneral(resp):
    if resp['general'] != '':
        input(['general: ',resp['general']])
    return ''
def goalResp(resp):
    input(['goalResponse: ',resp['goalResponse']])
    return resp['goalResponse']
def ifrRev(orig,js):
    if js['revision'] in ['',False]:
        js['revision'] = orig
    return js
def desiredResponseFormat(resp):
    return {"botNotation": resp['botNotation'],"goalResponse":goalResp(resp) ,"reassess": checkReassess(resp),"general": checkGeneral(resp)}
def initialResp():
    return {"botNotation": "","goalResponse":"" ,"reassess": "","revision": "","general": ""}
def imgTF(file_path):
    if not imghdr.what(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return False
        except (UnicodeDecodeError, IOError) as e:
            print(f"Error reading file: {file_path}. {e}")
            return False
    else:
        return True
def process_file_content(content, resp, file_path):
    updated = ''
    resp = loadIt(resp)
    sections = [content[i:i + token_size['desiredTokenSize']] for i in range(0, len(content), token_size['desiredTokenSize'])]

    for index, section in enumerate(sections):
        section_prompt = f'\n\nThis is section {index + 1} of {len(sections)} for {file_path}:\n'
        send_it = {"botNotation": resp["botNotation"], "revision": resp["revision"], "section_prompt": section_prompt, "section": section}
        tokens = tokenize(str(send_it))

        if token_size['maxTokenSize'] < tokens:
            subsections = [section[i:i + token_size['desiredTokenSize']] for i in range(0, len(section), token_size['maxTokenSize'])]
            for sub_index, subsection in enumerate(subsections):
                subsection_prompt = f'\n\nThis is subsection {sub_index + 1} of {len(subsections)} for section {index + 1} of {len(sections)} for {file_path}:\n'
                send_it["subsection_prompt"] = subsection_prompt
                send_it["subsection"] = subsection
                resp = send_to_openai(send_it)
                updated += ifrRev(send_it["subsection"], resp)['revision']
        else:
            resp = send_to_openai(send_it)
            updated += ifrRev(send_it["section"], resp)['revision']
    print(updated)
    return resp

def read_file_if_not_image(file_path):
    if not imghdr.what(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return content
        except (UnicodeDecodeError, IOError) as e:
            print(f"Error reading file: {file_path}. {e}")
            return None
    else:
        print(f"{file_path} is an image file.")
        return None
def get_size(path):
    if os.path.isfile(path):
        return os.path.getsize(path)
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for file in filenames:
            fp = os.path.join(dirpath, file)
            total_size += os.path.getsize(fp)
    return total_size
def tokenize(text):
    return len(text.split())
def process_files(folder_path,js):
    
    resp = send_to_openai(getInitialPrompt(chooseInit('/home/fresh1/Desktop/newReact/openai-react/src')))
    changeGlob('token_size',{'desiredTokenSize':1023,'maxTokenSize':2046})#'send_to_openai(getInitTokSize())
    # Update your process_files function with this loop
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            content = read_file_if_not_image(file_path)
            if content is not None:
                resp = process_file_content(content, resp, file_path)      

def GETHeader():
  return {"Content-Type" :"application/json","Authorization": "Bearer "+getOpenAiKey()}
def reqGet(js):
  return requests.post('https://api.openai.com/v1/chat/completions',json=loadIt(js),headers=GETHeader())
def send_to_openai(text):
    input(text)
def send_to_openai(send_it):
    # Truncate the section before sending it to the API
    text = send_it
    if "section" in send_it:
        section = send_it["section"][:int(token_size['maxTokenSize'])]
        # Create the text to send to the API
        text = f'botNotation: {send_it["botNotation"]}{send_it["section_prompt"]}{section}'
    
    jsDump = dumpIt({"model": "gpt-3.5-turbo","messages": [{"role": "user", "content": send_it}]})
    resp = reqGet(jsDump).json()

    if 'choices' in resp:
        resp = resp['choices']
    if isLs(resp):
        resp = resp[0]
    if 'message' in resp:
        resp = resp['message']
    if 'content' in resp:
        resp = resp['content']
    resp = jsFill(resp)
    input(isDict(resp))
    return resp



def create_directory_map(folder_path):
    directory_map = {}
    replica_folder_path = folder_path + "_replica"

    # Remove the replica folder if it exists, and create a new one
    if os.path.exists(replica_folder_path):
        shutil.rmtree(replica_folder_path)
    shutil.copytree(folder_path, replica_folder_path, ignore=shutil.ignore_patterns('*.*')) # Copy the folder structure only, excluding all files

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            replica_file_path = file_path.replace(folder_path, replica_folder_path)

            size = os.path.getsize(file_path)
            tokens = 0
            content = read_file_if_not_image(file_path)
            if content != None:
                tokens = tokenize(content)

            # Create a blank file in the replica folder
            if not imgTF(file_path):
                with open(replica_file_path, "w", encoding="utf-8") as f:
                    pass

            directory_map[file_path] = {"size": size, "tokens": tokens, 'image': imgTF(file_path)}
    print(json.dumps(directory_map, indent=2))
    return directory_map


if __name__ == "__main__":
    folder_path = '/home/fresh1/Desktop/New Folder/saveConvoReact/react-chat/src'#input("Enter the path to the folder: ")
    process_files(folder_path,chooseInit(folder_path))
