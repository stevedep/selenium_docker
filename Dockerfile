FROM mcr.microsoft.com/azure-functions/python:4-python3.10
ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true \ 
	CORS_ALLOWED_ORIGINS="[\"*\"]" \
	CONTAINER_NAME="yaradbg.dev" 


# 0. Install essential packages
RUN apt-get update \
    && apt-get install -y \
        build-essential \
        cmake \
        git \
        wget \
        unzip \
        unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# 1. Install Chrome (root image is debian)
# See https://stackoverflow.com/questions/49132615/installing-chrome-in-docker-file
ARG CHROME_VERSION="google-chrome-stable"
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
  && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
  && apt-get update -qqy \
  && apt-get -qqy install \
    ${CHROME_VERSION:-google-chrome-stable} \
  && rm /etc/apt/sources.list.d/google-chrome.list \
  && rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# 2. Install Chrome driver used by Selenium
#RUN wget http://chromedriver.storage.googleapis.com/114.0.5735.90/chromedriver_linux64.zip && \
#    unzip chromedriver_linux64.zip && ln -s $PWD/chromedriver /usr/local/bin/chromedriver114

RUN wget -N https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/121.0.6167.85/linux64/chromedriver-linux64.zip -O /tmp/chromedriver_linux64.zip
RUN unzip -o /tmp/chromedriver_linux64.zip -d /tmp/chromedriver/
RUN mkdir -p /tmp/Steve/
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub > /tmp/Steve/key.txt 
RUN apt-key add /tmp/Steve/key.txt
RUN echo "deb https://dl.google.com/linux/chrome/deb/ stable main" >> sudo -S /etc/apt/sources.list.d/google-chrome.list
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' 
RUN apt-get -y update 
RUN apt-get -y install google-chrome-stable 

# ENV PATH="/usr/local/bin/chromedriver114/:${PATH}"
ENV PATH="/tmp/chromedriver/:${PATH}"

# 4. Finally, copy python code to image
COPY . /home/site/wwwroot

# 5. Install other packages in requirements.txt
RUN cd /home/site/wwwroot && \
    pip install -r requirements.txt




