# build
FROM rust@sha256:da23629cc6826f0c395c8697994cdce0b5ac6850a695c448a101c3cc9cd6a59b as builder

WORKDIR /
RUN USER=root cargo new --lib minijit
WORKDIR /minijit
COPY ./minijit/Cargo.toml ./Cargo.toml

RUN cargo build --release
RUN rm src/*.rs

COPY ./minijit/src ./src

RUN rm ./target/release/deps/libminijit*
RUN cargo build --release

WORKDIR /
RUN USER=root cargo new --bin kubik
WORKDIR /kubik

COPY ./kubik/Cargo.toml ./Cargo.toml

RUN cargo build --release
RUN rm src/*.rs

COPY ./kubik/src ./src

RUN rm ./target/release/deps/kubik*
RUN cargo build --release

# runtime
FROM debian@sha256:70955dce615f114142818e95339f6ae9b461cf424d79d59ca2b04ec725d4dbc8

WORKDIR /appdir
COPY --from=builder /kubik/target/release/kubik .
COPY --from=builder /minijit/target/release/libminijit.so .

CMD ["./kubik"]
