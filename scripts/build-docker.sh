docker build . \
  -t xtube:latest \
  --build-arg http_proxy=$http_proxy \
  --build-arg https_proxy=$http_proxy \
  --network host
