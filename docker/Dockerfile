FROM python:3.6

ARG UID=1000
EXPOSE 8888

RUN adduser jupyter --uid $UID --disabled-password --system

RUN mkdir /app
COPY setup.py README.md HISTORY.md /app/
RUN pip install -e /app && pip install jupyter

COPY cms_ml /app/cms_ml
COPY tutorials /app/tutorials

WORKDIR /app
USER jupyter
CMD /usr/local/bin/jupyter notebook --ip 0.0.0.0 --NotebookApp.token=''
