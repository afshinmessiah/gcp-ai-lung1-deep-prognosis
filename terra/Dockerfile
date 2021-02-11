FROM tensorflow/tensorflow:1.15.4-gpu-py3

LABEL maintainer="dennis_bontempi@dfci.harvard.edu"
LABEL version="1.0"
LABEL description="Terra Docker for Deep Prognosis."

RUN apt-get update && apt-get install --no-install-recommends --no-install-suggests -y curl
RUN apt-get install -y unzip
RUN apt-get install -y plastimatch

 # google-cloud-sdk separately because it need lsb-release and other prereqs installed above
 RUN export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)" \
 && echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" > /etc/apt/sources.list.d/google-cloud-sdk.list \
 && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - \
 && apt-get update \
 && apt-get install -yq --no-install-recommends \
    google-cloud-sdk
    
ENV USER terra-test
ENV UID 1000
RUN useradd -m -s /bin/bash -N -u $UID $USER

ENV HOME /home/$USER

RUN mkdir /home/$USER/src
RUN mkdir /home/$USER/data
RUN mkdir /home/$USER/models

COPY src $HOME/src
COPY data $HOME/data
COPY models $HOME/models  
COPY requirements.txt $HOME
COPY run_pipeline.sh $HOME

RUN pip3 install -r $HOME/requirements.txt\
&& pip3 install google-cloud-bigquery

ENTRYPOINT ["/bin/bash"]
