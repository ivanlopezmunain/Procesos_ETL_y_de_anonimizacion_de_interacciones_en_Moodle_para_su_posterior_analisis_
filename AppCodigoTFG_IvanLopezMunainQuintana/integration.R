
#packages
pack<-c("rmarkdown","flexdashboard","dplyr","plotly","highcharter","shiny","treemap", "tibble")

#check if installed
for(i in 1:length(pack)){
  if ( (pack[i] %in% rownames(installed.packages())) == FALSE ){
    install.packages(pack[i], repos='https://cran.rstudio.com/') 
  }
}

dir <- Sys.getenv("RSTUDIO_PANDOC")
Sys.setenv(RSTUDIO_PANDOC=dir)

args = commandArgs(trailingOnly=TRUE)

#launch the dashboard in port 5001
setwd(getwd())
rmarkdown::run("dashboard.Rmd",  shiny_args = list(port = 5001),
               render_args = list(params=list(myargs_logs=args[1], myargs_grades=args[2])))
