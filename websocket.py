from quart import Quart, render_template, websocket
from functools import wraps
from clu.legacy.tron import TronConnection


app = Quart(__name__)

connected = set()

def collect_websocket(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        global connected
        connected.add(websocket._get_current_object())
        try:
            return await func(*args, **kwargs)
        finally:
            connected.remove(websocket._get_current_object())
    return wrapper 


@app.route('/')
async def index():
    return await render_template('index.html')


@app.websocket('/ws')
@collect_websocket
async def ws():
    async def broadcast(key):
        name = key.name
        value = key.value
        
        for c in connected:
            await c.send(f"{name}: {value}")
    tron = TronConnection('localhost', 6093, models=['apogee', 'alerts'])
    await tron.start()

    tron.models['apogee']['ln2alarm'].register_callback(broadcast)
    tron.models['alerts']['activeAlerts'].register_callback(broadcast)

    while True:
        data = await websocket.receive()
        for c in connected:
            for k, m in tron.models.items():
                print("model check", k, m.jsonify())
            await c.send(f"echo {data}")

    await tron.run_forever()


if __name__ == '__main__':
    app.run(port=5000)
