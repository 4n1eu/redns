FROM python:3

RUN pip install dnspython cryptography

RUN pip install PyYAML

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/redns

WORKDIR /app/redns/

COPY redns/__init__.py redns/nameservers.py redns/ns1.yaml redns/redns.py /app/redns/
COPY redns/algorithms/* /app/redns/algorithms/
COPY redns/resolver/* /app/redns/resolver/
COPY redns/log/* /app/redns/log/


EXPOSE 53535
EXPOSE 53535/udp

#CMD ["ls", "app/redns/"]
CMD ["python", "algorithms/majVote.py"]
