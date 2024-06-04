## config PATH
echo .bashrc
# refer to symbol link jdk
export JAVA_HOME=/d/local/jdk
export PATH=$PATH:${JAVA_HOME}/bin
export MVN_HOME='/d/local/maven/maven'
export PATH=$PATH:${MVN_HOME}/bin
# refer to symbol link node
NODE_HOME=/d/local/node
export PATH=$PATH:$NODE_HOME

## config alias
#mvn clean install -Dparallel=all -DperCoreThreadCount=true
alias mvnc='mvn clean compile package install -DskipTests -T5'
alias pp='export http_proxy=localhost:10808; export https_proxy=localhost:10808'
alias ppp='unset http_proxy; unset https_proxy'
alias ll='ls -al --color=auto'


export LANG=en_US.UTF-8

