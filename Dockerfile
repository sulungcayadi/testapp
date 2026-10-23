FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY uipath_robotdoc ./uipath_robotdoc
RUN pip install --no-cache-dir . && useradd -m robot
USER robot
WORKDIR /work
# Mount your packages and output folder at /work:  docker run --rm -v "$PWD":/work uipath-robotdoc MyRobot.nupkg -o out
ENTRYPOINT ["uipath-robotdoc"]
