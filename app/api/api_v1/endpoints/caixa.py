from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.database import get_db
from app.models.caixa import MovimentacaoCaixa, RetiradaCaixa, StatusRetirada
from app.schemas.caixa import (
    MovimentacaoCaixaCreate, MovimentacaoCaixa as MovimentacaoCaixaSchema,
    RetiradaCaixaCreate, RetiradaCaixa as RetiradaCaixaSchema,
    RetiradaCaixaAprovar
)
from app.core.security import get_current_active_user
from app.models.usuario import Usuario
from datetime import time
from pydantic import BaseModel
from typing import Dict, Any

class FechamentoCaixaResponse(BaseModel):
    data_fechamento: datetime
    saldo_inicial: float
    total_entradas: float
    total_saidas: float
    saldo_final: float
    total_retiradas: float
    saldo_atual: float
    movimentacoes: list[Dict[str, Any]]

router = APIRouter()

# Endpoints para Movimentações de Caixa
@router.post("/movimentacoes/", response_model=MovimentacaoCaixaSchema, status_code=status.HTTP_201_CREATED)
def criar_movimentacao(
    movimentacao: MovimentacaoCaixaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Registra uma nova movimentação de caixa (entrada ou saída).
    """
    try:
        # A validação do tipo já é feita pelo Pydantic no schema
        db_movimentacao = MovimentacaoCaixa(
            tipo=movimentacao.tipo.upper(),  # Garante que o tipo esteja em maiúsculas
            valor=movimentacao.valor,
            descricao=movimentacao.descricao,
            observacao=movimentacao.observacao,
            usuario_id=current_user.id
        )
        
        db.add(db_movimentacao)
        db.commit()
        db.refresh(db_movimentacao)
        return db_movimentacao.to_dict()
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar movimentação: {str(e)}"
        )

@router.get("/movimentacoes/", response_model=List[MovimentacaoCaixaSchema])
def listar_movimentacoes(
    tipo: Optional[str] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Lista as movimentações de caixa com filtros opcionais.
    """
    query = db.query(MovimentacaoCaixa).join(Usuario)
    
    # Aplicar filtros
    if tipo:
        query = query.filter(MovimentacaoCaixa.tipo == tipo.upper())
    if data_inicio:
        query = query.filter(MovimentacaoCaixa.data_movimentacao >= data_inicio)
    if data_fim:
        query = query.filter(MovimentacaoCaixa.data_movimentacao <= data_fim)
    
    # Ordenar e paginar
    movimentacoes = query.order_by(
        MovimentacaoCaixa.data_movimentacao.desc()
    ).offset(skip).limit(limit).all()
    
    return [m.to_dict() for m in movimentacoes]

# Endpoints para Retiradas de Caixa
@router.post("/retiradas/", response_model=RetiradaCaixaSchema, status_code=status.HTTP_201_CREATED)
def solicitar_retirada(
    retirada: RetiradaCaixaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Solicita uma nova retirada de caixa.
    """
    try:
        db_retirada = RetiradaCaixa(
            valor=retirada.valor,
            motivo=retirada.motivo,
            observacao=retirada.observacao,
            origem=retirada.origem,
            usuario_id=current_user.id,
            status="Pendente"
        )
        
        db.add(db_retirada)
        db.commit()
        db.refresh(db_retirada)
        return db_retirada.to_dict()
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao solicitar retirada: {str(e)}"
        )

@router.post("/retiradas/{retirada_id}/aprovar", response_model=RetiradaCaixaSchema)
def aprovar_retirada(
    retirada_id: int,
    acao: RetiradaCaixaAprovar,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Aprova ou rejeita uma retirada de caixa.
    Apenas usuários com permissão podem aprovar/rejeitar.
    """
    # Verificar se o usuário tem permissão para aprovar
    if not current_user.pode_aprovar_retiradas:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para aprovar retiradas"
        )
    
    retirada = db.query(RetiradaCaixa).filter(RetiradaCaixa.id == retirada_id).first()
    if not retirada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Retirada não encontrada"
        )
    
    if retirada.status != "Pendente":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Esta retirada já foi {retirada.status}"
        )
    
    try:
        if acao.aprovar:
            retirada.status = "Aprovado"
            retirada.data_aprovacao = datetime.utcnow()
            retirada.aprovador_id = current_user.id
            
            # Registrar a saída de caixa
            movimentacao = MovimentacaoCaixa(
                tipo="SAIDA",
                valor=retirada.valor,
                descricao=f"Retirada aprovada: {retirada.motivo}",
                observacao=f"ID da retirada: {retirada.id}",
                usuario_id=current_user.id
            )
            db.add(movimentacao)
        else:
            retirada.status = "Rejeitado"
            retirada.observacao = f"{retirada.observacao or ''}\nMotivo da rejeição: {acao.motivo}"
            retirada.data_aprovacao = datetime.utcnow()
            retirada.aprovador_id = current_user.id
        
        db.commit()
        db.refresh(retirada)
        return retirada.to_dict()
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar aprovação: {str(e)}"
        )

