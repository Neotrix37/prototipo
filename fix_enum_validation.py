from enum import Enum
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional

class MovimentacaoCaixaBase(BaseModel):
    """Base schema para movimentações de caixa."""
    tipo: str = Field(..., description="Tipo de movimentação (ENTRADA/SAIDA)")
    valor: float = Field(..., gt=0, description="Valor da movimentação")
    descricao: str = Field(..., max_length=255, description="Descrição da movimentação")
    observacao: Optional[str] = Field(None, max_length=500, description="Observações adicionais")
    
    @field_validator('tipo')
    @classmethod
    def validate_tipo(cls, v: str) -> str:
        """Valida e normaliza o tipo de movimentação para maiúsculas."""
        if not isinstance(v, str):
            raise ValueError("O tipo deve ser uma string")
        v = v.upper().strip()
        if v not in ('ENTRADA', 'SAIDA'):
            raise ValueError("Tipo de movimentação deve ser 'ENTRADA' ou 'SAIDA'")
        return v
    
    model_config = ConfigDict(from_attributes=True)

# Exemplo de uso
if __name__ == "__main__":
    # Teste de validação
    try:
        mov1 = MovimentacaoCaixaBase(
            tipo="entrada",
            valor=100.0,
            descricao="Teste de entrada"
        )
        print("Validação bem-sucedida!")
        print(f"Tipo normalizado: {mov1.tipo}")
    except Exception as e:
        print(f"Erro de validação: {e}")

    # Teste com valor inválido
    try:
        mov2 = MovimentacaoCaixaBase(
            tipo="INVALIDO",
            valor=200.0,
            descricao="Teste inválido"
        )
    except Exception as e:
        print(f"Erro esperado: {e}")