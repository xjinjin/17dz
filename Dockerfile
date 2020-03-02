FROM python:3.7
ADD requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN mkdir -p /code/logs
RUN chmod 777 /code/logs
COPY . /code
#WORKDIR /code
#RUN chmod +x docker-entrypoint.sh
#VOLUME ["/code/logs"]
#CMD nohup python /code/start_file.py >/dev/null 2>&1 &
CMD python /code/start_file.py
#CMD /code/docker-entrypoint.sh

