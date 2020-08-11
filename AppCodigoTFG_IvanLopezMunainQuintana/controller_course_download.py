# Author: Ivan Lopez de Munain Quintana
# Date: Feb-Jul, 2020

import model_moodle, model_moodle_WebScrapping
import os, webbrowser, xmltodict, json, collections, io, os, requests, csv, glob
import numpy as np
import http.cookiejar as cookielib
from bs4 import BeautifulSoup as bs
import cgi, mechanize, os, getpass, argparse, shutil, io, openpyxl, threading, time
from pathlib import Path


'''
Thread to launch the browser Chrome to visualize the dashboard. Sleep 15 seconds to allow execute the aplication in R
'''
def launch_browser():
    time.sleep(15)
    #chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
    #webbrowser.get(chrome_path).open('http://127.0.0.1:5001/')
    os.system('cmd /c' + "start chrome http://127.0.0.1:5001/")

'''
Thread to execute the aplication in R.
Input:
    arg: string with the name of the script R
    arg2: string with the arguments (names of the files with the data)
'''
def execute_command(arg, arg2, route_to_rscript):
    aux = "C:/Program Files/R/" + str(route_to_rscript) + "/bin/Rscript.exe"
    command = '"' + aux +  '"'
    cfinal = command + " --vanilla integration.R " + str(arg) + " " + str(arg2)
    os.system('cmd /c' + cfinal)



'''
Controller asociated to download data in investigator mode
Input:
    server: token access, uri and protocol
    parameters: filters to search data in the API
    down: download the data or not
    list_course_ids: ids of the courses asociated to the user
    request_args: query strings of the request
    dicc_anonim: correspondences id_moodle-id_anonim
    dicc_fullname: correspondences fullname-id_anonim
    table_anonim: all correspondences
    user: moodle username
    passwd: moodle password
    url_login: url to login moodle
Output:
    pack: dictionary with the data of the request
'''
def investigator_mode(server, parameters, down, list_course_ids, request_args,dicc_anonim,dicc_fullname,table_anonim,user,password, url_login):

    pack = {"error":"no"}
    mdl = model_moodle.MDL()

    try:
        data=[]
        data_keys=[]
        data_type=[]

        
        arg_keys = list(request_args.keys())

        #download all the information
        if "All_download" in arg_keys[0]:
            
            #download logs
            for c in range(len(list_course_ids)):
                data = model_moodle_WebScrapping.web_scrapping_moodle(list_course_ids[c] , user_id="", modulo_id="", modaction="All_actions", edu_level="All_events",one_tab="down", data_type="Logs", dicc_anonim= dicc_anonim, dicc_fullname= dicc_fullname, table_anonim=table_anonim,
                                                                        user=user, passwd=password, BASE_URL=url_login, mode="investigator")
            #download forums
            for c in range(len(list_course_ids)):

                data_type="Forum"
                data_keys = ["Feature", "Value"]
                index=0
                course_id = list_course_ids[c]
                parameters={
                    'courseids[0]':str(course_id)
                }

                res = mdl.get_forums_by_course(server,parameters)
                xpars2 = xmltodict.parse(res.text)
                model_moodle.cadena=""
                model_moodle.convertXML_to_String(xpars2,0)
                model_moodle.save_data(model_moodle.cadena, data_type)
            
            #download wikis
            for c in range(len(list_course_ids)):

                data_type="Wiki"
                data_keys = ["Feature", "Value"]
                index=0
                course_id = list_course_ids[c]
                parameters={
                    'courseids[0]':str(course_id)
                }

                res = mdl.get_wikis_by_course(server,parameters)
                xpars2 = xmltodict.parse(res.text)
                model_moodle.cadena=""
                model_moodle.convertXML_to_String(xpars2,0)
                model_moodle.save_data(model_moodle.cadena, data_type)

            pack.update({"data":None})

        #download only users info
        elif "Users_" in arg_keys[0]:
            data_keys=["Feature", "Value"]
            data_type="User"
            parameters = {
                'key': str(request_args["Users_key_user"]),
                'value' :  str(request_args["Users_value_user"])
            }

            for i in range(len(arg_keys)):
                if "User_selection" in arg_keys[i]:
                    index = int(request_args["User_selection"])
                    break
                else:
                    index=0
            
            for i in range(len(arg_keys)):
                if "download" in arg_keys[i]:
                    down = request_args['download']
                    break
                else:
                    down = None

            res = mdl.get_users(server, parameters)
            xpars2 = xmltodict.parse(res.text)
            model_moodle.cadena=""
            model_moodle.convertXML_to_String(xpars2,0)
            data = model_moodle.write_array(model_moodle.cadena, data_type)


            if data[0][index]=="":
                raise Exception
            
            if down != None:
                model_moodle.cadena=""
                model_moodle.convertXML_to_String(xpars2,0)
                model_moodle.save_data(model_moodle.cadena, data_type)
            
            pack.update({"data":data})
            pack.update({"data_keys":data_keys})
            pack.update({"data_type":data_type})
            pack.update({"index":index})

        #download only logs and grades
        elif "Log_Course_ID" in arg_keys[0]:
            course_id = request_args["Log_Course_ID"]
            user_id = request_args["Log_User_ID"]
            module_id = request_args["Log_Module_ID"]
            action_select = request_args["Log_Action_select"]
            event_select = request_args["Log_Event_select"]

            for i in range(len(arg_keys)):
                if "download" in arg_keys[i]:
                    down = request_args['download']
                    break
                else:
                    down=None


            data_type = "Logs"
            data = model_moodle_WebScrapping.web_scrapping_moodle(course_id, user_id, module_id, action_select, event_select,down, data_type, dicc_anonim, dicc_fullname,table_anonim, user, password, url_login, "investigator")
            index= None
            data_keys = data.pop(0)
            if len(data)>200:
                data = data[0:200]
            
            pack.update({"data":data})
            pack.update({"data_keys":data_keys})
            pack.update({"data_type":data_type})
            pack.update({"index":index})

        #download only forums
        elif "Forum_" in arg_keys[0]:
            
            data_type="Forum"
            data_keys = ["Feature", "Value"]
            index=0
            course_id = request_args['Forum_Course_ID']

            for i in range(len(arg_keys)):
                if "Forum_selection" in arg_keys[i]:
                    index= int(request_args["Forum_selection"])
                    break
                else:
                    index=0

            for i in range(len(arg_keys)):
                if "download" in arg_keys[i]:
                    down = request_args['download']
                    break
                else:
                    down = None

            parameters={
                'courseids[0]':str(course_id)
            }

            res = mdl.get_forums_by_course(server,parameters)
            xpars2 = xmltodict.parse(res.text)
            model_moodle.cadena=""
            model_moodle.convertXML_to_String(xpars2,0)
            data = model_moodle.write_array(model_moodle.cadena, data_type)

            if data[0][index]=="":
                raise Exception
            
            if down != None:
                model_moodle.cadena=""
                model_moodle.convertXML_to_String(xpars2,0)
                model_moodle.save_data(model_moodle.cadena, data_type)
            
            pack.update({"data":data})
            pack.update({"data_keys":data_keys})
            pack.update({"data_type":data_type})
            pack.update({"index":index})

        #download only wikis
        elif "Wiki_" in arg_keys[0]:
            
            data_type="Wiki"
            data_keys = ["Feature", "Value"]
            index=0
            course_id = request_args['Wiki_Course_ID']

            for i in range(len(arg_keys)):
                if "Wiki_selection" in arg_keys[i]:
                    index= int(request_args["Wiki_selection"])
                    break
                else:
                    index=0

            for i in range(len(arg_keys)):
                if "download" in arg_keys[i]:
                    down = request_args['download']
                    break
                else:
                    down = None

            parameters={
                'courseids[0]':str(course_id)
            }

            res = mdl.get_wikis_by_course(server,parameters)
            xpars2 = xmltodict.parse(res.text)
            model_moodle.cadena=""
            model_moodle.convertXML_to_String(xpars2,0)
            data = model_moodle.write_array(model_moodle.cadena, data_type)

            if data[0][index]=="":
                raise Exception
            
            if down != None:
                model_moodle.cadena=""
                model_moodle.convertXML_to_String(xpars2,0)
                model_moodle.save_data(model_moodle.cadena, data_type)
            
            pack.update({"data":data})
            pack.update({"data_keys":data_keys})
            pack.update({"data_type":data_type})
            pack.update({"index":index})

    except:
        pack.update({"error":"yes"})

    return pack



