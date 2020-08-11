# Procesos ETL y de anonimizacion de interacciones en Moodle para su posterior analisis
Este proyecto corresponde con el Trabajo de Fin de Grado asociado a la carrera de Ingeniería Informática de la Univerdad de Valladolid.
El trabajo aquí expuesto pretende desarrollar una aplicación web que permita extraer de forma sistematizada
la máxima cantidad de datos posibles del sistema e-learning con mayor aceptación
universitaria, Moodle. Esta aplicación tiene dos finalidades bien diferenciadas: la primera está
asociada al ámbito de investigación, posibilitando la obtención de cantidades masivas de información
anonimizada; mientras que la segunda se vincula a la ayuda de la práctica docente. Esta
última, permitirá a profesores universitarios acceder a los datos de sus asignaturas y monitorizarlas,
analizarlas e incluso mejorarlas gracias a la ayuda de un dashboard desplegado en una
segunda aplicación web. Ambas aplicaciones web son desarrolladas en lenguajes de programación
distintos (Python y R) por lo que son integradas de forma conjunta.

### Palabras clave
Python, Flask, R, Shiny, HTML, JS, CSS, Moodle, sistemas e-learning,
anonimización, big data, API, servicios web, web scraping, REST, dashboard, SCRUM, investigación,
análisis del aprendizaje, aplicación web, interacciones, notas, procedimientos estadísticos,
interfaces, técnicas ETL, base de datos de Moodle

### Jerarquía de ficheros

* MemoriaTFG_IvanLopezMunainQuintana: documentación completa sobre el desarrollo del proyecto, además de los manuales de instalación
y usuario de las aplicaciones web (junto a los requisitos necesarios para su lanzamiento).
* AppCodigoTFG_IvanLopezMunainQuintana: código correspondiente a las aplicaciones desarrolladas (ficheros en R y Python).
  + Folders:
    - _pycache_: python cache
    - Download: data download from Moodle
    - Pandoc: documentation about the version of Pandoc (to launch the R app)
    - static: images from the interface
    - templates: scripts htmls (views of the app)
  + Files:
    - app: server
    - controller*: controllers of the application
    - model*: models of the application
    -  dashboard: R application
    - integration: R script to launch dashboard.R
    - launcher: bat file to launch app.py
    - pandoc*: version of pandoc to allow launch dashboard
