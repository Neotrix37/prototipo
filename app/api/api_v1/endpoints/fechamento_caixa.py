from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.db.database import get_db
from app.models.fechamento_caixa import FechamentoCaixa, FormaPagamento, FechamentoFormaPagamento
from app.schemas.caixa import (
    FechamentoCaixaCreate, FechamentoCaixa as FechamentoCaixaSchema,
    FechamentoCaixaUpdate, FechamentoFormaPagamento as FechamentoFormaPagamentoSchema,
    FormaPagamento as FormaPagamentoSchema, FormaPagamentoCreate, FormaPagamentoUpdate
)
from app.core.security import get_current_active_user
from app.models.usuario import Usuario

router = APIRouter()

# Endpoints para Fechamento de Caixa
@router.post("/fechamentos/", response_model=FechamentoCaixaSchema, status_code=status.HTTP_201_CREATED)
def criar_fechamento(
    fechamento: FechamentoCaixaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Cria um novo fechamento de caixa.
    """
    try:
        # Verificar se já existe um fechamento em aberto
        fechamento_aberto = db.query(FechamentoCaixa).filter(
            FechamentoCaixa.status == 'Aberto'
        ).first()
        
        if fechamento_aberto:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um fechamento em aberto. Finalize-o antes de criar um novo."
            )
        
        # Calcular a diferença
        diferenca = fechamento.valor_informado - fechamento.valor_sistema
        
        # Criar o fechamento
        db_fechamento = FechamentoCaixa(
            valor_sistema=fechamento.valor_sistema,
            valor_informado=fechamento.valor_informado,
            diferenca=diferenca,
            observacoes=fechamento.observacoes,
            status="Aberto",
            usuario_id=current_user.id
        )
        
        db.add(db_fechamento)
        db.flush()  # Para obter o ID do fechamento
        
        # Adicionar as formas de pagamento
        for fp in fechamento.formas_pagamento:
            forma_pagamento = db.query(FormaPagamento).get(fp.forma_pagamento_id)
            if not forma_pagamento:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Forma de pagamento com ID {fp.forma_pagamento_id} não encontrada"
                )
            
            db_fp = FechamentoFormaPagamento(
                fechamento_id=db_fechamento.id,
                forma_pagamento_id=fp.forma_pagamento_id,
                valor=fp.valor
            )
            db.add(db_fp)
        
        db.commit()
        db.refresh(db_fechamento)
        return db_fechamento.to_dict()
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar fechamento: {str(e)}"
        )

@router.put("/fechamentos/{fechamento_id}", response_model=FechamentoCaixaSchema)
def atualizar_fechamento(
    fechamento_id: int,
    fechamento_update: FechamentoCaixaUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Atualiza um fechamento de caixa existente.
    """
    db_fechamento = db.query(FechamentoCaixa).filter(FechamentoCaixa.id == fechamento_id).first()
    if not db_fechamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fechamento não encontrado"
        )
    
    # Apenas permitir atualização se estiver aberto
    if db_fechamento.status != 'Aberto':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Só é possível atualizar fechamentos com status 'Aberto'"
        )
    
    try:
        # Atualizar campos
        if fechamento_update.observacoes is not None:
            db_fechamento.observacoes = fechamento_update.observacoes
        
        if fechamento_update.status:
            db_fechamento.status = fechamento_update.status
            if fechamento_update.status == 'Finalizado':
                db_fechamento.data_fechamento = datetime.utcnow()
        
        db.commit()
        db.refresh(db_fechamento)
        return db_fechamento.to_dict()
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar fechamento: {str(e)}"
        )

