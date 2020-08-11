# Author: Ivan Lopez de Munain Quintana
# Date: Feb-Jul, 2020

import model_moodle, xmltodict, json, collections, io, os, requests, csv, glob

'''
Get all the courses asociated to the user through the API
Input:
    server: token access, uri and protocol to access Moodle API
    data_keys: names of the columns of the data
    data_type: type of information
    index: to check if the search has more than one result
Output:
    aux_data: array with the id and name of the courses
'''
def obtain_all_courses(server,data_keys,data_type,index):

    mdl = model_moodle.MDL()
    res = mdl.get_courses(server)
    xpars2 = xmltodict.parse(res.text)
    model_moodle.cadena=""
    model_moodle.convertXML_to_String(xpars2,0)
    data = model_moodle.write_array(model_moodle.cadena, data_type)
    aux_data = model_moodle.extract_info(data[0],"fullname")
    aux_id = model_moodle.extract_info(data[0]," id ")
    for i in range(len(aux_data)):
        aux_data[i] = "ID:" + aux_id[i+1].replace(" ","") + aux_data[i]

    return aux_data
