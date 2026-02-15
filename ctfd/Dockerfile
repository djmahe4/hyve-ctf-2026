FROM ctfd/ctfd:latest

# Copy our custom plugin into the plugins directory
COPY ./import/plugins/DynamicXORKey /opt/CTFd/CTFd/plugins/DynamicXORKey

# Ensure permissions are correct (CTFd runs as ctfd user usually, but COPY as root is standard, 
# explicit ownership doesn't hurt)
USER root
RUN chown -R ctfd:ctfd /opt/CTFd/CTFd/plugins/DynamicXORKey
USER ctfd
