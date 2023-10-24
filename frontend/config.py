import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

class Config(object):
    ENV = os.environ["ENV"]
    DEBUG = os.environ["DEBUG"]
    TESTING = os.environ["TESTING"]
    SECRET_KEY = os.environ["SECRET_KEY"]
    AGENT_ENDPOINT = os.environ["AGENT_ENDPOINT"]