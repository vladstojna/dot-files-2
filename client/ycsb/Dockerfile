FROM ubuntu:focal

ARG YCSB_VER=0.17.0
ARG YCSB_BINDING

ENV YCSB_PREFIX=${YCSB_BINDING:+ycsb-${YCSB_BINDING}-binding-${YCSB_VER}}
ENV YCSB_PREFIX=${YCSB_PREFIX:-ycsb-${YCSB_VER}}

# install dependencies
RUN apt-get update
RUN apt-get install -y \
    curl \
    openjdk-8-jre-headless \
    python2 \
    tar

WORKDIR /work

RUN groupadd ycsb
RUN useradd -g ycsb ycsb
RUN chown -R ycsb:ycsb .

USER ycsb

# download YCSB and extract
RUN curl -OL \
    https://github.com/brianfrankcooper/YCSB/releases/download/${YCSB_VER}/${YCSB_PREFIX}.tar.gz
RUN tar xfz ${YCSB_PREFIX}.tar.gz
RUN rm -f ${YCSB_PREFIX}.tar.gz

WORKDIR ${YCSB_PREFIX}

ENTRYPOINT ["/usr/bin/python2", "bin/ycsb" ]
