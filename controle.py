from PyQt5 import uic, QtWidgets
import mysql.connector
from reportlab.pdfgen import canvas

# Função para conectar ao banco de dados
def conectar_banco():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="cadastro_produtos"
    )

# Função para executar uma consulta no banco de dados
def consultar(query, params=None):
    connection = conectar_banco()
    cursor = connection.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    result = cursor.fetchall()
    connection.close()
    return result

# Função para executar uma consulta de modificação no banco de dados
def modificar(query, params=None):
    connection = conectar_banco()
    cursor = connection.cursor()
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    connection.commit()
    connection.close()

# Função para preencher a segunda tela com os dados do banco de dados
def preencher_segunda_tela():
    dados = consultar("SELECT * FROM produtos")
    segunda_tela.tableWidget.setRowCount(len(dados))
    segunda_tela.tableWidget.setColumnCount(5)
    for i, linha in enumerate(dados):
        for j, valor in enumerate(linha):
            segunda_tela.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(valor)))

# Função para preencher o formulário de edição com os dados selecionados
def editar_dados():
    global numero_id

    linha = segunda_tela.tableWidget.currentRow()
    dados_id = consultar("SELECT id FROM produtos")
    valor_id = dados_id[linha][0]
    produto = consultar("SELECT * FROM produtos WHERE id = %s", (valor_id,))
    tela_editar.show()

    # Atualizar o valor global do número do ID
    numero_id = valor_id

    # Preencher os campos de edição com os dados do produto selecionado
    tela_editar.lineEdit_2.setText(str(produto[0][1]))
    tela_editar.lineEdit_3.setText(str(produto[0][2]))
    tela_editar.lineEdit_4.setText(str(produto[0][3]))
    tela_editar.lineEdit_5.setText(str(produto[0][4]))

# Função para salvar os valores editados
def salvar_valor_editado():
    global numero_id

    codigo = tela_editar.lineEdit_2.text()
    descricao = tela_editar.lineEdit_3.text()
    preco = tela_editar.lineEdit_4.text()
    categoria = tela_editar.lineEdit_5.text()

    modificar("UPDATE produtos SET codigo = %s, descricao = %s, preco = %s, categoria = %s WHERE id = %s",
              (codigo, descricao, preco, categoria, numero_id))

    tela_editar.close()
    segunda_tela.close()
    preencher_segunda_tela()

# Função para excluir dados selecionados
def excluir_dados():
    linha = segunda_tela.tableWidget.currentRow()
    dados_id = consultar("SELECT id FROM produtos")
    valor_id = dados_id[linha][0]
    modificar("DELETE FROM produtos WHERE id = %s", (valor_id,))
    segunda_tela.tableWidget.removeRow(linha)

# Função para gerar um PDF com os dados do banco de dados
def gerar_pdf():
    dados = consultar("SELECT * FROM produtos")
    pdf = canvas.Canvas("cadastro_produtos.pdf")
    pdf.setFont("Times-Bold", 25)
    pdf.drawString(200, 800, "Produtos cadastrados:")
    pdf.setFont("Times-Bold", 18)
    pdf.drawString(10, 750, "ID")
    pdf.drawString(110, 750, "CODIGO")
    pdf.drawString(210, 750, "PRODUTO")
    pdf.drawString(310, 750, "PREÇO")
    pdf.drawString(410, 750, "CATEGORIA")
    y = 0
    for linha in dados:
        y += 50
        for j, valor in enumerate(linha):
            pdf.drawString(10 + j * 100, 750 - y, str(valor))
    pdf.save()
    print("PDF FOI GERADO COM SUCESSO!")

# Função principal
def funcao_principal():
    linha1 = formulario.lineEdit.text()
    linha2 = formulario.lineEdit_2.text()
    linha3 = formulario.lineEdit_3.text()
    categoria = ""
    if formulario.radioButton.isChecked():
        categoria = "Eletronicos"
    elif formulario.radioButton_2.isChecked():
        categoria = "Alimentos"
    else:
        categoria = "Informatica"
    modificar("INSERT INTO produtos (codigo, descricao, preco, categoria) VALUES (%s, %s, %s, %s)",
              (linha1, linha2, linha3, categoria))
    formulario.lineEdit.setText("")
    formulario.lineEdit_2.setText("")
    formulario.lineEdit_3.setText("")
    preencher_segunda_tela()

# Função para exibir a segunda tela
def chama_segunda_tela():
    segunda_tela.show()
    preencher_segunda_tela()

app = QtWidgets.QApplication([])
formulario = uic.loadUi("formulario.ui")
segunda_tela = uic.loadUi("listar_dados.ui")
tela_editar = uic.loadUi("menu_editar.ui")
numero_id = 0

# Conectar sinais aos slots
formulario.pushButton.clicked.connect(funcao_principal)
formulario.pushButton_2.clicked.connect(chama_segunda_tela)
segunda_tela.pushButton.clicked.connect(gerar_pdf)
segunda_tela.pushButton_2.clicked.connect(excluir_dados)
segunda_tela.pushButton_3.clicked.connect(editar_dados)
tela_editar.pushButton.clicked.connect(salvar_valor_editado)

# Exibir o formulário principal
formulario.show()
app.exec()