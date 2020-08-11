# Author: Ivan Lopez de Munain Quintana
# Date: Feb-Jul, 2020

import model_moodle, xmltodict, json, collections, io, os, requests, csv, glob

'''
Controller to get the course details through the Moodle API in investigator mode 
Input:
    server: token access, uri and protocol to access Moodle API
    data_keys: names of the columns of the data
    data_type: type of information
    index: to check if the search has more than one result
    course_view: id of the course
Output:
    results: dictionary with the data
'''
def get_course_detail(server, data_keys, data_type, index, course_view):

    results={}

    mdl = model_moodle.MDL()
    res = mdl.get_courses(server)
    xpars2 = xmltodict.parse(res.text)
    model_moodle.cadena=""
    model_moodle.convertXML_to_String(xpars2,0)
    data = model_moodle.write_array(model_moodle.cadena, data_type)

    # extract details course
    course_detail = model_moodle.extract_course_detail(data[0],str(course_view))
    results.update({'course_detail':course_detail})


    #extract users enrolled by course id
    course_id=''
    for enum in course_detail[0]:
        for ind in enum:
            if "id" in ind:
                course_id = int(enum[1])
                break
        if course_id!="":
            break

    aux={'courseid':str(course_id)}
    res = mdl.get_enroll_users(server,aux)
    xpars2 = xmltodict.parse(res.text)
    model_moodle.cadena=""
    model_moodle.convertXML_to_String(xpars2,0)
    try:
        data = model_moodle.write_array(model_moodle.cadena, data_type)
        course_users_name = model_moodle.extract_info(data[0],"firstname")
        course_users_lastname = model_moodle.extract_info(data[0],"lastname")
        course_users_email = model_moodle.extract_info(data[0],"email")
    except:
        course_users_name = ["Sin usuarios"]
        course_users_lastname = ["Sin usuarios"]
        course_users_email = ["Sin usuarios"]
    
    course_users_data = []

    for ind in range(len(course_users_name)):
        course_users_data.append([course_users_name[ind],course_users_lastname[ind],course_users_email[ind]])
    
    results.update({'course_users_data':course_users_data})
    

    # extract modules and resources
    try:
        aux={'courseid':str(course_id)}
        res = mdl.get_courses_content(server,aux)
        xpars2 = xmltodict.parse(res.text)
        model_moodle.cadena=""
        model_moodle.convertXML_to_String(xpars2,0)
        data = model_moodle.write_array(model_moodle.cadena, data_type)
        aux_types = model_moodle.extract_info(data[0],"modname")
        course_content = model_moodle.extract_course_resource_modules(data[0])
        contador_type=0
        for j in range(len(course_content)):
            for i in range(len(enum)):
                if course_content[j][i]=="Resource":
                    course_content[j][i]=aux_types[contador_type]
                    contador_type+=1
        
        contador_type=0
        flag_type=True
        aux_types = model_moodle.extract_info(data[0],"author")
        for j in range(len(course_content)):
            for i in range(len(enum)):
                if "resource" in course_content[j][i]:
                    flag_type=False
                    course_content[j].append(aux_types[contador_type])
                    contador_type+=1
                    break
            if flag_type:
                course_content[j].append("-")
            else:
                flag_type=True
    except:
        course_content.append(["-","-","-"])
    
    results.update({'course_content':course_content})
    
    # extract forums
    try:
        course_forum=[]
        aux={'courseids[0]': str(course_id)}
        res = mdl.get_forums_by_course(server,aux)
        xpars2 = xmltodict.parse(res.text)
        model_moodle.cadena=""
        model_moodle.convertXML_to_String(xpars2,0)
        data = model_moodle.write_array(model_moodle.cadena, data_type)
        aux_forum1 = model_moodle.extract_info(data[0]," id ")
        aux_forum2 = model_moodle.extract_info(data[0]," course ")
        aux_forum3 = model_moodle.extract_info(data[0]," type ")
        aux_forum4 = model_moodle.extract_info(data[0]," name ")
        for i in range(len(aux_forum1)):
            course_forum.append([aux_forum1[i],aux_forum2[i],aux_forum3[i],aux_forum4[i]])
        results.update({'course_forum':course_forum})
    except:
        pass
    
    # extract labels
    try:
        course_label=[]
        aux={'courseids[0]': str(course_id)}
        res = mdl.get_labels_by_course(server,aux)
        xpars2 = xmltodict.parse(res.text)
        model_moodle.cadena=""
        model_moodle.convertXML_to_String(xpars2,0)
        data = model_moodle.write_array(model_moodle.cadena, data_type)
        aux_label1 = model_moodle.extract_info(data[0]," id ")
        aux_label2 = model_moodle.extract_info(data[0]," coursemodule ")
        aux_label3 = model_moodle.extract_info(data[0]," course ")
        aux_label4 = model_moodle.extract_info(data[0]," name ")
        for i in range(len(aux_label1)):
            course_label.append([aux_label1[i],aux_label2[i],aux_label3[i],aux_label4[i]])
        results.update({'course_label':course_label})
    except:
        pass
    

    # extract workshops
    
    try:
        course_workshop=[]
        aux={'courseids[0]': str(course_id)}
        res = mdl.get_workshops_by_course(server,aux)
        xpars2 = xmltodict.parse(res.text)
        model_moodle.cadena=""
        model_moodle.convertXML_to_String(xpars2,0)
        data = model_moodle.write_array(model_moodle.cadena, data_type)
        aux_workshop1 = model_moodle.extract_info(data[0]," id ")
        aux_workshop2 = model_moodle.extract_info(data[0]," course ")
        aux_workshop3 = model_moodle.extract_info(data[0]," name ")
        for i in range(len(aux_workshop1)):
            course_workshop.append([aux_workshop1[i],aux_workshop2[i],aux_workshop3[i]])
        results.update({'course_workshop':course_workshop})
    except:
        pass
    

    # extract labels
    
    try:
        course_wiki=[]
        aux={'courseids[0]': str(course_id)}
        res = mdl.get_wikis_by_course(server,aux)
        xpars2 = xmltodict.parse(res.text)
        model_moodle.cadena=""
        model_moodle.convertXML_to_String(xpars2,0)
        data = model_moodle.write_array(model_moodle.cadena, data_type)
        aux_wiki1 = model_moodle.extract_info(data[0]," id ")
        aux_wiki2 = model_moodle.extract_info(data[0]," coursemodule ")
        aux_wiki3 = model_moodle.extract_info(data[0]," course ")
        aux_wiki4 = model_moodle.extract_info(data[0]," name ")
        for i in range(len(aux_wiki1)):
            course_wiki.append([aux_wiki1[i],aux_wiki2[i],aux_wiki3[i],aux_wiki4[i]])
        results.update({'course_wiki':course_wiki})

    except:
        pass 
    
    # extract choices
    
    try:
        course_choice=[]
        aux={'courseids[0]': str(course_id)}
        res = mdl.get_choices_by_course(server,aux)
        xpars2 = xmltodict.parse(res.text)
        model_moodle.cadena=""
        model_moodle.convertXML_to_String(xpars2,0)
        data = model_moodle.write_array(model_moodle.cadena, data_type)
        aux_choice1 = model_moodle.extract_info(data[0]," id ")
        aux_choice2 = model_moodle.extract_info(data[0]," coursemodule ")
        aux_choice3 = model_moodle.extract_info(data[0]," course ")
        aux_choice4 = model_moodle.extract_info(data[0]," name ")
        for i in range(len(aux_choice1)):
            course_choice.append([aux_choice1[i],aux_choice2[i],aux_choice3[i],aux_choice4[i]])
        results.update({'course_choice':course_choice})
    except:
        pass
    
    # extract databases
    
    try:
        course_database=[]
        aux={'courseids[0]': str(course_id)}
        res = mdl.get_database_by_course(server,aux)
        xpars2 = xmltodict.parse(res.text)
        model_moodle.cadena=""
        model_moodle.convertXML_to_String(xpars2,0)
        data = model_moodle.write_array(model_moodle.cadena, data_type)
        aux_database1 = model_moodle.extract_info(data[0]," id ")
        aux_database2 = model_moodle.extract_info(data[0]," course ")
        aux_database3 = model_moodle.extract_info(data[0]," name ")
        for i in range(len(aux_database1)):
            course_database.append([aux_database1[i],aux_database2[i],aux_database3[i]])
        results.update({'course_database':course_database})
    except:
        pass 
    
    # extract folders
    
    try:
        course_folder=[]
        aux={'courseids[0]': str(course_id)}
        res = mdl.get_folders_by_course(server,aux)
        xpars2 = xmltodict.parse(res.text)
        model_moodle.cadena=""
        model_moodle.convertXML_to_String(xpars2,0)
        data = model_moodle.write_array(model_moodle.cadena, data_type)
        aux_folder1 = model_moodle.extract_info(data[0]," id ")
        aux_folder2 = model_moodle.extract_info(data[0]," coursemodule ")
        aux_folder3 = model_moodle.extract_info(data[0]," course ")
        aux_folder4 = model_moodle.extract_info(data[0]," name ")
        for i in range(len(aux_folder1)):
            course_folder.append([aux_folder1[i],aux_folder2[i],aux_folder3[i],aux_folder4[i]])
        results.update({'course_folder':course_folder})
    except:
        pass
    
    # extract glossary
    
    try:
        course_glossary=[]
        aux={'courseids[0]': str(course_id)}
        res = mdl.get_glossaries_by_course(server,aux)
        xpars2 = xmltodict.parse(res.text)
        model_moodle.cadena=""
        model_moodle.convertXML_to_String(xpars2,0)
        data = model_moodle.write_array(model_moodle.cadena, data_type)
        aux_glossary1 = model_moodle.extract_info(data[0]," id ")
        aux_glossary2 = model_moodle.extract_info(data[0]," coursemodule ")
        aux_glossary3 = model_moodle.extract_info(data[0]," course ")
        aux_glossary4 = model_moodle.extract_info(data[0]," name ")
        for i in range(len(aux_glossary1)):
            course_glossary.append([aux_glossary1[i],aux_glossary2[i],aux_glossary3[i],aux_glossary4[i]])
        results.update({'course_glossary':course_glossary})
    except:
        pass

    # extract quizz
    
    try:
        course_quizz=[]
        aux={'courseids[0]': str(course_id)}
        res = mdl.get_quizz_by_course(server,aux)
        xpars2 = xmltodict.parse(res.text)
        model_moodle.cadena=""
        model_moodle.convertXML_to_String(xpars2,0)
        data = model_moodle.write_array(model_moodle.cadena, data_type)
        aux_quizz1 = model_moodle.extract_info(data[0]," id ")
        aux_quizz2 = model_moodle.extract_info(data[0]," coursemodule ")
        aux_quizz3 = model_moodle.extract_info(data[0]," course ")
        aux_quizz4 = model_moodle.extract_info(data[0]," name ")
        for i in range(len(aux_quizz1)):
            course_quizz.append([aux_quizz1[i],aux_quizz2[i],aux_quizz3[i],aux_quizz4[i]])
        results.update({'course_quizz':course_quizz})
    except:
        pass 


    # extract url
    
    try:
        course_url=[]
        aux={'courseids[0]': str(course_id)}
        res = mdl.get_url_by_course(server,aux)
        xpars2 = xmltodict.parse(res.text)
        model_moodle.cadena=""
        model_moodle.convertXML_to_String(xpars2,0)
        data = model_moodle.write_array(model_moodle.cadena, data_type)
        aux_url1 = model_moodle.extract_info(data[0]," id ")
        aux_url2 = model_moodle.extract_info(data[0]," coursemodule ")
        aux_url3 = model_moodle.extract_info(data[0]," course ")
        aux_url4 = model_moodle.extract_info(data[0]," name ")
        for i in range(len(aux_url1)):
            course_url.append([aux_url1[i],aux_url2[i],aux_url3[i],aux_url4[i]])
        
        results.update({'course_url': course_url})
    except:
        pass




    return results