import datetime
import logging

from fastapi import FastAPI, Depends, Response, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy import Boolean, Column, String, Integer, DateTime

app = FastAPI()

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "https://localhost:8080"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SqlAlchemy Setup
load_dotenv()
DB_URL = os.getenv('DB_URL')
engine = create_engine(DB_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database schema
class ProjectVotesDB(Base):
    __tablename__ = "project_votes"

    ProjectID = Column(Integer, primary_key=True)
    ProjectName = Column(String, unique=True)
    ProjectCountry = Column(String)
    IconCode = Column(String)
    GraphColour = Column(String)
    VoteCount = Column(Integer, nullable=True)


class VoucherCodesDB(Base):
    __tablename__ = "voucher_codes"

    VoucherID = Column(Integer, primary_key=True, index=True)
    Voucher = Column(Integer, unique=True)
    ExpiryDate = Column(DateTime)
    Used = Column(Boolean, default=False)
    ProjectID = Column(Integer, nullable=True)


# API response schema
class ProjectVotes(BaseModel):
    ProjectName: str
    ProjectCountry: str
    IconCode: str
    GraphColour: str
    VoteCount: int

    class Config:
        orm_mode = True


class VoucherCodes(BaseModel):
    VoucherID: int
    Voucher: int
    ExpiryDate: datetime.datetime
    Used: bool
    ProjectID: Optional[int] = None

    class Config:
        orm_mode = True


def get_all_project_votes(db: Session):
    return db.query(ProjectVotesDB).all()


def update_project_vote_count(db: Session, proj_id: int):
    # Update the project vote count for the current project being voted for
    project_vote = db.query(ProjectVotesDB).where(ProjectVotesDB.ProjectID == proj_id).first()

    if project_vote:
        new_count = db.execute("SELECT COUNT(*) FROM voucher_codes WHERE ProjectID = %d" % proj_id).scalar()
        print("NEW COUNT " + str(new_count))
        if project_vote.VoteCount != new_count:
            project_vote.VoteCount = new_count
            db.add(project_vote)
            db.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found, please check project id is valid!"
        )


def get_voucher(db: Session, code: int):
    return db.query(VoucherCodesDB).where(VoucherCodesDB.Voucher == code).first()


def update_voucher(db: Session, code: int, proj_vote: int):
    voucher = get_voucher(db, code)

    if voucher:
        # check if voucher is still in date and has not been used
        is_not_expired = voucher.ExpiryDate != datetime.datetime.now()
        is_not_used = not voucher.Used

        if is_not_expired and is_not_used:
            voucher.ExpiryDate = datetime.datetime.now()
            voucher.Used = True
            voucher.ProjectID = proj_vote
            db.add(voucher)
            db.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Voucher code is invalid, please use another voucher"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voucher not found, please check voucher code is valid!"
        )


# Select * from project_votes;
@app.get("/projects/votes-summary/", response_model=List[ProjectVotes])
async def get_all_project_votes_view(db: Session = Depends(get_db)):
    return get_all_project_votes(db)


@app.post("/voucher/vote/")
async def post_voucher_vote_view(code: str, proj_id: int, db: Session = Depends(get_db)):
    voucher_code = int(code)
    update_voucher(db, voucher_code, proj_id)
    update_project_vote_count(db, proj_id)

    return {"message": "voting successful"}