# Author: Ivan Lopez de Munain Quintana
# Date: Feb-Jul, 2020

from flask import Flask, render_template, request, redirect
import model_moodle, controller_courses_home, controller_course_detail, controller_course_download
import xmltodict, json, collections, io, os, requests, csv, glob, random, webbrowser, sys
import model_moodle_WebScrapping


##################### global variables #######################
dicc_anonim={}
dicc_fullname={}
table_anonim = []

user=""
password=""
url_login=""
method="teacher"
list_courses_global=[]
list_courses_global_api=[]

#route to Rscript.exe
route_to_rscript = str(sys.argv[1].split("\\")[len(sys.argv[1].split("\\"))-2])



app = Flask(__name__)

######################### root ##################################
#select between teacher or investigator mode

@app.route('/', methods=['GET', 'POST'])
def home(): 
    return render_template("view_invest_teach.html")


######################### /Login ##################################
#introduce moodle user and password, it is neccesary for boths modes

@app.route('/Login', methods=['GET', 'POST'])
def home12(): 
    global method
    if request.method == 'POST':
        method = request.form['select_mode']

    return render_template("view_connection.html")

######################### /Auth ##################################
#introduce access token, uri and protocol. Only for investigator mode

@app.route('/Auth' , methods=['GET', 'POST'])
def home2(): 

    global user
    global password
    global url_login
    global method
    global list_courses_global

    if request.method == 'POST':
        user = request.form['user']
        password = request.form['password']
        url_login = request.form['url_login']

    if method=="investigator":
        return render_template("view_connection2.html")
    else:
        list_courses_global= model_moodle_WebScrapping.extract_courses(user,password,url_login)
        chain_ids= ""
        for element in list_courses_global:
            chain_ids = chain_ids + "-" + str(element.split(":")[0])

        return redirect("http://127.0.0.1:5000/course_selection/mode_teach/mode_teach/mode_teach/" + str(chain_ids))


######################### /check_connection/token/uri/protocol ##################################
#only possible to investigator mode. Allows to select courses

@app.route('/check_connection/<string:tok>/<string:uri>/<string:prot>')
def home_courses(tok,uri,prot):

    global dicc_anonim
    global dicc_fullname 
    global table_anonim
    global list_courses_global_api

    uri = uri.replace("-","/")
    mdl = model_moodle.MDL()

    server={
        "protocol" : str(prot),
        "uri" : str(uri),
        "token" : str(tok)
    }

    parameters={
        'key': '',
        'value':''
    }


    try:
        #extract users asociated to the moodle (it is used to anonymized the data)
        res = mdl.get_users(server, parameters)
        xpars2 = xmltodict.parse(res.text)
        model_moodle.cadena=""
        model_moodle.convertXML_to_String(xpars2,0)
        data = model_moodle.write_array(model_moodle.cadena, "User")
        anonim=1111
        ident = ""
        ident_2=""
        for ind in data[0]:
            for w in ind:
                for a in w:
                    if " id " in a:
                        ident = w[1]
                    if " fullname " in a:
                        ident_2 = w[1]
                    if " email " in a:
                        table_anonim.append([ident.strip(), w[1].strip(), ident_2.strip(), anonim])
                        anonim = anonim + random.randint(1,10)
        
        #saving the correspondences between real and anonymized data
        if not os.path.isdir("Download/researcher"):
                os.mkdir("Download/researcher")
        if not os.path.isdir("Download/researcher/Tmp_Anonim"):
            os.mkdir("Download/researcher/Tmp_Anonim")

        with open("Download/researcher/Tmp_Anonim/Correspondences_Complete_Course.csv", 'w', newline="") as f:
                import csv
                writer = csv.writer(f, delimiter=";")
                writer.writerow(("Key_Moodle","Email","Fullname","ID_anonim"))
                writer.writerows(table_anonim)
                f.close()


        # table_anonim: correspondences [id_moodle, email, fullname, id_anonim]
        # dicc_anonim: dictionary id_moodle-id_anonim
        # dicc_fullname: dictionary name-id_anonim 
        for users in table_anonim:
            dicc_anonim.update({str(users[0]): str(users[3])})
            dicc_fullname.update({str(users[2]): str(users[3])})
               

        try:
            #extract courses asociated to the user who has just identified to the system
            data_keys= ["Course"]
            data_type= "Course"
            aux_data = controller_courses_home.obtain_all_courses(server, data_keys , data_type,0)


            #save the correspondences between courses and the ID
            with open("Download/researcher/Tmp_Anonim/Correspondences_ Course_ID.csv", 'w') as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["Anonim_ID", "Name_Course"])
                for i in range(len(aux_data)):
                    a_aux = aux_data[i].split(" ")[0]
                    writer.writerow([a_aux[3:].strip(),aux_data[i]])
                f.close()
            list_courses_global_api=[]
            for i in range(len(aux_data)):
                a_aux = aux_data[i].split(" ")[0]
                list_courses_global_api.append([a_aux[3:].strip(),aux_data[i]])
            uri = uri.replace("/","-")
            return render_template("view_courses_home.html", data_keys=data_keys, data_type=data_type, aux_data=aux_data, protocol =prot, token = tok, uri =uri)

        except:
            uri = uri.replace("/","-")
            return render_template("view_error_parameters.html", protocol =prot, token = tok, uri =uri)
    
    except:
        return render_template("view_error_connection.html")


