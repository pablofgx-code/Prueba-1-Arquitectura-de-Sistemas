from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Sistema de Donaciones Iglesia")

@app.get("/")
def read_root():
    return {"mensaje": "¡El backend de la iglesia está funcionando perfectamente!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)