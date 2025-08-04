# --- START OF FILE utils/pdf_generator.py ---

import streamlit as st
import base64
import requests
import io
from weasyprint import HTML, CSS
from datetime import datetime
import pandas as pd

@st.cache_data(ttl=3600)
def get_logo_base64(url: str) -> str | None:
    """Faz o download de uma imagem de uma URL, converte para base64 e a armazena em cache."""
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', 'image/png')
        encoded_string = base64.b64encode(response.content).decode('utf-8')
        return f"data:{content_type};base64,{encoded_string}"
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao baixar a logo: {e}")
        return None

def create_professional_html(df: pd.DataFrame, logo_base64: str | None, training_title: str) -> str:
    """Cria a string HTML para o relatório com um design profissional."""
    
    # --- Preparação dos Dados ---
    total_colaboradores = len(df)
    aprovados = df[df['Status'] == 'Aprovado'].shape[0]
    reprovados_nota = df[df['Status'] == 'Reprovado por Nota'].shape[0]
    reprovados_freq = df[df['Status'] == 'Reprovado por Frequência'].shape[0]
    reprovados_total = reprovados_nota + reprovados_freq
    taxa_aprovacao = (aprovados / total_colaboradores * 100) if total_colaboradores > 0 else 0

    # --- Construção da Tabela HTML ---
    table_rows = ""
    status_colors = {
        "Aprovado": "#28a745",
        "Reprovado por Nota": "#dc3545",
        "Reprovado por Frequência": "#ffc107"
    }
    status_icons = {
        "Aprovado": "✔",
        "Reprovado por Nota": "✖",
        "Reprovado por Frequência": "●"
    }

    for _, row in df.iterrows():
        status_color = status_colors.get(row['Status'], '#6c757d')
        status_icon = status_icons.get(row['Status'], '')
        
        table_rows += f"""
        <tr>
            <td class="col-colaborador">{row['Colaborador']}</td>
            <td>{row['Check-ins Pontuais']}</td>
            <td>{row['Interações Válidas']}</td>
            <td>{row['Acertos na Prova']}</td>
            <td>{row['Nota Pontualidade']:.1f}</td>
            <td>{row['Nota Interação']:.1f}</td>
            <td>{row['Nota Avaliação']:.1f}</td>
            <td class="nota-final">{row['Nota Final']:.1f}</td>
            <td>{row['Frequência OK?']}</td>
            <td style="color: {status_color}; font-weight: bold;">{status_icon} {row['Status']}</td>
        </tr>
        """
    
    # --- Estrutura HTML Principal ---
    logo_element = f'<img src="{logo_base64}" alt="Logo">' if logo_base64 else ''

    html_string = f"""
    <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body>
            <header>
                <div class="logo-container">
                    {logo_element}
                </div>
                <div class="title-container">
                    <h1>Relatório de Avaliação de Treinamento</h1>
                    <p>{training_title}</p>
                </div>
            </header>
            
            <main>
                <h2>Resumo do Desempenho</h2>
                <div class="summary-grid">
                    <div class="summary-card">
                        <h3>Participantes</h3>
                        <p class="total-value">{total_colaboradores}</p>
                    </div>
                    <div class="summary-card">
                        <h3>Aprovados</h3>
                        <p class="approved-value">{aprovados}</p>
                    </div>
                    <div class="summary-card">
                        <h3>Reprovados</h3>
                        <p class="failed-value">{reprovados_total}</p>
                        <small>Nota: {reprovados_nota} | Frequência: {reprovados_freq}</small>
                    </div>
                    <div class="summary-card">
                        <h3>Taxa de Aprovação</h3>
                        <p class="rate-value">{taxa_aprovacao:.1f}%</p>
                    </div>
                </div>

                <h2>Resultados Detalhados</h2>
                <table class="results-table">
                    <thead>
                        <tr>
                            <th class="col-colaborador">Colaborador</th>
                            <th>Check-ins</th>
                            <th>Interações</th>
                            <th>Acertos</th>
                            <th>N. Pont.</th>
                            <th>N. Inter.</th>
                            <th>N. Aval.</th>
                            <th class="nota-final">Nota Final</th>
                            <th>Freq. OK?</th>
                            <th class="col-status">Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </main>
            
            <footer>
                Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')} | Documento de Referência: 040.010.060.0999.IT
            </footer>
        </body>
    </html>
    """
    return html_string

def get_professional_css() -> str:
    """Retorna a string CSS para o relatório profissional em paisagem."""
    return """
        @page {
            size: A4 landscape;
            margin: 1.5cm;
            @bottom-center {
                content: element(footer);
                vertical-align: top;
                padding-top: 1em;
            }
        }
        
        body {
            font-family: 'Helvetica Neue', 'Arial', sans-serif;
            color: #333;
        }

        header {
            display: flex;
            align-items: center;
            border-bottom: 3px solid #00A859; /* Verde Vibra */
            padding-bottom: 15px;
        }
        .logo-container {
            flex: 0 0 150px; /* Não cresce, não encolhe, base de 150px */
        }
        .logo-container img {
            max-width: 100%;
            max-height: 60px;
        }
        .title-container {
            flex-grow: 1;
            text-align: right;
        }
        .title-container h1 {
            font-size: 24pt;
            color: #002A4D; /* Azul Vibra */
            margin: 0;
            font-weight: 300; /* Fonte mais leve */
        }
        .title-container p {
            font-size: 14pt;
            color: #555;
            margin: 5px 0 0 0;
        }

        main {
            margin-top: 25px;
        }

        h2 {
            font-size: 16pt;
            color: #002A4D;
            border-bottom: 1px solid #ddd;
            padding-bottom: 8px;
            margin-bottom: 20px;
            font-weight: 400;
        }

        .summary-grid {
            display: flex;
            justify-content: space-between;
            gap: 20px;
        }
        .summary-card {
            flex-grow: 1;
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        .summary-card h3 {
            margin: 0 0 10px 0;
            font-size: 12pt;
            color: #005a8c;
            font-weight: 500;
        }
        .summary-card p {
            margin: 0;
            font-size: 28pt;
            font-weight: 700;
        }
        .summary-card small {
            font-size: 9pt;
            color: #6c757d;
        }
        .summary-card .approved-value { color: #00A859; }
        .summary-card .failed-value { color: #dc3545; }
        .summary-card .rate-value { color: #002A4D; }
        .summary-card .total-value { color: #002A4D; }

        .results-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 25px;
            font-size: 9pt;
        }
        .results-table thead tr {
            background-color: #002A4D;
            color: #fff;
        }
        .results-table th {
            padding: 10px 8px;
            font-weight: 500;
            text-align: center;
        }
        .results-table tbody tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .results-table td {
            padding: 8px;
            border: 1px solid #e9ecef;
            text-align: center;
        }
        .results-table .col-colaborador {
            width: 25%;
            text-align: left;
        }
        .results-table .col-status {
            width: 20%;
        }
        .results-table .nota-final {
            font-weight: bold;
            background-color: rgba(0, 42, 77, 0.05); /* Fundo sutil para a nota final */
        }

        footer {
            position: running(footer);
            font-size: 8pt;
            color: #777;
            text-align: center;
        }
    """

def generate_pdf_report(df, logo_url: str, training_title: str) -> io.BytesIO:
    """Função principal que orquestra a criação do relatório em PDF."""
    
    logo_base64 = get_logo_base64(logo_url)
    html_content = create_professional_html(df, logo_base64, training_title)
    
    css_string = get_professional_css()
    css = CSS(string=css_string)
    
    pdf_file = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_file, stylesheets=[css])
    pdf_file.seek(0)
    
    return pdf_file
