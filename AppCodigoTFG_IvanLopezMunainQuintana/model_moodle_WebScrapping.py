# Author: Ivan Lopez de Munain Quintana
# Date: Feb-Jul, 2020


import http.cookiejar as cookielib
from bs4 import BeautifulSoup as bs
import cgi, mechanize, os, getpass, argparse, shutil, io, openpyxl, random
from pathlib import Path
import numpy as np
from datetime import datetime



'''
Extract the name of the courses asociate to the user through webscraping
Input: 
    user: moodle username
    passwd: moodle password
    BASE_URL: url to login moodle
Output:
    list_ids_courses: list with the ids and names of the courses
'''
def extract_courses(user, passwd, BASE_URL):

    br = mechanize.Browser()
    #set options
    cookiejar = cookielib.LWPCookieJar()
    br.set_cookiejar(cookiejar)
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time = 1)
    br.open(BASE_URL)

    #introduce the credentials
    br.select_form(id='login')
    br.form['username']=user
    br.form['password']=passwd
    br.submit(id="loginbtn")

    get_courses_ids = str(BASE_URL.split("login")[0]) + "my/"

    #exploring the HTML and get the courses
    url = br.open(get_courses_ids)
    soup = bs(url, "html.parser")
    aux_link = "/course/view.php?id="
    list_courses_teach=[]
    for a in soup.findAll("a"):
        if aux_link in a.get("href"):
            list_courses_teach.append(a.get("href").split("=")[1])

    list_ids_courses=[]
    for i in range(len(list_courses_teach)):
        get_courses= str(BASE_URL.split("login")[0]) + "report/log/index.php?id=" + str(list_courses_teach[i])
        url = br.open(get_courses)
        soup = bs(url, "html.parser")
        for ind in soup.findAll("select"):
            if ind.get("id")=="menuid":
                for option in ind.findAll("option"):
                    list_ids_courses.append((str(option['value']) + ":" + str(option.text)))


    return list_ids_courses


