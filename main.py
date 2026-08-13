from fastapi import FastAPI, HTTPException  # noqa: I001
from pydantic import BaseModel
from typing import Optional


app = FastAPI()

lista_tarefas = []

class Tarefa(BaseModel):
    nome: str
    descricao: str
    concluida: Optional[bool] = False  # noqa: UP045

@app.get("/tarefas")
def listar_tarefas():
    if not lista_tarefas:
        return {"mensagem": "Nenhuma tarefa encontrada."}
    return lista_tarefas

@app.post("/adicionar")
def adiciona_tarefa(tarefa: Tarefa):
    for t in lista_tarefas:
        if t.nome == tarefa.nome:
            return {"mensagem": "Tarefa já existe."}
    lista_tarefas.append(tarefa)

    return {"mensagem": "Tarefa adicionada com sucesso.", "tarefa": tarefa}

@app.put("/concluir/{nome}")
def concluir_tarefa(nome: str):
    for tarefa in lista_tarefas:
        if tarefa.nome == nome:
            tarefa.concluida = True
            return {"mensagem": "Tarefa concluída com sucesso.", "tarefa": tarefa}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada.")

@app.delete("/remover/{nome}")
def remover_tarefa(nome: str):
    for tarefa in lista_tarefas:
        if tarefa.nome == nome:
            lista_tarefas.remove(tarefa)
            return {"mensagem": "Tarefa removida com sucesso.", "tarefa": tarefa}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada.")