'''
Controller asociated to download data in teacher mode
Input:
    down: download the data or not
    list_course_ids: ids of the courses asociated to the user
    request_args: query strings of the request
    dicc_anonim: correspondences id_moodle-id_anonim
    dicc_fullname: correspondences fullname-id_anonim
    table_anonim: all correspondences
    user: moodle username
    passwd: moodle password
    url_login: url to login moodle
Output:
    pack: dictionary with the data of the request
'''
def teacher_mode(down,list_course_ids,request_args,dicc_anonim,dicc_fullname,table_anonim,user,password, url_login,route_to_rscript):

    pack = {"error":"no"}

    try:
        data=[]
        data_keys=[]
        data_type=[]

        arg_keys = list(request_args.keys())

        #download logs and grades
        if "Log_Course_ID" in arg_keys[0]:
            course_id = request_args["Log_Course_ID"]
            user_id = request_args["Log_User_ID"]
            module_id = request_args["Log_Module_ID"]
            action_select = request_args["Log_Action_select"]
            event_select = request_args["Log_Event_select"]

            for i in range(len(arg_keys)):
                if "download" in arg_keys[i]:
                    down = request_args['download']
                    break
                else:
                    down=None

            data_type = "Logs"
            data = model_moodle_WebScrapping.web_scrapping_moodle(course_id, user_id, module_id, action_select, event_select,down, data_type, dicc_anonim, dicc_fullname, table_anonim, user, password, url_login,"teacher")
            if down=="down":
                arg = data[1]
                arg2 = data[2]
                data=data[0]

                #threads to launch the browser and execute the R aplication (dashboard)
                t1 = threading.Thread(target=launch_browser)  
                t2 = threading.Thread(target=execute_command, args = (arg,arg2,route_to_rscript))  
                t1.start()
                t2.start()
            
    
            index= None
            data_keys = data.pop(0)
            if len(data)>200:
                data = data[0:200]
            
            pack.update({"data":data})
            pack.update({"data_keys":data_keys})
            pack.update({"data_type":data_type})
            pack.update({"index":index})

    
    except:
        pack.update({"error":"yes"})
    
    return pack