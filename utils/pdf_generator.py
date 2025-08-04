import streamlit as st
import base64
import requests
import io
from weasyprint import HTML
from datetime import datetime

@st.cache_data(ttl=3600)
def get_logo_base64(url: str) -> str | None:
    """
    Faz o download de uma imagem de uma URL, converte para base64 e a armazena em cache.
    Retorna uma string base64 pronta para ser usada em HTML/CSS.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Levanta um erro para status HTTP 4xx/5xx
        
        # Determina o tipo de imagem para o Data URI
        content_type = response.headers.get('Content-Type', 'image/svg+xml')
        encoded_string = base64.b64encode(response.content).decode('utf-8')
        
        return f"data:{content_type};base64,{encoded_string}"
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao baixar a logo: {e}")
        return None

def create_report_html(df, logo_base64: str | None, training_title: str) -> str:
    """
    Cria a string HTML completa para o relatório de treinamento.
    """
    total_colaboradores = len(df)
    aprovados = df[df['Status'] == 'Aprovado'].shape[0]
    reprovados = total_colaboradores - aprovados
    taxa_aprovacao = (aprovados / total_colaboradores * 100) if total_colaboradores > 0 else 0

    df_html = df.to_html(index=False, border=0, classes='styled-table')

    logo_element = f'<img src="{logo_base64}" class="logo">' if logo_base64 else ''

    html_string = f"""
    <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
                body {{ font-family: 'Roboto', sans-serif; color: #333; }}
                .header {{ text-align: center; border-bottom: 2px solid #005a8c; padding-bottom: 15px; }}
                .logo {{ max-width: 200px; margin-bottom: 10px; }}
                h1 {{ color: #002a4d; font-size: 24px; margin: 0; }}
                h2 {{ color: #002a4d; font-size: 20px; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-top: 25px; }}
                .summary {{ 
                    display: flex; justify-content: space-around; text-align: center; 
                    padding: 15px; background-color: #f8f9fa; border-radius: 8px; margin: 20px 0;
                }}
                .summary-item {{ flex-grow: 1; }}
                .summary-item h3 {{ margin: 0; font-size: 16px; color: #005a8c; }}
                .summary-item p {{ margin: 5px 0 0 0; font-size: 22px; font-weight: bold; }}
                .styled-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 12px; }}
                .styled-table th, .styled-table td {{ border: 1px solid #ddd; padding: 8px 10px; text-align: left; }}
                .styled-table th {{ background-color: #e9ecef; color: #002a4d; font-weight: bold; }}
                .footer {{ 
                    text-align: center; position: fixed; bottom: 0; width: 100%;
                    font-size: 10px; color: #777; border-top: 1px solid #eee; padding-top: 10px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                {logo_element}
                <h1>Relatório de Avaliação de Treinamento</h1>
                <p style="font-size: 16px; color: #555; margin-top: 5px;">{training_title}</p>
            </div>
            <h2>Resumo do Desempenho</h2>
            <div class="summary">
                <div class="summary-item"><h3>Total de Participantes</h3><p>{total_colaboradores}</p></div>
                <div class="summary-item"><h3>Aprovados</h3><p style="color: #28a745;">{aprovados}</p></div>
                <div class="summary-item"><h3>Reprovados</h3><p style="color: #dc3545;">{reprovados}</p></div>
                <div class="summary-item"><h3>Taxa de Aprovação</h3><p style="color: #005a8c;">{taxa_aprovacao:.1f}%</p></div>
            </div>
            <h2>Resultados Detalhados</h2>
            {df_html}
            <div class="footer">
                <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | IT: 040.010.060.0999.IT</p>
            </div>
        </body>
    </html>
    """
    return html_string

def generate_pdf_report(df, logo_url: str, training_title: str) -> io.BytesIO:
    """
    Função principal que orquestra a criação do relatório em PDF.
    """
    logo_base64 = get_logo_base64(logo_url)
    
    html_content = create_report_html(df, logo_base64, training_title)
    
    pdf_file = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_file)
    pdf_file.seek(0)
    
    return pdf_file
