from flask import Flask, request, jsonify
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# 🔐 Substitua pelo seu token e ID da lista do ClickUp
CLICKUP_TOKEN = "HNE7Q5C447KHS44JQ2APVUPZOHEK6J4P53MWLAGN6KSV20S8TTND74LO6TECSRB4"
CLICKUP_LIST_ID = "90134635156"

def calcular_dias_uteis(data_inicio, dias_uteis):
    data = data_inicio
    while dias_uteis > 0:
        data += timedelta(days=1)
        if data.weekday() < 5:
            dias_uteis -= 1
    return data

@app.route("/webhook", methods=["POST"])
def receber_webhook():
    pedido = request.json
    try:
        nome_cliente = pedido["customer"]["name"]
        produto = pedido["products"][0]["name"]
        quantidade = pedido["products"][0]["quantity"]
        personalizacao = pedido.get("note", "Não informado")
        link_pedido = pedido.get("admin_url", "Não disponível")

        hoje = datetime.today()
        prazo_saida = calcular_dias_uteis(hoje, 20).strftime("%Y-%m-%d")

        payload = {
            "name": f"Pedido - {produto}",
            "description": f"👤 Cliente: {nome_cliente}\n📦 Produto: {produto}\n✏️ Personalização: {personalizacao}\n🔢 Quantidade: {quantidade}\n🔗 Link: {link_pedido}",
            "status": "Pedido Recebido",
            "due_date": int(datetime.strptime(prazo_saida, "%Y-%m-%d").timestamp()) * 1000,
            "checklists": [
                {
                    "name": "Etapas de Produção",
                    "items": [
                        "✏️ Personalização enviada",
                        "🛠️ Em produção",
                        "📦 Em embalagem",
                        "📬 Enviado",
                        "🧾 Finalizado"
                    ]
                }
            ]
        }

        headers = {
            "Authorization": CLICKUP_TOKEN,
            "Content-Type": "application/json"
        }

        response = requests.post(
            f"https://api.clickup.com/api/v2/list/{CLICKUP_LIST_ID}/task",
            headers=headers,
            json=payload
        )

        if response.status_code in [200, 201]:
            return jsonify({"message": "Tarefa criada com sucesso!"}), 200
        else:
            return jsonify({"error": response.text}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
