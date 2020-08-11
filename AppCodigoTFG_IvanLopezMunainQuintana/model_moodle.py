
# Author: Ivan Lopez de Munain Quintana
# Date: Feb-Jul, 2020


import xmltodict
import json
import collections
import io
import os
import requests
import csv
import glob
import numpy as np

#============================================================================
#========================== CLASS MOODLE ====================================
#============================================================================

#Allows to connect with the moodle API and use the web services to extract data 

class MDL:
    
    """ 
    Main class to connect Moodle webservice
    More information about Webservice:
        http://docs.moodle.org/20/en/Web_Services_API
        http://docs.moodle.org/dev/Web_services
        http://docs.moodle.org/dev/Creating_a_web_service_client
        http://docs.moodle.org/dev/Web_services_Roadmap#Web_service_functions

    Moodle Connection Methods available: REST
    Others methods: XML-RPC, SOAP, AMF Protocols, etc
    """


    """
    Connection to Moodle with REST Webservice
    Input:
        server = {
            'protocol': 'rest',
            'uri': 'http://www.mymoodle.org',
            'token': 'my_token_key_access',
        }
        function = webservice
    Output: string with the final request url
    """
    def conn_rest(self, server, function):

        if 'uri' not in server or 'token' not in server:
            return False

        if server['uri'][-1] == '/':
            server['uri'] = server['uri'][:-1]

        url = '%s/webservice/%s/server.php' % (server['uri'], server['protocol'])
        data = 'wstoken=%s&wsfunction=%s' % (server['token'], function)
        urlFinal = url+'?'+data
        result = requests.post(urlFinal)
        return result


    """
    Construct the correct function to call
    Input:
        server = {
            'protocol': 'rest',
            'uri': 'http://www.mymoodle.org',
            'token': 'my_token_key_access',
        }
        function = webservice
        params = parameters to search data
        key_word = key words to extract information through web services
    Output:  call to conn_rest (passing the string with part of the final request url)
    """
    def rest_protocol(self, server, params, function=None, key_word=None):

        if function is None:
            function = ""
        if key_word is None:
            key_word = ""
        count = 0
        for param in params:
            #if type(param) is dict:
            #for item in iter(param):
            if key_word =="":
                function+= '&%s=' % (param)
                function += '%s' % params[param]
            else:
                function += '&%s[0][%s]=' % (key_word, param)
                function += '%s' % params[param]
            #else:
                #function += '&%s[%s]=' % (key_word, str(count))
                #function += '%s' % param
            count += 1

        return self.conn_rest(server, function)

    """
    Get all courses
    Input:
        server = {
            'protocol': 'rest',
            'uri': 'http://www.mymoodle.org',
            'token': 'mytokenkey',
        }
    Output:
        rest protocol:      xml file format
    """
    def get_courses(self, server):

        if 'protocol' not in server:
            return False
        params=''
        function = 'core_course_get_courses'
        key_word = ''
        protocol = {
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function)



    """
    Create new course
    Dont use in the app
    Input:
        server = {
            'protocol': 'rest',
            'uri': 'http://www.mymoodle.org',
            'token': 'mytokenkey',
        }
        params = input a list of dictionaries of pairs key-value 
    Output:
        rest protocol:      xml file format
    """
    def create_courses(self, server, params):
        if 'protocol' not in server:
            return False
        function = 'core_course_create_courses'
        key_word = 'courses'
        protocol = {
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function, key_word)
        
    """
    Get course modules
    Input:
        server = {
            'protocol': 'rest',
            'uri': 'http://www.mymoodle.org',
            'token': 'mytokenkey',
        }
        params = input dictionary with pais key-value
    Output:
        rest protocol:      xml file format
    """

    def get_courses_module(self, server, params):
        if 'protocol' not in server:
            return False
        function = 'core_course_get_course_module'
        key_word = ''
        protocol = {
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function, key_word)


    """
    Get course content
    Input:
        server = {
            'protocol': 'rest',
            'uri': 'http://www.mymoodle.org',
            'token': 'mytokenkey',
        }
        params = input dictionary with pais key-value
    Output:
        rest protocol:      xml file format
    """
    def get_courses_content(self, server, params):
        if 'protocol' not in server:
            return False
        function = 'core_course_get_contents'
        key_word = ''
        protocol = {
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function, key_word)


    """
    Get users
    Input:
        server = {
            'protocol': 'rest',
            'uri': 'http://www.mymoodle.org',
            'token': 'mytokenkey',
        }
        params = [{  
            'key': 'key to search: firstname, username, etc'
            'value: 'value of the key'
        }]
    Output:
        rest protocol:      xml file format
    """
    def get_users(self, server, params):
        if 'protocol' not in server:
            return False
        function = 'core_user_get_users'
        key_word = 'criteria'
        protocol = {
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function, key_word)

    """
    Get users
    Input:
        server = {
            'protocol': 'rest',
            'uri': 'http://www.mymoodle.org',
            'token': 'mytokenkey',
        }
        params = input a dictionary with pairs key-value
    Output:
        rest protocol:      xml file format
    """
    def get_enroll_users(self, server, params):
        if 'protocol' not in server:
            return False
        function = 'core_enrol_get_enrolled_users'
        key_word = ''
        protocol = {
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function, key_word)


    """
    Create new user
    Dont use in the app
    Input:
        server = {
            'protocol': 'rest',
            'uri': 'http://www.mymoodle.org',
            'token': 'mytokenkey',
        }
        params = [{                      # Input a list of dictionaries
            'username': username,        # Required & unique
            'password': password,
            'firstname': firstname,
            'lastname': lastname,
            'email': email,
        }]
    Output:
        rest protocol:      xml file format
    """
    def create_users(self, server, params):
        if 'protocol' not in server:
            return False
        function = 'core_user_create_users'
        key_word = 'users'
        protocol = {
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function, key_word)



    """
    Get forums by course
    Input:
        server = {
            'protocol': 'rest',
            'uri': 'http://www.mymoodle.org',
            'token': 'mytokenkey',
        }
        params = pair key-value, ID course
    Output:
        rest protocol:      xml file format
    """    
    def get_forums_by_course(self, server, params):

        if 'protocol' not in server:
            return False
        function = 'mod_forum_get_forums_by_courses'
        key_word = ''
        protocol = {
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function, key_word)
    

    """
    Get labels by course
    Input:
        server = {
            'protocol': 'rest',
            'uri': 'http://www.mymoodle.org',
            'token': 'mytokenkey',
        }
        params = pair key-value, ID course
    Output:
        rest protocol:      xml file format
    """ 
    def get_labels_by_course(self, server, params):

        if 'protocol' not in server:
            return False
        function = 'mod_label_get_labels_by_courses'
        key_word = ''
        protocol = {
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function, key_word)

    """
    Get workshops by course
    Input:
        server = {
            'protocol': 'rest',
            'uri': 'http://www.mymoodle.org',
            'token': 'mytokenkey',
        }
        params = pair key-value, ID course
    Output:
        rest protocol:      xml file format
    """  
    def get_workshops_by_course(self, server, params):

        if 'protocol' not in server:
            return False
        function = 'mod_workshop_get_workshops_by_courses'
        key_word = ''
        protocol = {
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function, key_word)

    """
    Get wikis by course
    Input:
        server = {
            'protocol': 'rest',
            'uri': 'http://www.mymoodle.org',
            'token': 'mytokenkey',
        }
        params = pair key-value, ID course
    Output:
        rest protocol:      xml file format
    """ 
    def get_wikis_by_course(self, server, params):

        if 'protocol' not in server:
            return False
        function = 'mod_wiki_get_wikis_by_courses'
        key_word = ''
        protocol = {
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function, key_word)

    """
    Get choices by course
    Input:
        server = {
            'protocol': 'rest',
            'uri': 'http://www.mymoodle.org',
            'token': 'mytokenkey',
        }
        params = pair key-value, ID course
    Output:
        rest protocol:      xml file format
    """ 
    def get_choices_by_course(self, server, params):

        if 'protocol' not in server:
            return False
        function = 'mod_choice_get_choices_by_courses'
        key_word = ''
        protocol = {
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function, key_word)

    """
    Get database by course
    Input:
        server = {
            'protocol': 'rest',
            'uri': 'http://www.mymoodle.org',
            'token': 'mytokenkey',
        }
        params = pair key-value, ID course
    Output:
        rest protocol:      xml file format
    """ 
    def get_database_by_course(self, server, params):

        if 'protocol' not in server:
            return False
        function = 'mod_data_get_databases_by_courses'
        key_word = ''
        protocol = {
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function, key_word)

    """
    Get folders by course
    Input:
        server = {
            'protocol': 'rest',
            'uri': 'http://www.mymoodle.org',
            'token': 'mytokenkey',
        }
        params = pair key-value, ID course
    Output:
        rest protocol:      xml file format
    """ 
    def get_folders_by_course(self, server, params):

        if 'protocol' not in server:
            return False
        function = 'mod_folder_get_folders_by_courses'
        key_word = ''
        protocol = {
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function, key_word)

    """
    Get glosarries by course
    Input:
        server = {
            'protocol': 'rest',
            'uri': 'http://www.mymoodle.org',
            'token': 'mytokenkey',
        }
        params = pair key-value, ID course
    Output:
        rest protocol:      xml file format
    """ 
    def get_glossaries_by_course(self, server, params):

        if 'protocol' not in server:
            return False
        function = 'mod_glossary_get_glossaries_by_courses'
        key_word = ''
        protocol = {
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function, key_word)
    

    """
    Get quizz by course
    Input:
        server = {
            'protocol': 'rest',
            'uri': 'http://www.mymoodle.org',
            'token': 'mytokenkey',
        }
        params = pair key-value, ID course
    Output:
        rest protocol:      xml file format
    """ 
    def get_quizz_by_course(self, server, params):

        if 'protocol' not in server:
            return False
        function = 'mod_quiz_get_quizzes_by_courses'
        key_word = ''
        protocol = {
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function, key_word)

    """
    Get url by course
    Input:
        server = {
            'protocol': 'rest',
            'uri': 'http://www.mymoodle.org',
            'token': 'mytokenkey',
        }
        params = pair key-value, ID course
    Output:
        rest protocol:      xml file format
    """ 
    def get_url_by_course(self, server, params):

        if 'protocol' not in server:
            return False
        function = 'mod_url_get_urls_by_courses'
        key_word = ''
        protocol = {
            "rest": self.rest_protocol,
        }
        return protocol[server['protocol']](server, params, function, key_word)







