FROM python:3

RUN pip install dnspython cryptography

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/redns

WORKDIR /app/redns/

COPY redns/__init__.py redns/nameservers.py redns/redns.py /app/redns/
COPY redns/algorithms/* /app/redns/algorithms/
COPY redns/log/* /app/redns/log/
COPY redns/ns/* /app/redns/ns/
COPY redns/resolver/* /app/redns/resolver/


EXPOSE 53535
EXPOSE 53535/udp

CMD ["python", "algorithms/scanner.py"]
