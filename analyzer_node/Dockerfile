# syntax=docker/dockerfile:1

# reference guide at https://docs.docker.com/engine/reference/builder/

FROM alpine:3.17


### 2. Get Java via the package manager
RUN  apk update \ 
  && apk upgrade \
  && apk add ca-certificates \
  && update-ca-certificates \
  && apk add --update coreutils && rm -rf /var/cache/apk/*   \ 
  && apk add --update openjdk11 tzdata curl unzip bash \
  && apk add --no-cache nss 

# and maven (requirement for dependency check)
RUN apk add --no-cache maven

# add npm, pnpm, yarn and go
RUN apk --no-cache add curl && \
curl -L https://unpkg.com/@pnpm/self-installer &&\
apk add nodejs npm && \
npm install --global yarn && \
apk add go 

# install dependencies and core runtime as it includes both .NET and ASP.NET Core runtimes. and don't install JDK
# cause we won#t develop an .NET app but only run (only runtime is needed)
RUN apk add bash icu-libs krb5-libs libgcc libintl libssl1.1 libstdc++ zlib libgdiplus && \
apk add aspnetcore6-runtime

### 3. Get Python, PIP
RUN apk add --no-cache python3 \
&& python3 -m ensurepip \
&& pip3 install --upgrade pip setuptools \
&& rm -r /usr/lib/python*/ensurepip && \
if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
rm -r /root/.cache

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

## 4. Get Git
# install git # prerequisite for gitpython
RUN apk add git 


WORKDIR /app

# eport env variable to use dependency check from anywhere in container
 ENV PATH="${PATH}:/app/dependency-check/bin"


# download dependency check cli and update database of dependency check every time container starts
RUN apk add zip && \
    VERSION=$(curl -s https://jeremylong.github.io/DependencyCheck/current.txt) && \
    curl -Ls "https://github.com/jeremylong/DependencyCheck/releases/download/v$VERSION/dependency-check-$VERSION-release.zip" --output dependency-check.zip && \
    unzip dependency-check.zip && \
    dependency-check.sh --updateonly


# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt


# Copy the source code into the container.
COPY . .

# Run the application.
CMD ["python3", "rmq_receive_analyze.py"]
