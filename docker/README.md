## RMTK on Docker

### How to build the container

```bash
$ docker build --rm=true -t openquake/rmtk -f Dockerfile .
```

A custom branch can be used too:

```bash
$ docker build --build-arg branch=mybranch --rm=true -t openquake/rmtk:mybranch -f Dockerfile .
```

### Start a new container

```bash
$ docker run --name rmtk -p 8888:8888 openquake/rmtk
```

A custom port can be specified if `8888` is already in use: in example `-p 8885:8888` exposes port `8885`.

### Manage an existing container

#### Stop

```bash
$ docker stop rmtk
```

#### Start

```bash
$ docker start rmtk
```

#### Attach

```bash
$ docker exec -i -t rmtk /bin/bash
```

### Debug option

A container can be made _ephemeral_ adding ``--rm``; the container will be destroyed as soon as it gets stopped.

Print Jupyter logs on screen

```bash
$ docker run --rm --name rmtk -i -t -p 8888:8888 openquake/rmtk
```

Run a debug bash console in the container

```bash
$ docker run --rm -i -t -p 8888:8888 openquake/rmtk /bin/bash
```
