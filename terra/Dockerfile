FROM tensorflow/tensorflow:1.15.4-gpu-py3
USER root
LABEL maintainer="dennis_bontempi@dfci.harvard.edu"
LABEL version="1.0"
LABEL description="Terra Docker for Deep Prognosis."

RUN python3 -m pip install --upgrade pip
RUN apt-get update && apt-get install --no-install-recommends \
    --no-install-suggests -y curl \
    sudo \
    wget \
    locales \
    git
RUN apt-get install -y unzip
RUN apt-get install -y plastimatch

 # google-cloud-sdk separately because it need lsb-release and other prereqs installed above
 RUN export CLOUD_SDK_REPO="cloud-sdk-$(lsb_release -c -s)" \
 && echo "deb http://packages.cloud.google.com/apt $CLOUD_SDK_REPO main" > /etc/apt/sources.list.d/google-cloud-sdk.list \
 && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - \
 && apt-get update \
 && apt-get install -yq --no-install-recommends google-cloud-sdk
 
ENV REPO_NAME deep-prognosis-code
RUN mkdir "${REPO_NAME}"
RUN cd "${REPO_NAME}"
RUN git init
RUN git remote add -f origin https://github.com/afshinmessiah/gcp-ai-lung1-deep-prognosis.git
RUN git config core.sparseCheckout true
RUN echo "terra/src" >> .git/info/sparse-checkout
RUN echo "terra/models" >> .git/info/sparse-checkout
RUN echo "terra/requirements.txt" >> .git/info/sparse-checkout
RUN cd ..
RUN pip3 install -r "/${REPO_NAME}/terra/requirements.txt"\
&& pip3 install google-cloud-bigquery


