FROM python:3-slim
EXPOSE 8080
ADD . .
RUN pip install Flask==3.0.0 pymongo[srv] Flask-PyMongo flask-cors dnspython Flask-SQLAlchemy
ENTRYPOINT [“python”]
CMD [“run.py”]
