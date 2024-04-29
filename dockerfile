FROM python AS jsl

RUN apt update && \
    apt install vim -y

RUN pip3 install black
RUN pip3 install argcomplete
RUN pip3 install blessed
RUN pip3 install jira
RUN pip3 install Requests