######################### /check_connection/token/uri/protocol/id_course ##################################
#only possible to investigator mode. Allows to view detail information of a subject.

@app.route('/check_connection/<string:tok>/<string:uri>/<string:prot>/<string:course_view>')
def course_view(tok,uri,prot,course_view): 

    global dicc_anonim
    global dicc_fullname

    uri = uri.replace("-","/")

    server={
        "protocol" : str(prot),
        "uri" : str(uri),
        "token" : str(tok)
    }

    #gets the detail information asociated to the course 
    data_keys=["Feature", "Value"]
    data_type = "Course"
    index=0
    course_view = course_view[course_view.find(" "):]
    results = controller_course_detail.get_course_detail(server, data_keys, data_type, index, course_view)  

    uri = uri.replace("/","-")
    return render_template("view_course_detail.html" ,  data_keys=data_keys, data_type=data_type,
                          results=results, protocol =prot, token = tok, uri =uri)


######################### /check_connection/token/uri/protocol/list_courses_selected ##################################
#Avalaible to teacher and investigator mode. Allows to select information of a subject and download it.
#Investigator mode: the download data is anonymized
#Teacher mode: the download data is not anonymized but it is possible to view a dashboard of the data.

@app.route('/course_selection/<string:tok>/<string:uri>/<string:prot>/<string:list_course>')
def course_selection(tok,uri,prot,list_course): 

    global dicc_anonim
    global dicc_fullname
    global table_anonim
    global user
    global password
    global url_login
    global method
    global list_courses_global
    global list_courses_global_api
    global route_to_rscript

    down = None

    list_course_ids = list_course.split("-")[1:]

    if method=="investigator":
        if request.args:        

            uri = uri.replace("-","/")
            server={
                "protocol" : str(prot),
                "uri" : str(uri),
                "token" : str(tok)
            }

            parameters = {
                'key': '',
                'value' : ''
            }
            aux_r=request.args
            pack = controller_course_download.investigator_mode(server, parameters,down,list_course_ids,aux_r,dicc_anonim,dicc_fullname,table_anonim,user,password, url_login)


            if pack["error"]=="yes":
                uri = uri.replace("/","-")
                return render_template("view_error_parameters.html", protocol =prot, token = tok, uri =uri, list_course=list_course)
            else:

                if pack["data"]==None:
                    return render_template("view_course_download.html", protocol =prot, token = tok, uri =uri, list_course=list_course, list_course_ids=list_courses_global_api, mode=method)
                else:
                    uri=uri.replace("/","-")
                    return render_template("view_course_download.html" ,
                                                protocol =prot, token = tok, uri =uri, list_course=list_course, list_course_ids=list_courses_global_api,
                                                data=pack['data'] ,index=pack['index'],data_keys=pack['data_keys'], data_type=pack['data_type'],mode=method)
                
        uri=uri.replace("/","-")
        return render_template("view_course_download.html", protocol =prot, token = tok, uri =uri, list_course=list_course, list_course_ids=list_courses_global_api, mode=method)

    else:

        a_a_aux=[]
        for i in range(len(list_course_ids)):
            a_a_aux.append([list_course_ids[i],list_courses_global[i]])

        if request.args:

            aux_r=request.args
            pack = controller_course_download.teacher_mode(down,list_course_ids,aux_r,dicc_anonim,dicc_fullname,table_anonim,user,password, url_login,route_to_rscript)

            if pack["error"]=="yes":
                return render_template("view_error_parameters.html", protocol =prot, token = tok, uri =uri, list_course=list_course)
            else:
                return render_template("view_course_download.html" ,
                                            protocol =prot, token = tok, uri =uri, list_course=list_course, list_course_ids=a_a_aux,
                                            data=pack['data'] ,index=pack['index'],data_keys=pack['data_keys'], data_type=pack['data_type'])

        return render_template("view_course_download.html", protocol =prot, token = tok, uri =uri, list_course=list_course, list_course_ids=a_a_aux)

    


if __name__ == '__main__':
    app.run()



