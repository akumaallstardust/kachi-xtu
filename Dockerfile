FROM python:3.10.12
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# 変数設定
ARG WORK_DIR
ARG WORK_USER
ARG USER_UID=1000
ARG USER_GID=1000

# uwsgiのパスを通す
ENV PATH "$PATH:/home/$WORK_USER/.local/bin"

# ユーザーを新規作成
RUN groupadd --gid $USER_GID $WORK_USER \
    && useradd --uid $USER_UID --gid $USER_GID -m $WORK_USER \
    && apt-get update \
    && apt-get install -y sudo \
    && echo $WORK_USER ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$WORK_USER \
    && chmod 0440 /etc/sudoers.d/$WORK_USER
USER $WORK_USER

# ワークスペースを作成
RUN mkdir /home/$WORK_USER/$WORK_DIR
WORKDIR /home/$WORK_USER/$WORK_DIR
COPY . /home/$WORK_USER/$WORK_DIR

# pipライブラリをインストール&パーミッションを変更
RUN pip install --upgrade pip \
    && sudo chown -R $WORK_USER:$WORK_USER /home/$WORK_USER/$WORK_DIR\
    && pip install -r /home/$WORK_USER/$WORK_DIR/requirements.txt