from fastapi import FastAPI, HTTPException, Depends, Query
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
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(10, ge=1, le=100, description="Quantidade de itens por página"),
    ordenar_por: str | None = Query(
        None,
        description="Campo para ordenação. Valores permitidos: nome, descricao"
    ),
    username: str = Depends(autenticar_meu_usuario)
):
    # Validação de paginação
    if page < 1 or size < 1:
        raise HTTPException(
            status_code=400,
            detail="Parâmetros de página e size devem ser maiores que zero."
        )

    # Validação do campo de ordenação
    campos_permitidos = {"nome", "descricao"}
    if ordenar_por is not None and ordenar_por not in campos_permitidos:
        raise HTTPException(
            status_code=400,
            detail=f"Campo de ordenação inválido. Use um dos seguintes: {', '.join(campos_permitidos)}"
        )

    if not lista_tarefas:
        return {"mensagem": "Nenhuma tarefa encontrada."}

    # Ordenação
    tarefas_ordenadas = lista_tarefas
    if ordenar_por:
        tarefas_ordenadas = sorted(
            lista_tarefas,
            key=lambda t: getattr(t, ordenar_por).lower()
        )

    # Paginação
    start_index = (page - 1) * size
    end_index = start_index + size
    tarefas_paginadas = tarefas_ordenadas[start_index:end_index]

    return {
        "mensagem": "Tarefas listadas com sucesso.",
        "tarefas": tarefas_paginadas,
        "pagina": page,
        "size": size,
        "total": len(lista_tarefas),
        "ordenado_por": ordenar_por
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