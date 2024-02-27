#from flask import Flask,render_template,request,current_app,send_from_directory,redirect,url_for,flash,Response,jsonify
#from flask import render_template
from fastapi import FastAPI, Request, Form, Depends, Response, HTTPException, Cookie, Header
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from typing import Annotated
import uvicorn
import os
import ast
import pickle
from pathlib import Path
#from werkzeug.utils import secure_filename
import io
import random as rd
import shutil
import base64
import multiprocessing
import sass
from urllib.parse import unquote
from uuid import uuid4
from typing import Union