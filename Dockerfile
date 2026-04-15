FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    ninja-build \
    pkg-config \
    linux-libc-dev \
    git \
    curl \
    zip \
    unzip \
    tar \
    ca-certificates \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

RUN bash -lc 'for i in 1 2 3 4 5; do \
        git clone --depth 1 https://github.com/microsoft/vcpkg.git /opt/vcpkg && break; \
        echo "vcpkg clone failed, retry $i/5"; \
        rm -rf /opt/vcpkg; \
        sleep 5; \
    done' \
    && test -d /opt/vcpkg \
    && /opt/vcpkg/bootstrap-vcpkg.sh -disableMetrics

RUN python3 -m pip install --no-cache-dir -r /app/frontend/requirements.txt

RUN mkdir -p /opt/vcpkg/downloads \
    && curl -L --retry 5 --retry-all-errors https://github.com/openssl/openssl/archive/openssl-3.6.2.tar.gz -o /opt/vcpkg/downloads/openssl-openssl-openssl-3.6.2.tar.gz \
    && curl -L --retry 5 --retry-all-errors https://github.com/curl/curl/archive/curl-8_19_0.tar.gz -o /opt/vcpkg/downloads/curl-curl-curl-8_19_0.tar.gz \
    && curl -L --retry 5 --retry-all-errors https://github.com/madler/zlib/archive/refs/tags/v1.3.1.tar.gz -o /opt/vcpkg/downloads/madler-zlib-v1.3.1.tar.gz \
    && curl -L --retry 5 --retry-all-errors https://github.com/ninja-build/ninja/releases/download/v1.13.2/ninja-linux.zip -o /opt/vcpkg/downloads/ninja-linux-1.13.2.zip \
    && curl -L --retry 5 --retry-all-errors https://github.com/NixOS/patchelf/releases/download/0.15.5/patchelf-0.15.5-x86_64.tar.gz -o /opt/vcpkg/downloads/patchelf-0.15.5-x86_64.tar.gz \
    && curl -L --retry 5 --retry-all-errors https://github.com/nlohmann/json/archive/v3.12.0.tar.gz -o /opt/vcpkg/downloads/nlohmann-json-v3.12.0.tar.gz \
    && curl -L --retry 5 --retry-all-errors https://github.com/uNetworking/uSockets/archive/v0.8.8.tar.gz -o /opt/vcpkg/downloads/uNetworking-uSockets-v0.8.8.tar.gz \
    && curl -L --retry 5 --retry-all-errors https://github.com/uNetworking/uWebSockets/archive/v20.76.0.tar.gz -o /opt/vcpkg/downloads/uNetworking-uWebSockets-v20.76.0.tar.gz

RUN /opt/vcpkg/vcpkg install --triplet x64-linux

RUN cmake -S /app -B /app/build/linux -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_TOOLCHAIN_FILE=/opt/vcpkg/scripts/buildsystems/vcpkg.cmake \
    -DVCPKG_TARGET_TRIPLET=x64-linux

RUN cmake --build /app/build/linux --config Release --target wikilive_backend

ENV ENABLE_AI=false
ENV WIKILIVE_BACKEND_URL=http://127.0.0.1:3000
ENV PYTHONUNBUFFERED=1

EXPOSE 3000 8501

CMD ["/bin/bash", "-lc", "/app/build/linux/wikilive_backend & python3 -m streamlit run /app/frontend/app.py --server.headless true --server.port 8501"]
