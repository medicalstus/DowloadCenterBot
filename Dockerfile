FROM python

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV PYTHONUNBUFFERED=1

CMD ["python", "bot.py"]
