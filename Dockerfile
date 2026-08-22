FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl git python3 \
    && rm -rf /var/lib/apt/lists/*

ENV ELAN_HOME=/root/.elan
ENV PATH=/root/.elan/bin:$PATH
RUN curl -sSf https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh \
    | sh -s -- -y --default-toolchain leanprover/lean4:v4.24.0

WORKDIR /src
COPY examples/easy-ledger/lean/lean-toolchain examples/easy-ledger/lean/lean-toolchain
RUN lean --version

COPY . /src
WORKDIR /src
CMD ["python3", "scripts/gate.py", "--all"]
