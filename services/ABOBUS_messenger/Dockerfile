FROM rust:1.76

# Install SQLite3 and development headers
RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev socat

# Set the working directory
WORKDIR /usr/src/app
COPY . .

RUN sqlite3 cats.db < init.sql
RUN head -c 32 /dev/urandom  > src/secret_key

RUN cargo build --release 
RUN mv target/release/ABOBUS_messenger .
RUN chmod +x entrypoint.sh ABOBUS_messenger
ENTRYPOINT [ "./entrypoint.sh" ]