# Sistema para Detecção de Defeitos em Tecido Jeans

O projeto original pode ser econtrado em nosso repositório do [gitlab](https://gitlab.com/gabrie1/projeto-de-pdi). 
Lá é possível encontrar os arquivos de vídeo gerados, os quais não puderam ser adicionados  a este repositório em virtude do tamanho.

<img src=".\Usage.gif" height = "520" alt="" align=center />

## Funcionamento

## Uso
Instale as dependências
``` bash
pip install -r requirements.txt
```
Para gerar um novo vídeo, edite as informações no arquivo `pdiufc/video_generator.py`. 
Em seguida, execute
```bash
cd pdiufc
python3 video_generator.py
```
Para inicializar a aplicação execute

```bash
python3 master.py
```
Por fim, no seu navegador, acesse `localhost:5000`.
