import requests
import json
import os
import re


class DiscordWebHook:
    def __init__(self):
        self._webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        self._headers = {
            "Content-Type": "application/json"
        }
        self._username = "Luciano Hook"

    def envia_mensagem(self, mensagem):
        dados = {
            "content" : mensagem,
            "username" : self._username
        }
        
        response = requests.post(self._webhook_url, data=json.dumps(dados), headers=self._headers)

        if response.status_code == 204:
            return {
                "message": "Mensagem enviada com sucesso!",
                "status" : response.status_code
                }
        
        return response.json(), response.status_code
        
    def envia_merge_feature(self, dados_merge):
        pattern = r'\[FEATURE - (\w+)\]'
        
        match = re.search(pattern, dados_merge.get('descricao'))
        descricao = dados_merge.get("descricao").split("]")[1].removeprefix(':').replace(" ", "")

        if not match:
            return 'Não é feature'
        
        mensagem =  f'### {match.group(1) if match.group(1) else "FEATURE"} - {dados_merge.get("dia")}\n{descricao}\nFeito por: {dados_merge.get("autor")}'
        
        dados = {
            "content" : mensagem,
            "username" : self._username
        }
        
        response = requests.post(self._webhook_url, data=json.dumps(dados), headers=self._headers)

        if response.status_code == 204:
            return {
                "message": "Mensagem enviada com sucesso!",
                "status" : response.status_code
                }
        
        return response.json(), response.status_code
    
    