FROM python

COPY requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

EXPOSE 7000

COPY ./api /api

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7000", "--no-access-log"]