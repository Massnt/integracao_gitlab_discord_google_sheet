from dotenv import load_dotenv
from gspread.utils import ValueInputOption
from gspread.utils import rowcol_to_a1
from datetime import datetime
import gspread
import os
import pandas as pd
import locale


class PlanilhaGoogle:
    def __init__(self):
        load_dotenv()
        locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        
        self._gc = gspread.service_account(filename=os.getenv('PATH_CREDENCIAIS'))
        self._planilha = self._gc.open_by_url(os.getenv('PLANILHA_URL'))
        self._resumo = self._planilha.sheet1
        
        try:
            self._pagina_mes = self._planilha.worksheet(datetime.now().strftime('%B').upper())
        except :
            self._pagina_mes = self._planilha.add_worksheet(datetime.now().strftime('%B').upper(), 10, 5, 1)
            self._pagina_mes.insert_rows([['Sem Teste'], ['Com Teste'], ['Dia', 'Descrição', 'Autor', 'Falta Teste', '']])
            self._pagina_mes.merge_cells('A1:B1')
            self._pagina_mes.merge_cells('A2:B2')
            
        self._planilha.worksheet
    
    @property
    def coluna_mes(self):
        return self._resumo.find(self._pagina_mes.title)
    
    
    def set_dataframe(self, dataframe : pd.DataFrame):
        return self._resumo.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())
        
        
    def mudar_cor_linha(self, linha: int, red: float, green: float, blue: float):
        cor = {
            "red": red,
            "green": green,
            "blue": blue
        }

        requests = [{
            "repeatCell": {
                "range": {
                    "sheetId": self._pagina_mes.id,
                    "startRowIndex": linha - 1,  
                    "endRowIndex": linha,       
                },
                "cell": {
                    "userEnteredFormat": {
                        "backgroundColor": cor
                    }
                },
                "fields": "userEnteredFormat.backgroundColor"
            }
        }]

        return self._planilha.batch_update({"requests": requests})
        
        
    def prepend_dataframe(self, dataframe: pd.DataFrame):
        return self._pagina_mes.insert_row(dataframe.values.tolist()[0], int(os.getenv('INICIO_PLANILHA')))
    
        
    def append_dataframe(self, dataframe: pd.DataFrame):
        if self._pagina_mes.row_count == 0:
            data = [dataframe.columns.values.tolist()] + dataframe.values.tolist()
        else:
            data = dataframe.values.tolist()

        return self._pagina_mes.append_rows(data, value_input_option='RAW')
        

    def add_coluna_mes(self):
        if not self.coluna_mes:
            dados_coluna = [
                f'=COUNTIFS({self._pagina_mes.title}!C:C; A{i}; {self._pagina_mes.title}!D:D; TRUE)' 
                if i % 2 == 0 
                else f'=COUNTIF({self._pagina_mes.title}!C:C; A{i-1})' for i in range(2,24)
                ]
            all_values = self._resumo.get_all_values()

            if not all_values:
                return 0

            colunas = list(zip(*all_values))
            colunas_preenchidas = sum(1 for col in colunas if any(cell.strip() for cell in col))

            self._resumo.insert_cols([[self._pagina_mes.title] + dados_coluna], 
                                      value_input_option=ValueInputOption.user_entered, 
                                      col=colunas_preenchidas+1)
            
            coluna_inserida_letra = rowcol_to_a1(1, colunas_preenchidas + 1)[0]
            somas = self._resumo.range(f'{coluna_inserida_letra}26:{coluna_inserida_letra}27')
            somas[0].value = f'=SOMA(arrayformula(SE(ÉPAR(LIN({coluna_inserida_letra}2:{coluna_inserida_letra}23))=VERDADEIRO;{coluna_inserida_letra}2:{coluna_inserida_letra}23;"")))'
            somas[1].value = f'=SOMA(arrayformula(SE(ÉIMPAR(LIN({coluna_inserida_letra}2:{coluna_inserida_letra}23))=VERDADEIRO;{coluna_inserida_letra}2:{coluna_inserida_letra}23;"")))'

            self._resumo.update_cells(somas, value_input_option=ValueInputOption.user_entered)