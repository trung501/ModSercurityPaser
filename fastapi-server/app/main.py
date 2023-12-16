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
    print(f"number: {number}, page: {page}, distinct: {distinct}, filters: {filters}")

    list_result = []
    list_msg = []
    try:
        query = db.query(ModsecLog)

        if filters:
            query = query.filter(ModsecLog.message.ilike(f"%{filters}%"))

        # if distinct == 1:
        #     query = query.distinct(ModsecLog.msg)

        log = query.order_by(ModsecLog.id.desc()).limit(number).offset((page - 1) * number).all()

        for entry in log:
            if distinct == 1 and entry.msg in list_msg:
                continue
            list_result.append({
                "id": entry.id,
                "remote_address": entry.remote_address,
                "remote_port": entry.remote_port,
                "local_address": entry.local_address,
                "local_port": entry.local_port,
                "request": entry.request,
                "time": entry.time,
                "msg": entry.msg,
                "message": entry.message
            })
            list_msg.append(entry.msg)
        del list_msg
        return list_result
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        db.close()


        
    


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)