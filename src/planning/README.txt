install VScode extension: https://marketplace.visualstudio.com/items?itemName=jan-dolejsi.pddl
install docker

> docker run -it --privileged -p 5555:5555 aiplanning/planutils:latest bash

Inside the container:
  > pip install flask
  > planutils install lpg-td
  > planutils server --host 0.0.0.0 --port 5555
