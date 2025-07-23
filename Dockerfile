FROM vault.habana.ai/gaudi-docker/1.21.0/rhel9.2/habanalabs/pytorch-installer-2.6.0:latest

ENV HABANA_VISIBLE_DEVICES=all
ENV OMPI_MCA_btl_vader_single_copy_mechanism=none

WORKDIR /rag-app

# Install dependencies including sqlite-devel from system packages
RUN yum install -y \
    wget tar \
    gcc make \
    zlib-devel readline-devel \
    glibc-devel bzip2-devel xz-devel openssl-devel libffi-devel \
    sqlite-devel \
    && yum clean all


# Recompile Python’s sqlite3 module to link to the new SQLite
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install --force-reinstall --no-cache-dir pysqlite3-binary

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# CMD ["python", "app/main.py"]


# Command to run the FastAPI application using Uvicorn
# This now points to 'server:app' inside the 'app' package
# CMD ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]
# ENTRYPOINT ["uvicorn", "app.server:app", "--host", "0.0.0.0", "--port", "8000"]
ENTRYPOINT ["/bin/bash", "-c", "uvicorn app.server:app --host 0.0.0.0 --port 8000"]