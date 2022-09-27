# Run CMS-ML using Docker

**CMS-ML** is prepared to be run using [Docker](https://docker.com/).

## Runing CMS-ML docker on a local environment

These are the steps needed to start a Docker container locally that runs a [Jupyter Notebook](
https://jupyter.org/) already configured to run CMS-ML.

### 1. Create a Github Token

First you will need to have a Github account and access to the [CMS-ML](
https://github.com/signals-dev/CMS-ML) repository. Then, you will need to create a GitHub token
in order to be able to read / write from the repository's packages. To achieve so visit the
following [link](https://github.com/settings/tokens) and:

1. Click on `Generate new token`.
2. On `Note` introduce a desired name (for example Docker).
3. Select the options `write:pakcages` and `read:packages`.
4. Click the `Generate token`.

Make sure to copy the token displayed as it will disappear after you close the tab or navigate to
another web page. Save the token in a `txt` file on a reachable for you folder.

### 2. Pulling the docker image

In order to pull the docker image, we will have to login using the previously saved `txt` file.
To do so, simply run the following command replacing the `txt` file location and the github
username with the one that you used to generate the token.

```bash
cat /path/to/token.txt | docker login docker.pkg.github.com -u <github_username> --password-stdin
```

If everything was correct, a `Login Successfull` message will appear on your console, and you can
pull the docker image with the following command:

```bash
docker pull docker.pkg.github.com/signals-dev/cms-ml/cms-ml:latest
```

### 4. Run the Docker image

Once you have pulled the docker image you can run the image with the following command:

```bash
docker run -ti -p8888:8888 cms-ml:latest
```

This will start a Jupyter Notebook instance on your computer already configured to use **CMS-ML**.
You can access it by pointing your browser at http://127.0.0.1:8888 .

## Run CMS-ML on Kubernetes

**CMS-ML** can also be started using [Kubernetes](https://kubernetes.io/).

Here are the minimum steps required to create a POD in a local Kubernetes cluster:

0. Pull the docker image as explained in the previous section or create your own (explained
at the end of this readme).

1. Create a POD yaml file with the these contents:

For this example, we are assuming that the yaml file is named `cms-ml-pod.yml`

```yml
apiVersion: v1
kind: Pod
metadata:
  name: cms-ml
spec:
  containers:
  - name: cms-ml
    image: cms-ml:latest
    ports:
    - containerPort: 8888
```

2. Create a POD.

After creating the yaml file, you can create a POD in your Kubernetes cluster using the `kubectl`
command:

```bash
kubectl apply -f cms-ml-pod.yml
```

3. Forward the port 8888

After the POD is started, you still need to forward a local port to it in order to access the
Jupyter instance.

```bash
kubectl port-forward cms-ml 8888
```

4. Point your browser at http://localhost:8888

## Building the Docker image from scratch

If you want to build the Docker image from scratch instaed of using the github image, you will need
to:

1. Clone the repository

```bash
git clone git@github.com:signals-dev/CMS-ML.git
cd CMS-ML
```

2. Build the docker image

Build the docker image using the CMS-ML make command:

```bash
make docker-build
```
