FROM 10.79.1.164:5000/cki/ubuntu-jetty:9.3.23.test
MAINTAINER by daiyongjie

ADD ./target/*.war /opt/jetty-9.3.23/webapps/


#启动时运行jetty
#CMD ["/opt/jetty-9.3.23/bin/jetty.sh","run"]
