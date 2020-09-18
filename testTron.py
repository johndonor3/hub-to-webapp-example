import asyncio
from clu.legacy import TronConnection

def reportln2Alarm(val):
    print(type(val))
    print(f'ln2Alarm reported {val}')

def reportGeneral(*args):
	print("living dangerously: ", args)

async def main():
    tron = TronConnection(host='localhost', port=6093, models=['apogee'])
    tron.models['apogee']['ln2Alarm'].register_callback(reportln2Alarm)
    await tron.start()
    await tron.run_forever()

asyncio.run(main())
