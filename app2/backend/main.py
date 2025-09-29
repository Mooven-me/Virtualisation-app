from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

class Client(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nom: str
    prenom: str
    email: str | None = None
    nombre_de_commande: int | None = None

mysql_url = "mysql+pymysql://app:ChangeMe@app2-database:3306/app"
engine = create_engine(mysql_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(title="Client Management API", version="1.0.0")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/add", response_model=Client)
async def add(client: Client, session: SessionDep):
    """Create a new client"""
    # Set ID to None to let MySQL auto-generate it
    if client.id is not None:
        client.id = None
    
    session.add(client)
    session.commit()
    session.refresh(client)
    return client

@app.put("/modify/{client_id}", response_model=Client)
async def modify(client_id: int, client: Client, session: SessionDep):
    """Update an existing client by ID"""
    db_client = session.get(Client, client_id)
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Update only provided fields
    client_data = client.model_dump(exclude_unset=True, exclude={"id"})
    db_client.sqlmodel_update(client_data)
    session.add(db_client)
    session.commit()
    session.refresh(db_client)
    return db_client

@app.delete("/delete/{client_id}")
async def delete(client_id: int, session: SessionDep):
    """Delete a client by ID"""
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    session.delete(client)
    session.commit()
    return {"message": f"Client with ID {client_id} deleted successfully"}

@app.get("/get/{client_id}", response_model=Client)
async def get(client_id: int, session: SessionDep):
    """Get a client by ID"""
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@app.get("/clients", response_model=list[Client])
async def get_all_clients(
    session: SessionDep,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return")
):
    """Get all clients with pagination"""
    statement = select(Client).offset(skip).limit(limit)
    clients = session.exec(statement).all()
    return clients

@app.get("/clients/search", response_model=list[Client])
async def search_clients(
    session: SessionDep,
    nom: str | None = Query(None, description="Search by last name"),
    prenom: str | None = Query(None, description="Search by first name"),
    email: str | None = Query(None, description="Search by email")
):
    """Search clients by name or email"""
    statement = select(Client)
    
    if nom:
        statement = statement.where(Client.nom.ilike(f"%{nom}%"))
    if prenom:
        statement = statement.where(Client.prenom.ilike(f"%{prenom}%"))
    if email:
        statement = statement.where(Client.email.ilike(f"%{email}%"))
    
    clients = session.exec(statement).all()
    return clients

@app.patch("/clients/{client_id}/orders", response_model=Client)
async def update_order_count(
    client_id: int, 
    session: SessionDep,
    increment: int = Query(..., description="Number to add to order count"),
):
    """Update the order count for a specific client"""
    client = session.get(Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    if client.nombre_de_commande is None:
        client.nombre_de_commande = 0
    
    client.nombre_de_commande += increment
    session.add(client)
    session.commit()
    session.refresh(client)
    return client

@app.get("/")
async def root():
    """API health check"""
    return {"message": "Client Management API is running", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)