@router.get("/fechamentos/", response_model=List[FechamentoCaixaSchema])
def listar_fechamentos(
    status: Optional[str] = None,
    data_inicio: Optional[datetime] = None,
    data_fim: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Lista os fechamentos de caixa com filtros opcionais.
    """
    try:
        query = db.query(FechamentoCaixa).options(
            joinedload(FechamentoCaixa.usuario),
            joinedload(FechamentoCaixa.formas_pagamento).joinedload(FechamentoFormaPagamento.forma_pagamento)
        )
        
        # Aplicar filtros
        if status:
            query = query.filter(FechamentoCaixa.status == status)
        if data_inicio:
            query = query.filter(FechamentoCaixa.data_fechamento >= data_inicio)
        if data_fim:
            query = query.filter(FechamentoCaixa.data_fechamento <= data_fim)
        
        # Ordenar e paginar
        fechamentos = query.order_by(
            FechamentoCaixa.data_fechamento.desc()
        ).offset(skip).limit(limit).all()
        
        # Log para depuração
        print("\n=== DEBUG: Fechamentos encontrados ===")
        for i, f in enumerate(fechamentos):
            print(f"\nFechamento {i+1}:")
            print(f"ID: {f.id}")
            print(f"Valor Sistema: {f.valor_sistema}")
            print(f"Valor Informado: {f.valor_informado}")
            print(f"Status: {f.status}")
            print(f"Usuário: {f.usuario.nome if f.usuario else 'N/A'}")
            print(f"Formas de Pagamento: {len(f.formas_pagamento) if f.formas_pagamento else 0}")
            
            # Verificar serialização
            try:
                fechamento_dict = f.to_dict()
                print("Serialização bem-sucedida!")
                # Verificar estrutura do usuário
                if 'usuario' in fechamento_dict:
                    print(f"Usuário no dict: {fechamento_dict['usuario']}")
                # Verificar formas de pagamento
                if 'formas_pagamento' in fechamento_dict:
                    print(f"Formas de pagamento no dict: {fechamento_dict['formas_pagamento']}")
            except Exception as e:
                print(f"Erro na serialização: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Retornar os fechamentos convertidos para dicionário
        return [f.to_dict() for f in fechamentos]
        
    except Exception as e:
        # Log detalhado do erro
        print(f"\n=== ERRO NO ENDPOINT listar_fechamentos ===")
        print(f"Tipo do erro: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Retornar erro 500 com detalhes
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Erro ao listar fechamentos",
                "type": type(e).__name__,
                "message": str(e)
            }
        )

@router.get("/fechamentos/{fechamento_id}", response_model=FechamentoCaixaSchema)
def obter_fechamento(
    fechamento_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtém os detalhes de um fechamento de caixa específico.
    """
    fechamento = db.query(FechamentoCaixa).filter(FechamentoCaixa.id == fechamento_id).first()
    if not fechamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fechamento não encontrado"
        )
    
    return fechamento.to_dict()

# Endpoints para Formas de Pagamento
@router.post("/formas-pagamento/", response_model=FormaPagamentoSchema, status_code=status.HTTP_201_CREATED)
def criar_forma_pagamento(
    forma_pagamento: FormaPagamentoCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Cria uma nova forma de pagamento.
    """
    try:
        db_forma_pagamento = FormaPagamento(
            nome=forma_pagamento.nome,
            ativo=forma_pagamento.ativo
        )
        
        db.add(db_forma_pagamento)
        db.commit()
        db.refresh(db_forma_pagamento)
        return db_forma_pagamento.to_dict()
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar forma de pagamento: {str(e)}"
        )

@router.put("/formas-pagamento/{forma_pagamento_id}", response_model=FormaPagamentoSchema)
def atualizar_forma_pagamento(
    forma_pagamento_id: int,
    forma_pagamento_update: FormaPagamentoUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Atualiza uma forma de pagamento existente.
    """
    db_forma_pagamento = db.query(FormaPagamento).filter(FormaPagamento.id == forma_pagamento_id).first()
    if not db_forma_pagamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forma de pagamento não encontrada"
        )
    
    try:
        if forma_pagamento_update.nome is not None:
            db_forma_pagamento.nome = forma_pagamento_update.nome
        if forma_pagamento_update.ativo is not None:
            db_forma_pagamento.ativo = forma_pagamento_update.ativo
        
        db.commit()
        db.refresh(db_forma_pagamento)
        return db_forma_pagamento.to_dict()
        
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar forma de pagamento: {str(e)}"
        )

@router.get("/formas-pagamento/", response_model=List[FormaPagamentoSchema])
def listar_formas_pagamento(
    ativo: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_active_user)
):
    """
    Lista as formas de pagamento disponíveis.
    """
    query = db.query(FormaPagamento)
    
    # Aplicar filtros
    if ativo is not None:
        query = query.filter(FormaPagamento.ativo == ativo)
    
    # Ordenar e paginar
    formas_pagamento = query.order_by(
        FormaPagamento.nome
    ).offset(skip).limit(limit).all()
    
    return [fp.to_dict() for fp in formas_pagamento]
