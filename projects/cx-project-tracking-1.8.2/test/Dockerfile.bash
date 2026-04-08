FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash zsh python3 python3-pip jq curl git dos2unix file \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /project
COPY . /project/

RUN mkdir -p /root/.snowflake
RUN mkdir -p /root/.snow

ENTRYPOINT ["bash", "/project/test/test-install-sh.sh"]