@router.get("/retiradas/", response_model=List[RetiradaCaixaSchema])
def listar_retiradas(
    status: Optional[str] = None,
    usuario_id: Optional[int] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Lista as retiradas de caixa com filtros opcionais.
    """
    # Verificar permissões (se necessário)
    # if not current_user.pode_ver_todas_retiradas:
    #     usuario_id = current_user.id
    
    query = db.query(RetiradaCaixa)
    
    # Aplicar filtros
    if status:
        query = query.filter(RetiradaCaixa.status == status)
    if usuario_id:
        query = query.filter(RetiradaCaixa.usuario_id == usuario_id)
    if data_inicio:
        query = query.filter(RetiradaCaixa.data_retirada >= data_inicio)
    if data_fim:
        # Adiciona 1 dia para incluir o dia inteiro
        data_fim = datetime.combine(data_fim.date(), datetime.max.time())
        query = query.filter(RetiradaCaixa.data_retirada <= data_fim)
    
    # Ordenar por data de retirada (mais recentes primeiro)
    query = query.order_by(RetiradaCaixa.data_retirada.desc())
    
    # Aplicar paginação
    retiradas = query.offset(skip).limit(limit).all()
    
    # Usar o método to_dict() para cada retirada
    return [retirada.to_dict() for retirada in retiradas]

@router.get("/saldo/", response_model=float)
def obter_saldo_caixa(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtém o saldo atual do caixa.
    """
    # Calcular totais de entradas e saídas
    total_entradas = db.query(
        db.func.sum(MovimentacaoCaixa.valor)
    ).filter(
        MovimentacaoCaixa.tipo == "ENTRADA"
    ).scalar() or 0.0
    
    total_saidas = db.query(
        db.func.sum(MovimentacaoCaixa.valor)
    ).filter(
        MovimentacaoCaixa.tipo == "SAIDA"
    ).scalar() or 0.0
    
    # Calcular saldo
    saldo = total_entradas - total_saidas
    return saldo

@router.post("/fechamento/", response_model=FechamentoCaixaResponse)
def fechar_caixa(
    saldo_inicial: float = 0.0,
    data_fechamento: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Realiza o fechamento do caixa, calculando totais e gerando um relatório.
    
    - saldo_inicial: Saldo em caixa no início do período
    - data_fechamento: Data do fechamento (padrão: data/hora atual)
    """
    if not data_fechamento:
        data_fechamento = datetime.utcnow()
    
    # Iniciar transação
    try:
        # Calcular totais do dia
        inicio_dia = datetime.combine(data_fechamento.date(), time.min)
        fim_dia = datetime.combine(data_fechamento.date(), time.max)
        
        # Buscar movimentações do dia
        movimentacoes = db.query(MovimentacaoCaixa).filter(
            MovimentacaoCaixa.data_movimentacao.between(inicio_dia, fim_dia)
        ).order_by(MovimentacaoCaixa.data_movimentacao).all()
        
        # Calcular totais
        total_entradas = sum(
            m.valor for m in movimentacoes 
            if m.tipo == "ENTRADA"
        )
        
        total_saidas = sum(
            m.valor for m in movimentacoes 
            if m.tipo == "SAIDA"
        )
        
        # Calcular total de retiradas aprovadas no dia
        total_retiradas = db.query(db.func.sum(RetiradaCaixa.valor)).filter(
            RetiradaCaixa.status == "Aprovado",
            RetiradaCaixa.data_aprovacao.between(inicio_dia, fim_dia)
        ).scalar() or 0.0
        
        # Calcular saldos
        saldo_final = saldo_inicial + total_entradas - total_saidas
        saldo_atual = saldo_final - total_retiradas
        
        # Preparar resposta
        return {
            "data_fechamento": data_fechamento,
            "saldo_inicial": saldo_inicial,
            "total_entradas": total_entradas,
            "total_saidas": total_saidas,
            "saldo_final": saldo_final,
            "total_retiradas": total_retiradas,
            "saldo_atual": saldo_atual,
            "movimentacoes": [
                {
                    "id": m.id,
                    "tipo": m.tipo,
                    "valor": m.valor,
                    "descricao": m.descricao,
                    "data": m.data_movimentacao.isoformat(),
                    "usuario": m.usuario.nome if m.usuario else "Sistema"
                }
                for m in movimentacoes
            ]
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar fechamento: {str(e)}"
        )
