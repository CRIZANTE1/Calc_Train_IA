import streamlit as st
import base64
import requests
import io
from weasyprint import HTML, CSS
from datetime import datetime

@st.cache_data(ttl=3600)
def get_logo_base64(url: str) -> str | None:
    """
    Faz o download de uma imagem de uma URL, converte para base64 e a armazena em cache.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', 'image/png')
        encoded_string = base64.b64encode(response.content).decode('utf-8')
        
        return f"data:{content_type};base64,{encoded_string}"
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao baixar a logo: {e}")
        return None

def create_report_html(df, logo_base64: str | None, training_title: str) -> str:
    """
    Cria a string HTML para o relatório, sem o CSS do @page.
    """
    total_colaboradores = len(df)
    aprovados = df[df['Status'] == 'Aprovado'].shape[0]
    reprovados = total_colaboradores - aprovados
    taxa_aprovacao = (aprovados / total_colaboradores * 100) if total_colaboradores > 0 else 0

    # Formata as colunas numéricas para 1 casa decimal
    for col in ["Nota Pontualidade", "Nota Interação", "Nota Avaliação", "Nota Final"]:
        df[col] = df[col].apply(lambda x: f"{x:.1f}")

    df_html = df.to_html(index=False, border=0, classes='styled-table')
    logo_element = f'<img src="{logo_base64}" class="logo">' if logo_base64 else ''

    html_string = f"""
    <html>
        <head>
            <!-- O CSS principal será injetado pelo WeasyPrint -->
        </head>
        <body>
            <div class="header">
                {logo_element}
                <h1>Relatório de Avaliação de Treinamento</h1>
                <p class="training-title">{training_title}</p>
            </div>
            
            <h2>Resumo do Desempenho</h2>
            <div class="summary">
                <div class="summary-item"><h3>Total de Participantes</h3><p>{total_colaboradores}</p></div>
                <div class="summary-item"><h3>Aprovados</h3><p class="approved">{aprovados}</p></div>
                <div class="summary-item"><h3>Reprovados</h3><p class="failed">{reprovados}</p></div>
                <div class="summary-item"><h3>Taxa de Aprovação</h3><p class="approval-rate">{taxa_aprovacao:.1f}%</p></div>
            </div>
            
            <h2>Resultados Detalhados</h2>
            {df_html}
            
            <!-- O rodapé será adicionado via CSS @page -->
        </body>
    </html>
    """
    return html_string

def get_report_css() -> str:
    """Retorna a string CSS completa para estilizar o relatório PDF."""
    return """
        @page {
            size: A4;
            margin: 2cm 1.5cm 3cm 1.5cm; /* top, right, bottom, left */

            @bottom-center {
                content: element(footer);
            }
        }

        body { 
            font-family: 'Roboto', sans-serif; 
            color: #333; 
            font-size: 11pt;
        }

        .header { 
            text-align: center; 
            border-bottom: 2px solid #005a8c; 
            padding-bottom: 15px; 
            position: running(header);
        }
        .logo { 
            max-width: 180px; 
            margin-bottom: 10px; 
        }
        h1 { 
            color: #002a4d; 
            font-size: 22pt; 
            margin: 0; 
        }
        .training-title {
            font-size: 14pt;
            color: #555;
            margin-top: 5px;
        }
        
        h2 { 
            color: #002a4d; 
            font-size: 18pt; 
            border-bottom: 1px solid #eee; 
            padding-bottom: 5px; 
            margin-top: 25px; 
        }

        .summary { 
            display: flex; 
            justify-content: space-around; 
            text-align: center; 
            padding: 15px; 
            background-color: #f8f9fa; 
            border-radius: 8px; 
            margin: 20px 0;
        }
        .summary-item { 
            flex-grow: 1; 
        }
        .summary-item h3 { 
            margin: 0; 
            font-size: 12pt; 
            color: #005a8c;
            font-weight: normal;
        }
        .summary-item p { 
            margin: 5px 0 0 0; 
            font-size: 20pt; 
            font-weight: bold; 
        }
        .summary-item p.approved { color: #28a745; }
        .summary-item p.failed { color: #dc3545; }
        .summary-item p.approval-rate { color: #005a8c; }

        .styled-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 9pt;
        }
        .styled-table th, .styled-table td {
            border: 1px solid #ddd;
            padding: 6px 8px;
            text-align: center;
        }
        .styled-table th {
            background-color: #e9ecef;
            color: #002a4d;
            font-weight: bold;
        }
        .styled-table td:first-child {
            text-align: left; /* Alinha nome do colaborador à esquerda */
        }
        
        .footer {
            position: running(footer);
            text-align: center;
            font-size: 8pt; 
            color: #777; 
            border-top: 1px solid #eee; 
            padding-top: 10px;
            width: 100%;
        }
    """

def generate_pdf_report(df, logo_url: str, training_title: str) -> io.BytesIO:
    """
    Função principal que orquestra a criação do relatório em PDF.
    """
    logo_base64 = get_logo_base64(logo_url)
    html_content = create_report_html(df, logo_base64, training_title)
    
    # Adiciona o rodapé diretamente no HTML, para que o CSS possa posicioná-lo
    footer_html = f"""
    <div class="footer">
        Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | IT: 040.010.060.0999.IT
    </div>
    """
    html_content = html_content.replace("</body>", f"{footer_html}</body>")
    
    css = CSS(string=get_report_css())
    
    pdf_file = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_file, stylesheets=[css])
    pdf_file.seek(0)
    
    return pdf_file
