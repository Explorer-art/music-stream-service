FROM python:3.9
WORKDIR /code
COPY . .
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
CMD ["uvicorn", "app:app", "--host", "0.0.0.0"]