FROM vault.habana.ai/gaudi-docker/1.21.1/rhel9.2/habanalabs/pytorch-installer-2.6.0:latest
ENV HABANA_VISIBLE_DEVICES=all
ENV OMPI_MCA_btl_vader_single_copy_mechanism=none
WORKDIR /rag_app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000


CMD ["python", "app/main.py"]