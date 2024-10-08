FROM python:3

RUN pip install dnspython cryptography

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/redns


VOLUME . /app/redns

EXPOSE 53535

CMD ["python3", "/app/redns/algorithms/majVote.py"]
