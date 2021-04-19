FROM andrius/asterisk

RUN apk add --update less psqlodbc asterisk-odbc asterisk-pgsql && \
    rm -rf /var/cache/apk/*
