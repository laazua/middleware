import pyinfra

from tasks import setup
from tasks import kafka


# print(pyinfra.host.data.dict())


#运行任务(命令行传入--data action=setup 或 kafka)
if pyinfra.host.data.get('action') == 'setup':
    setup.run()

if pyinfra.host.data.get('action') == 'kafka':
    kafka.run()

if pyinfra.host.data.get('action') is None:
    print("No action specified. Run 'setup' and 'kafka' task.")
    setup.run()
    kafka.run()
