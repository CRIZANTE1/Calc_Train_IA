def calcular_nota_pontualidade(check_ins_pontuais: int, total_check_ins: int) -> float:
    """Calcula a nota de pontualidade com base no número de check-ins."""
    if total_check_ins == 0:
        return 2.0 # Retorna nota máxima se não houver check-ins definidos
    return (check_ins_pontuais / total_check_ins) * 2

def calcular_nota_interacao(interacoes_validas: int, total_oportunidades: int) -> float:
    """Calcula a nota de interação de forma proporcional."""
    if total_oportunidades == 0:
        return 2.0 # Retorna nota máxima se não houver oportunidades
    return (interacoes_validas / total_oportunidades) * 2

def calcular_nota_avaliacao(acertos: int) -> float:
    """Calcula a nota da prova final."""
    return acertos * 0.6

def determinar_status(nota_final: float, frequencia_ok: bool) -> str:
    """Determina o status final do colaborador (Aprovado/Reprovado)."""
    if not frequencia_ok:
        return "Reprovado por Frequência"
    elif nota_final >= 7.0:
        return "Aprovado"
    else:
        return "Reprovado por Nota"

def processar_dados_colaboradores(colaboradores: list, total_oportunidades: int, total_check_ins: int) -> list:
    """
    Recebe a lista de dados brutos dos colaboradores e retorna uma lista
    de dicionários com todos os cálculos e dados para o relatório.
    """
    resultados = []
    for colab in colaboradores:
        if not colab.get('nome'):
            continue

        # Dados brutos
        check_ins_pontuais = colab.get('check_ins_pontuais', 0)
        interacoes = colab.get('interacoes', 0)
        acertos = colab.get('acertos', 0)
        frequencia_ok = colab.get('frequencia', False)

        # Cálculos das notas
        nota_p = calcular_nota_pontualidade(check_ins_pontuais, total_check_ins)
        nota_i = calcular_nota_interacao(interacoes, total_oportunidades)
        nota_a = calcular_nota_avaliacao(acertos)
        
        nota_final = nota_p + nota_i + nota_a
        status = determinar_status(nota_final, frequencia_ok)

        resultados.append({
            # Dados para o relatório
            "Colaborador": colab.get('nome'),
            "Check-ins Pontuais": f"{check_ins_pontuais}/{total_check_ins}",
            "Interações Válidas": f"{interacoes}/{total_oportunidades}",
            "Acertos na Prova": f"{acertos}/10",
            "Nota Pontualidade": nota_p,
            "Nota Interação": nota_i,
            "Nota Avaliação": nota_a,
            "Nota Final": nota_final,
            "Frequência OK?": "Sim" if frequencia_ok else "Não",
            "Status": status
        })
    return resultados