#===============================================================================
#========================  AUXILIAR METHODS ====================================
#===============================================================================


"""
Find all occurrences of a letter
Input:
    s:string
    ch=letter
Output:
    the ocurrences
""" 
def findOccurrences_letter(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]


"""
all occurrences of a substring
Input:
    a_str:string
    sub=substring
Output:
    the ocurrences
""" 
def find_all_substring(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1: return
        yield start
        start += len(sub)

"""
Get number of elements in a nested list
Input:
    listOfElem:list
Output:
    int of the count
""" 
def getSizeOfNestedList(listOfElem):
    count = 0
    # Iterate over the list
    if isinstance(listOfElem,list):
        for elem in listOfElem:
            # Check if type of element is list
            if isinstance(elem,list):  
                # Again call this function to get the size of this element
                count += getSizeOfNestedList(elem)
            elif isinstance(elem,dict):
                count += getSizeOfNestedList(elem)
    if isinstance(listOfElem,dict):
        for k,v in listOfElem.items():
            if isinstance(v,list):
                count+=getSizeOfNestedList(v)
            elif isinstance(v,dict):
                count += getSizeOfNestedList(v)
            elif isinstance(v,str) or isinstance(v,int):
                count+=1

    return count


'''
Convert XML to a string, recursively saving in the global variable cadena
Input:
    xpars2: response xml of the request
    flag: flag 

'''
def convertXML_to_String(xpars2, flag):

    camposMultiples = [
        #fields multiples in users
        "preferences", "warnings",
        #fields multiples in courses
        "courseformatoptions",  "customfields",
        #fields multiples in contents course
        "mimetypes", "tags",  #"modules" , # " contents ",
        ]

    global cadena
    global num_glob
    global contador_aux

    if isinstance(xpars2,dict):
        for w in range(len(list(xpars2))):
            if isinstance(xpars2[list(xpars2)[w]],str):
                if any(camp in xpars2[list(xpars2)[w]] for camp in camposMultiples):
                    num_glob = getSizeOfNestedList(xpars2['MULTIPLE'])
                    flag=1
                cadena += str(' ') + str(xpars2[list(xpars2)[w]] + " ; ")
            else:
                convertXML_to_String(xpars2[list(xpars2)[w]],flag)
            
            if xpars2[list(xpars2)[w]] is None:
                cadena += str(" None ;")

        if flag==1:
            contador_aux=contador_aux+1
        
        if flag==0 or contador_aux>(num_glob-1):
            contador_aux=0
            cadena += str("\n ")

        flag=0
    elif isinstance(xpars2,list):
        for a in range(len(xpars2)):
            convertXML_to_String(xpars2[a],flag)


'''
Saving the data in a csv file
Input:
    cadena:string to save
    type_info: string showing the type of information
'''
def save_data(cadena, type_info):

    dicc_ident={
        "User": "username",
        "Course": "shortname",
        "Course_Content": "name",
        "Forum": "name",
        "Wiki" : "name",
    }

    info = list(find_all_substring(cadena, " id ;"))

    for j in range(len(info)):
        
        if j==(len(info)-1):
            s = io.StringIO("Feature; Value; \n" + cadena[info[j]:])
            aux1= cadena[info[j]:]
            aux1=aux1[(aux1.find("id")+4):]
            aux2= cadena[info[j]:]
            aux2=aux2[( aux2.find(dicc_ident[type_info]) + len(dicc_ident[type_info]) + 2 ):]
            identificator= str("_id_" + aux1[1:(aux1.find(";")-1)] + "_" + str(dicc_ident[type_info]) + "_" + aux2[1:(aux2.find(";")-1)]) 

        else:
            s = io.StringIO( "Feature; Value; \n" + cadena[info[j]:info[j+1]])
            aux1= cadena[info[j]:info[j+1]]
            aux1=aux1[(aux1.find("id")+4):]
            aux2= cadena[info[j]:info[j+1]]
            aux2=aux2[( aux2.find(dicc_ident[type_info]) + len(dicc_ident[type_info]) + 2 ):]
            identificator= str("_id_" + aux1[1:(aux1.find(";")-1)] + "_" + str(dicc_ident[type_info]) + "_" + aux2[1:(aux2.find(";")-1)]) 

        identificator = identificator.replace(":","-")
        identificator = identificator.replace("/","-")
        identificator = identificator.replace(" ","_")
        identificator = identificator.replace(";","-")

        if not os.path.isdir("Download"):
            os.mkdir("Download")
        
        if not os.path.isdir("Download/researcher"):
            os.mkdir("Download/researcher")

        if not os.path.isdir("Download/researcher/" + str(type_info)):
            os.mkdir("Download/researcher/" + str(type_info))

        with open("Download/researcher/" + str(type_info) + '/' + str(type_info) + str(identificator) + '.csv', 'w') as f:
            for line in s:
                if not line in ['\n',' \n', '\r\n']:
                    if line.count(";")==1:
                        line = line[0:(len(line)-1)] + "null; \n"
                        f.write(line)
                    elif line.count(";")>2:
                        aux = findOccurrences_letter(line,";")
                        line = line[:aux[0]] + "; (" + line[(aux[0]+1):]
                        line = line[:(aux[len(aux)-1]+2)] + ");" + line[(aux[len(aux)-1]+3):]
                        for i in range(1,len(aux)-1):
                            if i%2==0:
                                line = line[:(aux[i]+2)] + "/" + line[(aux[i]+3):] 
                            else:
                                line = line[:(aux[i]+2)] + ":" + line[(aux[i]+3):]
                        f.write(line)
                    else:                          
                        f.write(line)
            f.close() 


'''
Transform the string with the response XML into a list
Input:
    cadena: string with the response
    type_info: string showing the type of information
Output:
    tupple-> [list with the response, int with the num of items of the response]
'''
def write_array(cadena, type_info):
    
    dicc_ident={
        "User": "username",
        "Course": "shortname",
        "Course_Content": "name",
        "Forum": "name",
        "Wiki": "name",
    }
    
    info = list(find_all_substring(cadena, " id ;"))

    lista=np.frompyfunc(list, 0, 1)(np.empty((len(info)), dtype=object)) 

    for j in range(len(info)):
        
        if j==(len(info)-1):
            s = io.StringIO( cadena[info[j]:])
            aux1= cadena[info[j]:]
            aux1=aux1[(aux1.find("id")+4):]
            aux2= cadena[info[j]:]
            aux2=aux2[( aux2.find(dicc_ident[type_info]) + len(dicc_ident[type_info]) + 2 ):]
            identificator= str("_id_" + aux1[1:(aux1.find(";")-1)] + "_" + str(dicc_ident[type_info]) + "_" + aux2[1:(aux2.find(";")-1)]) 

        else:

            s = io.StringIO(  cadena[info[j]:info[j+1]])
            aux1= cadena[info[j]:info[j+1]]
            aux1=aux1[(aux1.find("id")+4):]
            aux2= cadena[info[j]:info[j+1]]
            aux2=aux2[( aux2.find(dicc_ident[type_info]) + len(dicc_ident[type_info]) + 2 ):]
            identificator= str("_id_" + aux1[1:(aux1.find(";")-1)] + "_" + str(dicc_ident[type_info]) + "_" + aux2[1:(aux2.find(";")-1)]) 


        identificator = identificator.replace(":","-")
        identificator = identificator.replace("/","-")
        identificator = identificator.replace(" ","_")
        identificator = identificator.replace(",","-")

        for line in s:
            if not line in ['\n',' \n', '\r\n']:
                if line.count(";")==1:
                    line = line[0:(len(line)-1)] + "null; \n"
                    line= line.replace("\n","")
                    lista[j].append(line.split(";")[0:2])

                elif line.count(";")>2:
                    aux = findOccurrences_letter(line,";")
                    line = line[:aux[0]] + "; (" + line[(aux[0]+1):]
                    line = line[:(aux[len(aux)-1]+2)] + ");" + line[(aux[len(aux)-1]+3):]
                    for i in range(1,len(aux)-1):
                        if i%2==0:
                            line = line[:(aux[i]+2)] + "/" + line[(aux[i]+3):] 
                        else:
                            line = line[:(aux[i]+2)] + ":" + line[(aux[i]+3):]
                    line= line.replace("\n","")
                    lista[j].append(line.split(";")[0:2])

                else:
                    line= line.replace("\n","")
                    lista[j].append(line.split(";")[0:2])                        

    num_items=list(range(len(info)))

    return (lista, num_items)


'''
Extract information from a list
Input:
    lista: list
    info: the identificator of the info
Output:
    list with the info
'''
def  extract_info(lista,info):
    aux_lista = []
    for enum in lista:  
        for ind in enum:
            for w in ind:
                if info in w and not("New Site" in ind[1]):
                    aux_lista.append(ind[1])

    return aux_lista

'''
Extract info of a determined course 
Input:
    lista: list with the info of the course
    name: name of the info desired
Output:
    list with the info
'''
def extract_course_detail(lista, name):
    aux_lista=[]
    for enum in lista:
        for ind in enum:
            for w in ind:
                if name in w:
                    aux_lista.append(enum)
                    break
            if len(aux_lista)==1:
                break
        if len(aux_lista)==1:
                break
    return aux_lista


'''
Extract resource/modules of a determined course 
Input:
    lista: list with the info of the course
Output:
    list with the info
'''
def extract_course_resource_modules(lista):
    flag=0
    aux_lista=[]
    for enum in lista:
        aux = auxiliar_extract_course_resource_modules(enum)
        for ind in enum:
            for w in ind:
                if " name " in w:
                    if flag==0 or aux:
                        aux_lista.append(["Module", ind[1]])
                    else:
                        aux_lista.append(["Resource",ind[1]])
                if " modules " in w and "null" in ind[1]:
                    flag=1
    return aux_lista


'''
Auxiliar to extract resource/modules of a determined course 
Input:
    lista: list with the info of the course
Output:
    boolean
'''
def auxiliar_extract_course_resource_modules(lista_aux):
    boolean = False
    for ind_aux in lista_aux:
        for w_aux in ind_aux:
            if " modules " in w_aux:
                boolean = True
                break
    
    return boolean
                

