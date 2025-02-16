from models import Conta, engine, Bancos, Status, Historico, Tipos
from sqlmodel import Session, select
from datetime import date,timedelta

def criar_conta(conta: Conta):
     with Session(engine) as session: #  gerenciador de contextos que abre e fecha sessões automaticamente
        statement = select(Conta).where(Conta.banco==conta.banco) # buscar informações do banco
        results = session.exec(statement).all() # busca que traga todos os dados
        if results:
            print("Já existe uma conta nesse banco!")
            return
        # memória temporária
        session.add(conta)
        # salvar 
        session.commit()
        return conta
    
def listar_contas():
     with Session(engine) as session:
         statement = select(Conta) # buscar todas as contas
         results = session.exec(statement).all()
     return results

def desativar_conta(id):
     with Session(engine) as session:
         statement = select(Conta).where(Conta.id == id)
         conta = session.exec(statement).first()
         if conta.valor > 0: # se tiver saldo, dá erro
             raise ValueError('Essa conta ainda possui saldo, não é possível desativar!')
         conta.status = Status.INATIVO
         session.commit()

def transferir_saldo(id_conta_saida, id_conta_entrada, valor):
     with Session(engine) as session:
         statement = select(Conta).where(Conta.id == id_conta_saida)
         conta_saida = session.exec(statement).first()
         if conta_saida.valor < valor:
             raise ValueError ("Saldo insuficiente!")
         statement = select(Conta).where(Conta.id == id_conta_entrada)
         conta_entrada = session.exec(statement).first()

         conta_saida.valor -= valor
         conta_entrada.valor += valor
         session.commit()

def movimentar_dinheiro(historico: Historico): 
     with Session(engine) as session:
         statement = select(Conta).where(Conta.id==historico.conta_id)
         conta = session.exec(statement).first()
         #TODO: Validar se a conta está ativa
         if conta.status ==Status.INATIVO:
             raise ValueError("Conta inativa, não é possível realizar movimentações")

         if historico.tipo == Tipos.ENTRADA:
             conta.valor += historico.valor
         else:
             if conta.valor < historico.valor:
                 raise ValueError("Saldo insuficiente")
         conta.valor -= historico.valor

     session.add(historico)
     session.commit()
     return historico

def total_contas():
     with Session(engine) as session:
         statement = select(Conta)
         contas = session.exec(statement).all()
     total = 0
     for conta in contas:
         total += conta.valor

     return float(total)

def buscar_historicos_entre_datas(data_inicio: date, data_fim: date):
     with Session(engine) as session:
         statement = select(Historico).where(
             Historico.data >= data_inicio,
             Historico.data <= data_fim
         )
         resultados = session.exec(statement).all()
         return resultados

def criar_grafico_por_conta():
     with Session(engine) as session:
         statement = select(Conta).where(Conta.status == Status.ATIVO)
         contas = session.exec(statement).all()
         bancos = []
         total = []
         for i in contas:
             bancos.append(i.value)
         for i in contas:
             total.append(i.banco.value)
         # ou bancos = [i.banco.value for i in contas]
         # ou total = [i.value for i in contas]
         #print(total)
         #print(bancos)
         import matplotlib as plt
         plt.bar(bancos, total)
         plt.show()



conta = Conta(valor=10, banco=Bancos.NUBANK)
criar_conta(conta)
#historico = Historico(conta_id = 1, tipo = Tipos.ENTRADA, valor = 10, data = date.today())
#movimentar_dinheiro(historico)
#x = buscar_historicos_entre_datas(date.today() - timedelta(days = 1), date.today() + timedelta(days = 1))
#print(x)

#desativar_conta(1)
#transferir_saldo(2, 3, 1)
#print(total_contas())


