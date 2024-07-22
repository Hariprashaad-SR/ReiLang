import basic

while True:
    temp = input('basic > ')
    if temp == 'exit':
        break
    if temp == 'hari':
        print(f'reilang🤖 > Woooooh man!!! you found an easter egg')
        continue
    tokens, error = basic.run(temp, '<stdin>')
    if error:
        print(error.tostring())
    else:
        print(f'reilang🤖 > {tokens}')