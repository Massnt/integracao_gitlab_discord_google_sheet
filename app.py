from flask import Flask, request, jsonify, render_template
from datetime import datetime
from integracao_google_planilhas import PlanilhaGoogle
from discord_webhook import DiscordWebHook
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home_page():
    return render_template('home.html')
    
@app.route('/gitlab-webhook', methods=['POST'])
def gitlab_webhook():
    dados_merge = request.json
    atributos_merge = dados_merge.get('object_attributes')
    dados_coletados = {}
    planilha = PlanilhaGoogle()
    discord_webhook = DiscordWebHook()
    
    if dados_merge.get('object_kind') == 'merge_request':
        dados_coletados['dia'] = datetime.now().strftime('%d/%m/%Y')
        dados_coletados['descricao'] = atributos_merge.get('title')
        dados_coletados['autor'] = dados_merge.get('assignees')[0].get('name').split()[0]
        dados_coletados['falta_teste'] = True if 'FALTA TESTE' in atributos_merge.get('labels') else False
        dados_coletados['url'] = atributos_merge.get('url')
        
        df_novo = pd.DataFrame([dados_coletados])
        
        planilha.prepend_dataframe(df_novo)
        planilha.add_coluna_mes()
        
        
        '''if 'FEATURE' in atributos_merge.get('labels'):
            discord_webhook.envia_merge_feature(dados_coletados)'''

        return jsonify({'message': 'dados coletados com sucesso'}), 200
    
    return jsonify({"message": "não é um evento de merge"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('APP_PORT'))
