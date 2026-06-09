import os

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from config import DB_NAME

MONGO_URI = os.getenv("MONGO_URI")


client = MongoClient(
    MONGO_URI,
    server_api=ServerApi("1"),
)

db = client[DB_NAME]

student_collection = db["student"]
teacher_collection = db["teacher"]
evaluations_collection = db["evaluations"]


def get_student_collection():
    return student_collection


def get_teacher_collection():
    return teacher_collection


def get_evaluations_collection():
    return evaluations_collection