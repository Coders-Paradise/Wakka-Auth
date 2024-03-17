# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.12

EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

ENV PATH="/scripts:$PATH"

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install -r requirements.txt

COPY run.sh /scripts/
COPY . /app

RUN adduser -u 5678 --disabled-password --gecos "" appuser \
    && chown -R appuser /app \
    && chown -R appuser /scripts/ \
    && chmod +x /scripts/run.sh \
    && chown -R appuser:appuser /app
USER appuser


CMD ["run.sh"]
