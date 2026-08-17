from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets


app = FastAPI()

MEU_USUARIO = "Admin"
MINHA_SENHA = "Admin"

security = HTTPBasic()

lista_tarefas = []


class Tarefa(BaseModel):
    nome: str
    descricao: str
    concluida: bool | None = False


def autenticar_meu_usuario(credentials: HTTPBasicCredentials = Depends(security)):
    is_correct_username = secrets.compare_digest(credentials.username, MEU_USUARIO)
    is_correct_password = secrets.compare_digest(credentials.password, MINHA_SENHA)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=401,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/tarefas")
def listar_tarefas(
    page: int = 1,
    limit: int = 10,
    username: str = Depends(autenticar_meu_usuario)
):
    if page < 1 or limit < 1:
        raise HTTPException(
            status_code=400,
            detail="Parâmetros de página e limite devem ser maiores que zero."
        )

    if not lista_tarefas:
        return {"mensagem": "Nenhuma tarefa encontrada."}

    start_index = (page - 1) * limit
    end_index = start_index + limit
    tarefas_paginadas = lista_tarefas[start_index:end_index]

    return {
        "mensagem": "Tarefas listadas com sucesso.",
        "tarefas": tarefas_paginadas,
        "pagina": page,
        "limite": limit,
        "total": len(lista_tarefas)
    }


@app.post("/adicionar")
def adiciona_tarefa(
    tarefa: Tarefa,
    username: str = Depends(autenticar_meu_usuario)
):
    for t in lista_tarefas:
        if t.nome == tarefa.nome:
            return {"mensagem": "Tarefa já existe."}
    lista_tarefas.append(tarefa)

    return {"mensagem": "Tarefa adicionada com sucesso.", "tarefa": tarefa}


@app.put("/concluir/{nome}")
def concluir_tarefa(
    nome: str,
    username: str = Depends(autenticar_meu_usuario)
):
    for tarefa in lista_tarefas:
        if tarefa.nome == nome:
            tarefa.concluida = True
            return {"mensagem": "Tarefa concluída com sucesso.", "tarefa": tarefa}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada.")


@app.delete("/remover/{nome}")
def remover_tarefa(
    nome: str,
    username: str = Depends(autenticar_meu_usuario)
):
    for tarefa in lista_tarefas:
        if tarefa.nome == nome:
            lista_tarefas.remove(tarefa)
            return {"mensagem": "Tarefa removida com sucesso.", "tarefa": tarefa}
    raise HTTPException(status_code=404, detail="Tarefa não encontrada.")