ARG ARANGODB_VERSION=latest
FROM arangodb:${ARANGODB_VERSION}

WORKDIR /results
VOLUME /results

ENTRYPOINT ["arangobench"]
CMD ["--version"]
