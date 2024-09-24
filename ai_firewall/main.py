from fastapi import FastAPI, HTTPException
import csv
from typing import List, Optional
from pydantic import BaseModel
import os

app = FastAPI()

# CSV 文件路径
CSV_FILE = "keywords.csv"


# Keyword 模型
class Keyword(BaseModel):
    id: int
    keyword: str
    deleted: bool = False


# 读取 CSV 文件并返回所有关键词
def read_csv() -> List[Keyword]:
    keywords = []
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                keywords.append(Keyword(id=int(row["id"]), keyword=row["keyword"], deleted=row["deleted"] == "True"))
    return keywords


# 将关键词列表写回到 CSV 文件
def write_csv(keywords: List[Keyword]):
    with open(CSV_FILE, mode='w', newline='') as file:
        fieldnames = ["id", "keyword", "deleted"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for keyword in keywords:
            writer.writerow({"id": keyword.id, "keyword": keyword.keyword, "deleted": keyword.deleted})


# 获取所有未删除的关键词
@app.get("/keyword_list", response_model=List[Keyword])
def get_keywords():
    keywords = [keyword for keyword in read_csv() if not keyword.deleted]
    return keywords


# 添加新关键词
@app.post("/keyword", response_model=Keyword)
def add_keyword(new_keyword: Keyword):
    keywords = read_csv()
    if any(keyword.id == new_keyword.id for keyword in keywords):
        raise HTTPException(status_code=400, detail="Keyword with this ID already exists.")
    keywords.append(new_keyword)
    write_csv(keywords)
    return new_keyword


# 更新现有关键词
@app.put("/keyword/{keyword_id}", response_model=Keyword)
def update_keyword(keyword_id: int, updated_keyword: Keyword):
    keywords = read_csv()
    for i, keyword in enumerate(keywords):
        if keyword.id == keyword_id:
            keywords[i] = updated_keyword
            write_csv(keywords)
            return updated_keyword
    raise HTTPException(status_code=404, detail="Keyword not found.")


# 删除关键词（软删除）
@app.delete("/keyword/{keyword_id}")
def delete_keyword(keyword_id: int):
    keywords = read_csv()
    for keyword in keywords:
        if keyword.id == keyword_id:
            keyword.deleted = True
            write_csv(keywords)
            return {"message": "Keyword deleted successfully."}
    raise HTTPException(status_code=404, detail="Keyword not found.")
