from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from connect_to_database import get_database

app = FastAPI()
database = get_database()['items']

class Produit(BaseModel):
    name: str
    description: str
    quantity: int

@app.post("/add")
async def add(produit: Produit):
    database.insert_one(produit.model_dump())
    return {"message": "added !"}

@app.put("/modify")
async def modify(produit: Produit):
    result = database.find_one_and_update(
        {"name": produit.name},
        {"$set": produit.model_dump()},
        return_document=True
    )
    
    if "_id" in result:
        del result["_id"]

    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": "Product modified successfully!", "product": result}

@app.delete("/delete/{name}")
async def delete(name: str):
    result = database.delete_one({"name": name})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": f"Product '{name}' deleted successfully!"}

@app.get("/get/{name}")
async def get(name: str):
    product = database.find_one({"name": name})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if "_id" in product:
        del product["_id"]
    
    return product