from typing import Optional
from fastapi import FastAPI,Request,HTTPException, Depends
from pydantic import BaseModel
import time
import json
from datetime import datetime
import asyncio
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CREATE TABLE IF NOT EXISTS MODSECLOG (
#         id INTEGER PRIMARY KEY AUTOINCREMENT,
#         remote_address TEXT ,
#         remote_port TEXT,
#         local_address TEXT,
#         local_port TEXT,
#         request TEXT,
#         time TEXT,
#         msg TEXT,
#         message TEXT

SQLITE_DATABASE_URL  = "sqlite:////db/modsec.db"
engine = create_engine(SQLITE_DATABASE_URL,connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ModsecLog(Base):
    __tablename__ = "modseclog"
    id = Column(Integer, primary_key=True, index=True)
    remote_address = Column(String)
    remote_port = Column(String)
    local_address = Column(String)
    local_port = Column(String)
    request = Column(String)
    time = Column(String)
    msg = Column(String)
    message = Column(String)



@app.get("/")
def read_root():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/getlog")
def getlog(number: int = 10,page: int = 1,distinct:int=0 ,filters: str = None):
    # oreder by id desc , filter with message colume with no case sensitive, distinct by msg
    db = SessionLocal()
    try:
        if distinct == 1:
            if filters:
                log = db.query(ModsecLog).filter(ModsecLog.message.ilike(f"%{filters}%")).order_by(ModsecLog.id.desc()).distinct(ModsecLog.msg).limit(number).offset((page-1)*number).all()
            else:
                log = db.query(ModsecLog).order_by(ModsecLog.id.desc()).distinct(ModsecLog.msg).limit(number).offset((page-1)*number).all()
        else:
            if filters:
                log = db.query(ModsecLog).filter(ModsecLog.message.ilike(f"%{filters}%")).order_by(ModsecLog.id.desc()).limit(number).offset((page-1)*number).all()
            else:
                log = db.query(ModsecLog).order_by(ModsecLog.id.desc()).limit(number).offset((page-1)*number).all()
    finally:
        db.close()
    
    try:
        if log:
            for i in log:
                yield i
    finally:
        db.close()
        
    


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)