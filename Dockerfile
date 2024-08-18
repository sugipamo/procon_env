# Stage 1: Rust setup
FROM rust:latest AS rust-setup
RUN git clone https://github.com/sugipamo/cargo-compete.git
WORKDIR /cargo-compete
RUN cargo build --release

# Stage 2: Setup PyPy3
FROM pypy:3.10-slim AS pypy-setup

# Final stage
FROM python:3.10-slim

# 必要なパッケージをインストール
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    git \
    curl \
    openssh-server  # SSHサーバーをインストール

# PyPy3 をインストール
COPY --from=pypy-setup /opt/pypy /opt/pypy
COPY --from=pypy-setup /usr/local/bin/pypy3 /usr/local/bin/pypy3

# 環境変数PATHにPyPy3のパスを追加
ENV PATH="/opt/pypy/bin:$PATH"

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | \
    sh -s -- -y --default-toolchain "1.70.0"
ENV PATH="/root/.cargo/bin:$PATH"

# cargo-compete をインストール
COPY --from=rust-setup /cargo-compete/target/release/cargo-compete /usr/local/bin/cargo-compete

# .envファイルから環境変数を読み込む
# Docker Composeを使用してコンテナを起動する場合は、以下の行は不要です。
# ENV ROOT_PASSWORD=${ROOT_PASSWORD}

# SSH設定の追加
RUN mkdir /var/run/sshd && \
    echo "root:your_password" | chpasswd && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

# SSHのポートを公開
EXPOSE 22

# SSHサービスを起動
CMD ["/usr/sbin/sshd", "-D"]

# 作業ディレクトリを設定
WORKDIR /workspace
