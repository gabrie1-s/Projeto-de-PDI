# Sistema para Detecção de Defeitos em Tecido Jeans

O projeto original pode ser econtrado em nosso repositório do [gitlab](https://gitlab.com/gabrie1/projeto-de-pdi). 
Lá é possível encontrar os arquivos de vídeo gerados, os quais não puderam ser adicionados  a este repositório em virtude do tamanho.

<img src=".\Usage.gif" height = "520" alt="" align=center />

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

## Detecção
### Preprocessamento
1. **Correção de Brilho:** Cria uma tabela de mapeamento que ajusta o brilho da imagem com uma função exponencial (a potência de 0.2). Isso torna a imagem mais clara;
2. **Conversão para Escala de Cinza:** Converte a imagem ajustada para tons de cinza;
3. **Suavização:** Aplica um filtro gaussiano para suavizar a imagem e reduzir o ruído;
4. **Detecção de Bordas com Filtro Laplaciano:** Aplica um filtro Laplaciano, que realça as bordas da imagem;
5. **Equalização de Histograma:** Realça o contraste da imagem, distribuindo melhor os níveis de brilho;
6. **Suavização com Filtro de Média:** Aplica filtro de média para suavizar novamente a imagem;
7. **Limiarização Binária:** Converte a imagem para uma máscara binária, onde os pixels acima de 120 ficam pretos e os demais ficam brancos;
8. **Abertura (Morfologia Matemática):** Realiza a operação de "opening" (dilatação seguida de erosão) para remover ruídos.

### Processamento
1. **Suavização:** Aplica um filtro de média com uma kernel grande (13x13), reduzindo ruídos de forma significativa;
2. **Limiarização Binária:** Converte a imagem para binária, mantendo apenas valores acima de 20 em branco e o restante em preto;
3. **Detecção de Bordas com Canny:** Detecta as bordas na imagem binarizada;
4. **Detecção de Contornos:** Encontra contornos nas bordas detectadas;
5. **Filtragem de Contornos por Comprimento:** Para cada contorno detectado, calcula o perímetro. Apenas contornos com comprimento acima de 260 são mantidos;
6. **Extração de Coordenadas de Contornos:** Para os contornos selecionados, calcula o retângulo delimitador e salva as coordenadas (x, y, w, h).