'''
Extract logs and grades of the courses asociate to the user through webscraping
Input: 
    course_id: id of the course
    user_id: id of a user to make a filter
    modulo_id: id of a moduleto make a filter
    modaction: type of actions in the log to make a filter
    edu_level: type of role in the log to make a filter
    one_tab: donwload the data or not
    data_type: type of information
    dicc_anonim: correspondences id_moodle-id_anonim
    dicc_fullname: correspondences fullname-id_anonim
    table_anonim: all correspondences
    user: moodle username
    passwd: moodle password
    BASE_URL: url to login moodle
    mode: teacher or investigator
Output:
    final_list: list with the logs (after anonymized and make the filters)
'''
def web_scrapping_moodle(course_id, user_id, modulo_id, modaction, edu_level, one_tab, data_type, dicc_anonim, dicc_fullname,table_anonim, user, passwd, BASE_URL,mode):


    a_nom={'investigator': 'researcher',
        'teacher': 'teacher'}

    # Set the browser for the web crawler
    br = mechanize.Browser()
    cookiejar = cookielib.LWPCookieJar()
    br.set_cookiejar(cookiejar)
    br.set_handle_equiv(True)
    br.set_handle_gzip(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time = 1)
    br.open(BASE_URL)
    
    br.select_form(id='login')
    br.form['username']=user
    br.form['password']=passwd
    br.submit(id="loginbtn")

    '''
    # Check if success (login to the Moodle)
    url = br.open(BASE_URL)
    login = url.get('X-Frame-Options', None)
    status, _ = cgi.parse_header(login)
    if status.upper() == "DENY":
        print("Login failed. Check your NIA and password and try again")
        exit(1)
    '''

    # ============================ Download grades ===============================================

    try:

        query_string_grades_1 = str(BASE_URL.split("login")[0]) + "grade/report/grader/index.php?id=" + str(course_id)
        url_grades_1 = br.open(query_string_grades_1)
        soup = bs(url_grades_1, "html.parser")
        idents_users=[]
        for a in soup.findAll("a", {'class': 'username'}):
                if "user" in str(a.get("href")):
                    if "id=" in str(a.get("href")):
                        if "course=" in str(a.get("href")):
                            a_idents = str(a.get("href")).split("id=")[1]
                            a_idents = a_idents.split("&")[0]
                            idents_users.append(a_idents)
        


        query_string_grades= str(BASE_URL.split("login")[0]) + "grade/export/xls/index.php?id=" + str(course_id)
        url_grades = br.open(query_string_grades)

        soup = bs(url_grades, "html.parser")
        count_forms=-1
        for a in soup.findAll("form"):
            count_forms = count_forms + 1

        br.select_form(nr=count_forms)

        #saving the grades        
        if not os.path.isdir("Download"):
                os.mkdir("Download")

        if not os.path.isdir("Download/" + str(a_nom[mode])):
            os.mkdir("Download/" + str(a_nom[mode]))

        if not os.path.isdir("Download/" + str(a_nom[mode]) +"/Grades"):
            os.mkdir("Download/" + str(a_nom[mode]) + "/Grades")

        with open("Download/" + str(a_nom[mode]) + "/Grades/Grades_" + str(course_id) + ".xlsx", 'wb') as ff:
            shutil.copyfileobj(br.submit(id="id_submitbutton"), ff)
            ff.close()

        
        xlsx_file_grades = Path("./Download/" + str(a_nom[mode]) + "/Grades/Grades_" + str(course_id) + ".xlsx" )
        wb_obj_grades = openpyxl.load_workbook(xlsx_file_grades)


        os.remove("Download/" + str(a_nom[mode]) + "/Grades/Grades_" + str(course_id) + ".xlsx" )

        #processing marks (normalize into 0-1)
        sheet_grades = wb_obj_grades.active
        aux_list_grades=[]
        final_list_grades=[]
        for row in sheet_grades:
            aux_list_grades=[]
            for cell in row:      
                aux_list_grades.append(cell.value)
            final_list_grades.append(aux_list_grades)
        

        save_grades=[]
        save_grades_final=[]
        aux_names_grades=[]

        aux_g=[]
        aux_g.append("User ID")

        norm_grades = []
        norm_grades_f = []
        num_mark = (len(final_list_grades[0])-1-6)

        for a in range(len(final_list_grades[0])):
            if a<(len(final_list_grades[0])-1) and a>5:
                aux_g.append(final_list_grades[0][a])
        save_grades_final.append(aux_g)

        for row in final_list_grades[1:]:
            name_student = str(row[0]) + " " + str(row[1])
            save_grades=[]
            aux_names_grades.append(name_student)
            save_grades.append(name_student)
            
            norm_grades=[]
            for i in range(len(row)):
                if i<(len(row)-1) and i>5:
                    norm_grades.append(row[i])

                    save_grades.append(row[i])
            norm_grades_f.append(norm_grades)
            
            save_grades_final.append(save_grades)

        marks_matrix = np.array(norm_grades_f)

        f_yes=0
        a_yes=[]
        for i in range(num_mark):
            f_yes=0
            a_yes=[]
            for ii in range(len(marks_matrix[:,i])):
                if marks_matrix[ii,i]!= "-":
                    a_yes.append(float(marks_matrix[ii,i]))
                    f_yes=1
            if f_yes!=0:
                maxi = max(a_yes)
                for j in range(len(marks_matrix[:,i])):
                    if marks_matrix[j,i]!="-":
                        marks_matrix[j,i] =  round(float(marks_matrix[j,i])/float(maxi),3)
                        '''
                        #to categorize
                        if val > 0.666:
                            marks_matrix[j,i]= "High"
                        elif val<0.333:
                            marks_matrix[j,i]= "Low"
                        else:
                            marks_matrix[j,i]= "Intermediate"
                        '''

        cont=0
        for row in save_grades_final[1:]:
            for i in range(len(row)):
                if  i>0:
                    row[i]= marks_matrix[cont,i-1]
            cont = cont+1

        list_trans_users=[]
        sep=" "
        cont=0
        if mode=="teacher":
            save_grades_final[0].append("ID_Moodle")
            for row in save_grades_final[1:]:
                row.append(idents_users[cont])
                cont = cont + 1
        
            for row in save_grades_final[1:]:
                row[0] = sep.join(row[0].split())
                list_trans_users.append([row[0],row[len(row)-1]])

        cont=0
        if mode=="investigator":
            for row in save_grades_final[1:]:
                row[0] = sep.join(row[0].split())
                list_trans_users.append([row[0],idents_users[cont]])
                cont = cont + 1
    except:
        pass

    dicc_names_grades={}
    for a in range(len(list_trans_users)):
        aux_l = list_trans_users[a][0].split()
        aux_l.sort()
        dicc_names_grades.update({list_trans_users[a][1]:aux_l})


    # ===================================== Download logs =====================================================


    dic_queryString = {
        "All_actions": "",
        "Delete": "d",
        "Create" : "c",
        "Update" : "u",
        "All_changes": "cud",
        "View": "r",
        "All_events" : "-1",
        "Others": "0",
        "Teaching": "1",
        "Participant": "2"
    }

        

    query_string_logs = str(BASE_URL.split("login")[0]) + "report/log/index.php?chooselog=1&showusers=0&showcourses=0&id=" + course_id + "&user=" + user_id + "&date=&modid=" + modulo_id + "&modaction=" + dic_queryString[modaction] +"&origin=&edulevel=" + dic_queryString[edu_level] + "&logreader=logstore_standard"
    url = br.open(query_string_logs)


    dic = {
        "csv": "csv",
        "excel": "xlsx",
        "html" : "html",
        "json" : "json",
        "ods" : "ods",
        "pdf" : "pdf"
    }

    type_fich = "excel"
    br.select_form(nr=1)
    form = br.form
    form['download'] = [type_fich]

    a_nom={'investigator': 'researcher',
        'teacher': 'teacher'}

    #creating the directories
    if not os.path.isdir("Download"):
        os.mkdir("Download")
    
    if not os.path.isdir("Download/" + str(a_nom[mode])):
        os.mkdir("Download/" + str(a_nom[mode]))

    if not os.path.isdir("Download/" + str(a_nom[mode]) + "/" + str(data_type)):
        os.mkdir("Download/" + str(a_nom[mode]) + "/" + str(data_type))

    cadena = "Course_" + str(course_id)
    if user_id != "":
        cadena = cadena + "_User_" + str(user_id)

    if modulo_id != "":
        cadena = cadena + "_Module_" + str(modulo_id)

    if modaction != "All_actions":
        cadena = cadena + "_Action_" + str(modaction)

    if edu_level != "All_events":
        cadena = cadena + "_Event_" + str(edu_level)
    
    with open("Download/" + str(a_nom[mode]) + "/" + str(data_type) + "/" + cadena + "." + str(dic[type_fich]), 'wb') as f:
        shutil.copyfileobj(br.submit(), f)
        f.close()

   
    xlsx_file = Path("./Download/" + str(a_nom[mode]) + "/" + str(data_type) , cadena + "." + str(dic[type_fich]))
    wb_obj = openpyxl.load_workbook(xlsx_file)

    sheet = wb_obj.active
    aux_list=[]
    final_list=[]
    for row in sheet:
        aux_list=[]
        for cell in row:      
            aux_list.append(cell.value)
        final_list.append(aux_list)


    os.remove("Download/" + str(a_nom[mode]) + "/" + str(data_type) + "/" + cadena + "." +  str(dic[type_fich]))


    #remove logs from others years (Moodle bug)
    actual_year = datetime.today().strftime('%Y')
    actual_month = datetime.today().strftime('%m')
    if int(actual_month)<8:
        actual_year = int(actual_year) - 1

    a_cont=0
    for row in final_list[1:]:
        a_date = row[0].split(" ")[0]
        print(a_date)
        a_year = a_date.split("/")[2]
        if  int(a_year) == int(actual_year):
            a_month = a_date.split("/")[1]
            if int(a_month)<9:
                break
        a_cont = a_cont + 1
    
    final_list = final_list[0:a_cont]

   
    #diccs local anonim
    dicc_local_anonim = {}
    dicc_local_anonim_names = {}

    #diccs names integration
    dic_user_moodle={}
    keys_names_grades = list(dicc_names_grades.keys())
    dic_user_moodle_teacher=[]

    new_id=2222
    flag_1=0
    separator=""
    final_list[0][1] = "ID User"
    if mode=="teacher":
        final_list[0].append("ID_Moodle")
        final_list[0].append("Role")
    
    if mode=="investigator":
        final_list[0].append("Role")

    for row in final_list[1:]:

        if mode=="teacher":
            g_flag=0
            try:
                if row[1] in dic_user_moodle_teacher:
                    row.append("-")
                    row.append("Teacher")
                else:
                    row.append(dic_user_moodle[row[1]])
                    row.append("Student")
            except:
                aux_row1 = row[1].split()
                aux_row1.sort()
                for k_g in range(len(keys_names_grades)):
                    if aux_row1 == dicc_names_grades[keys_names_grades[k_g]]:
                        dic_user_moodle.update({row[1]:keys_names_grades[k_g]})
                        row.append(keys_names_grades[k_g])
                        row.append("Student")
                        g_flag=1
                        break
                if g_flag==0:
                    row.append("-")
                    row.append("Teacher")
                    dic_user_moodle_teacher.append(row[1])
            
            sep=" "
            row[1] = sep.join(row[1].split())



        #Anonimization
        if mode=="investigator":
            g_flag=0
            try:
                if row[1] in dic_user_moodle_teacher:
                    row.append("Teacher")
                else:
                    aux_no_util = dic_user_moodle[row[1]]
                    row.append("Student")
            except:
                aux_row1 = row[1].split()
                aux_row1.sort()
                for k_g in range(len(keys_names_grades)):
                    if aux_row1 == dicc_names_grades[keys_names_grades[k_g]]:
                        dic_user_moodle.update({row[1]:keys_names_grades[k_g]})
                        row.append("Student")
                        g_flag=1
                        break
                if g_flag==0:
                    row.append("Teacher")
                    dic_user_moodle_teacher.append(row[1])

            flag_1=0
            row[8]= "No IP"
            row[3] = row[3].split(":")[0]
            div = row[6].split("'")
            keys = list(dicc_local_anonim.keys())
            keys_global_api = list(dicc_anonim.keys())
            if len(div)>1:
                if str(div[1]) in keys_global_api:
                    div[1] = dicc_anonim[div[1]]
                    row[6] = separator.join(div)
                    row[1]= div[1]
                else:
                    for j in range(len(keys)):
                        if keys[j]==div[1]:
                            div[1] = dicc_local_anonim[keys[j]]
                            row[6] = separator.join(div)
                            row[1]= div[1]
                            flag_1=1
                            break
                    if flag_1==0:
                        dicc_local_anonim.update({str(div[1]) : str(new_id)})
                        dicc_local_anonim_names.update({str(row[1]) : str(new_id)})
                        div[1] = dicc_local_anonim[div[1]]
                        row[6] = separator.join(div)
                        row[1]= div[1]
                    new_id = new_id + 1

    
    if mode=="investigator":
        keys_names = list(dicc_local_anonim_names.keys()) 
        flag_2=0
        for row in final_list[1:]:
            flag_2=0
            for j in range(len(keys_names)):
                if keys_names[j] in row[2]:
                    row[2] = dicc_local_anonim_names[keys_names[j]]
                    flag_2=1
                if keys_names[j] in row[1]:
                    row[1] = dicc_local_anonim_names[keys_names[j]]
            if flag_2==0:
                new_id = new_id + 1
                dicc_local_anonim_names.update({str(row[2]) : str(new_id)})
                row[2] = str(new_id)


        #anonimyzed dates
        c_cont = len(final_list)-1
        cont_days = 1
        before_date=""
        while c_cont>0:

            div = final_list[c_cont][0].split(",")
            a_div = div[1].split(":")[0]

            if c_cont==(len(final_list)-1):
                d_anonim = "Day: " + str(cont_days) + ", Hour: " + str(a_div)
            
            else:

                if str(div[0]) != str(before_date):
                    cont_days = cont_days + 1
                    d_anonim = "Day: " + str(cont_days) + ", Hour: " + str(a_div)
                else:
                    d_anonim = "Day: " + str(cont_days) + ", Hour: " + str(a_div)
                
            before_date = final_list[c_cont][0].split(",")[0]
            final_list[c_cont][0] = d_anonim
            c_cont = c_cont - 1 
 
    #saving processed grades and processed logs
    if one_tab == "down":
        if mode=="teacher":
            path = "Download/" + str(a_nom[mode]) + "/"  + str(data_type) + "/" + cadena + ".csv"
            path_2= "Download/" + str(a_nom[mode]) + "/Grades/Grades_" + str(course_id) + ".csv"
            final_list = [final_list, path, path_2]

        a_nom={'investigator': 'researcher',
                'teacher': 'teacher'}
            
        with open("Download/" + str(a_nom[mode]) + "/"  + str(data_type) + "/" + cadena + ".csv", 'w', newline="") as f:
            import csv
            writer = csv.writer(f, delimiter=";")
            if mode == "teacher":
                writer.writerows(final_list[0])
            else:
                writer.writerows(final_list)
            f.close()

    

    # ============ Save grades ===============
   
    if mode=="investigator":
        for ind in range(len(save_grades_final[0])):
            save_grades_final[0][ind]= save_grades_final[0][ind].split(":")[0]
        
        flag_save_g=0
        for r in save_grades_final[1:]:
            flag_save_g=0
            keys_n = list(dicc_fullname.keys())
            for a in range(len(keys_n)):
                if r[0]==keys_n[a]:
                    r[0]= dicc_fullname[keys_n[a]]
                    flag_save_g=1
                    break
            if flag_save_g==0:
                new_id=new_id+1
                dicc_fullname.update({r[0]:new_id})
                r[0]=new_id

    if one_tab=="down":
        a_nom={'investigator': 'researcher',
        'teacher': 'teacher'}
        with open("Download/" + str(a_nom[mode]) + "/Grades/Grades_" + str(course_id) + ".csv", 'w', newline="") as f:
            import csv
            writer = csv.writer(f, delimiter=";")
            writer.writerows(save_grades_final)
            f.close()



    return final_list
